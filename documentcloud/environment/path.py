"""
Helper functions to standardize the paths where files associated with a document are
stored
"""

# Third Party
import environ

env = environ.Env()
DOCUMENT_BUCKET = env.str("DOCUMENT_BUCKET")

DOCUMENT_SUFFIX = "pdf"
INDEX_SUFFIX = "index"
PAGESIZE_SUFFIX = "pagesize"
IMAGE_SUFFIX = "gif"
TEXT_SUFFIX = "txt"


def path(doc_id):
    """The path where this document's files are located"""
    return f"{DOCUMENT_BUCKET}/documents/{doc_id}/"


def file_path(doc_id, slug, ext):
    """The path to one of the files associated with this document"""
    return path(doc_id) + f"{slug}.{ext}"


def doc_path(doc_id, slug):
    """The path to the document file"""
    return file_path(doc_id, slug, DOCUMENT_SUFFIX)


def index_path(doc_id, slug):
    """The path to the index file"""
    return file_path(doc_id, slug, INDEX_SUFFIX)


def pagesize_path(doc_id, slug):
    """The path to the pagesize file"""
    return file_path(doc_id, slug, PAGESIZE_SUFFIX)


def text_path(doc_id, slug):
    """The path to the text file"""
    return file_path(doc_id, slug, TEXT_SUFFIX)


def pages_path(doc_id):
    """The path to the pages directory for this document"""
    return path(doc_id) + "pages/"


def page_image_path(doc_id, slug, page_number, page_size):
    """The path to the image file for a single page"""
    return pages_path(doc_id) + f"{slug}-p{page_number + 1}-{page_size}.{IMAGE_SUFFIX}"


def page_text_path(doc_id, slug, page_number):
    """The path to the text file for a single page"""
    return pages_path(doc_id) + f"{slug}-p{page_number + 1}.{TEXT_SUFFIX}"