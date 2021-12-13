from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()


class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    username = None
    first_name = None
    last_name = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    objects = UserManager()


class RequestHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    request_id = models.CharField(max_length=50, unique=True)
    create_date = models.DateTimeField(auto_now_add=True)
    count_data = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return self.request_id

    @staticmethod
    def create_request_history(user, request_id, count_data=None, status=None):
        return RequestHistory.objects.create(user=user, request_id=request_id, count_data=count_data, status=status)


class AccessLevel(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, unique=True)
    max_number_of_data = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.email

    def update_max_number_of_data(self, used_data: int):
        if self.max_number_of_data:
            temp = self.max_number_of_data - used_data
            self.max_number_of_data = 0 if temp < 1 else temp
            self.save()
