# Standard Library
import base64
import json

# Third Party
import environ

env = environ.Env()

ERROR_IF_NO_TOPIC = True


def encode_pubsub_data(data):
    return json.dumps(data).encode("utf8")


def encode_published_pubsub_data(data):
    return {"data": base64.b64encode(data).decode("utf-8")}


def decode_pubsub_data(data):
    return json.loads(base64.b64decode(data["data"]).decode("utf-8"))


class LocalPubSubClient:
    def __init__(self):
        self.tasks = {}

    @staticmethod
    def topic_path(namespace, name):
        return (namespace, name)

    def register_internal_callback(self, topic_path, callback_fn):
        self.tasks[topic_path] = callback_fn

    def publish(self, topic_path, data):
        if topic_path in self.tasks:
            self.tasks[topic_path](encode_published_pubsub_data(data))
        else:
            if ERROR_IF_NO_TOPIC:
                raise ValueError(f"Topic not registered: {topic_path}")


# Define pub sub client and topic subscriptions
publisher = LocalPubSubClient()


def process_pdf_task(data):
    from documentcloud.documents.tasks import process_file_internal

    return process_file_internal.delay(data)


def extract_image_task(data):
    from documentcloud.documents.tasks import extract_images

    return extract_images(data)


def ocr_page_task(data):
    from documentcloud.documents.tasks import ocr_pages

    return ocr_pages.delay(data)


publisher.register_internal_callback(
    ("documentcloud", env.str("PDF_PROCESS_TOPIC", default="pdf-process")),
    process_pdf_task,
)
publisher.register_internal_callback(
    ("documentcloud", env.str("IMAGE_EXTRACT_TOPIC", default="image-extraction")),
    extract_image_task,
)
publisher.register_internal_callback(
    ("documentcloud", env.str("OCR_TOPIC", default="ocr-extraction")), ocr_page_task
)