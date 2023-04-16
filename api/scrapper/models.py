from django.db import models
from django.core.exceptions import ValidationError


class Episode(models.Model):
    number = models.IntegerField()
    name = models.CharField(max_length=150)
    season_number = models.IntegerField()
    release_date = models.DateTimeField()
    url = models.URLField(max_length=200)
    summary = models.TextField()

    class Meta:
        unique_together = ("season_number", "number")
