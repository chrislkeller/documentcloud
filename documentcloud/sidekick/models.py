# Django
from django.db import models
from django.utils.translation import ugettext_lazy as _

# Third Party
import numpy as np

# DocumentCloud
from documentcloud.common import path
from documentcloud.common.environment import storage
from documentcloud.sidekick.choices import Status

VOCAB_SIZE = 30_000


def file_path(instance, file_name):
    return f"sidekick/{instance.pk}/{file_name}"


class Sidekick(models.Model):
    """Online learning for documents in a project"""

    project = models.OneToOneField(
        verbose_name=_("project"),
        to="projects.Project",
        on_delete=models.CASCADE,
        related_name="sidekick",
        help_text=_("The project this sidekick is for"),
    )
    status = models.IntegerField(
        _("status"),
        choices=Status.choices,
        default=Status.uninitialized,
        help_text=_("The status of this sidekick"),
    )
    tag_name = models.CharField(
        _("tag name"),
        max_length=50,
        help_text=_(
            "The name of the tag to use to associate a document as a positive or "
            "negative match for this sidekick"
        ),
    )

    def preprocess(self):
        """Preprocess the documents in the project for online learning"""

    def learn(self):
        """Update the document estimates based on the document tags"""
        # XXX potentially move to celery task

    def get_document_vectors(self):
        """Fetch the pre-preocessed document vectors from storage"""
        # XXX error handle missing file
        with storage.open(
            path.sidekick_document_vectors_path(self.project_id), "rb"
        ) as vectors_file:
            doc_vector_obj = np.load(vectors_file)

        # Grab document vector matrix
        # XXX how does this work?
        return doc_vector_obj.get(doc_vector_obj.files[0])