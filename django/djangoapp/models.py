from django.conf import settings
from django.conf import settings
from django.db import models

# Create your models here.


class UserTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             null=True, on_delete=models.CASCADE)
    user_token = models.CharField(max_length=64)
    file = models.FileField(upload_to='files/', null=True)
    content_type = models.CharField(max_length=254, blank=True, default='')
    file_name = models.CharField(max_length=254, blank=True, default='')
    file_size = models.PositiveBigIntegerField(blank=True, default=0)
    file_width = models.PositiveSmallIntegerField(blank=True, default=0)
    file_height = models.PositiveSmallIntegerField(blank=True, default=0)
    file_fps = models.PositiveSmallIntegerField(blank=True, default=0)
    file_numframes = models.PositiveBigIntegerField(blank=True, default=0)
    date = models.DateTimeField(auto_now=True)
