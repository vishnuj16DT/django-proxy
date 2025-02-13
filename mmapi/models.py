from django.db import models

# Create your models here.


class tokenkey(models.Model):
    token = models.CharField(max_length=255)