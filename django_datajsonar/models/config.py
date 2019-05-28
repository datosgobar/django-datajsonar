from django.db import models
from solo.models import SingletonModel


class IndexingConfig(SingletonModel):

    verify_ssl = models.BooleanField(default=False)
