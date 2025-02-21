from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class MMUser(AbstractUser):
    mattermost_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    mattermost_access_token = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username