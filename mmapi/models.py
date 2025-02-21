from django.db import models

# Create your models here.


# class tokenkey(models.Model):
#     token = models.CharField(max_length=255)

# from django.contrib.auth.models import AbstractUser
# from django.db import models

# class MMUser(AbstractUser):
#     mattermost_user_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
#     mattermost_access_token = models.TextField(null=True, blank=True)

#     def __str__(self):
#         return self.username


# class MattermostProfile(models.Model):
#     user = models.OneToOneField(MMUser, on_delete=models.CASCADE, related_name="mattermost_profile")
#     mattermost_user_id = models.CharField(max_length=255, unique=True)
#     mattermost_access_token = models.TextField()

#     def __str__(self):
#         return f"Mattermost Profile for {self.user.username}"
