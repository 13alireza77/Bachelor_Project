from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class RequestHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request_id = models.CharField(max_length=50)
    create_date = models.DateTimeField(auto_now_add=True)
    count_data = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)


class AccessLevel(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    max_number_of_data = models.IntegerField(blank=True, null=True)
