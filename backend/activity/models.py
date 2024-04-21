from django.db import models


class Activity(models.Model):
    activity_name = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    frequency = models.CharField(max_length=50)
    start_date = models.DateField()

    class Meta:
        verbose_name_plural = "activities"

    def __str__(self):
        return self.activity_name



