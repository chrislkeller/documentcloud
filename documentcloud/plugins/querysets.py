# Django
from django.db import models


class PluginQuerySet(models.QuerySet):
    def get_viewable(self, user):
        if user.is_staff:
            return self.all()
        else:
            return self.none()