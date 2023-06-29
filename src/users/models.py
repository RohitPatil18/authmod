from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from authmod.models import RolePermissionsMixin
from users.managers import UserManager


class User(AbstractBaseUser, RolePermissionsMixin):
    """
    Custom database model for entity `User` which extends
    Django's inbuilt `AbstractBaseUser`
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email_address = models.EmailField(
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    _is_staff = models.BooleanField(
        _("staff status"),
        db_column="is_staff",
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    objects = UserManager()

    USERNAME_FIELD = "email_address"

    class Meta:
        db_table = "user"
        default_permissions = ()

    @property
    def is_staff(self):
        return self.is_superuser or self._is_staff

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
