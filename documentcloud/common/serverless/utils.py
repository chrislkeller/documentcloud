"""
Helper functions to perform common serverless operations.
"""

# Standard Library
import logging
from urllib.parse import urljoin

# Third Party
import environ
import furl
import redis as _redis
import requests

# Local
from .. import redis_fields

env = environ.Env()

# Common environment variables
API_CALLBACK = env.str("API_CALLBACK")
PROCESSING_TOKEN = env.str("PROCESSING_TOKEN")
REDIS_URL = furl.furl(env.str("REDIS_PROCESSING_URL"))
REDIS_PASSWORD = env.str("REDIS_PROCESSING_PASSWORD")


def get_redis():
    """Opens a connection to Redis and returns it"""
    return _redis.Redis(
        host=REDIS_URL.host, port=REDIS_URL.port, password=REDIS_PASSWORD, db=0
    )


def send_update(redis, doc_id, json):
    """Sends an update to the API server specified as JSON"""
    if not still_processing(redis, doc_id):
        return

    requests.patch(
        urljoin(API_CALLBACK, f"documents/{doc_id}/"),
        json=json,
        headers={"Authorization": f"processing-token {PROCESSING_TOKEN}"},
    )


def send_complete(redis, doc_id):
    """Sends an update to the API server that processing is complete"""
    if not still_processing(redis, doc_id):
        return

    send_update(redis, doc_id, {"status": "success"})
    # Clean out redis
    clean_up(redis, doc_id)


def send_error(redis, doc_id, message, fatal=False):
    """Sends an error to the API server specified as a string message"""
    if not still_processing(redis, doc_id):
        return

    # Send the error to the server
    requests.post(
        urljoin(API_CALLBACK, f"documents/{doc_id}/errors/"),
        json={"message": message},
        headers={"Authorization": f"processing-token {PROCESSING_TOKEN}"},
    )

    # Log the error depending on its severity
    if fatal:
        logging.error(message)
    else:
        logging.warning(message)

    clean_up(redis, doc_id)


def initialize(redis, doc_id):
    """Sets up Redis for processing"""
    redis.set(redis_fields.is_running(doc_id), 1)


def still_processing(redis, doc_id):
    """Returns whether the doc_id is still processing"""
    return redis.get(redis_fields.is_running(doc_id)) == b"1"


def clean_up(redis, doc_id):
    """Removes all keys associated with a document id in redis"""

    dimensions_field = redis_fields.dimensions(doc_id)

    def remove_all(pipeline):
        # Remove all simple fields
        pipeline.delete(
            redis_fields.images_remaining(doc_id),
            redis_fields.texts_remaining(doc_id),
            redis_fields.page_count(doc_id),
            redis_fields.is_running(doc_id),
            redis_fields.image_bits(doc_id),
            redis_fields.text_bits(doc_id),
        )

        # Remove any existing dimensions that may be lingering
        existing_dimensions = pipeline.smembers(dimensions_field)
        if existing_dimensions is not None:
            for dimension in existing_dimensions:
                pipeline.delete(redis_fields.page_dimension(doc_id, dimension))
        pipeline.delete(dimensions_field)

    redis.transaction(remove_all, dimensions_field)