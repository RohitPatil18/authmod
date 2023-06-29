from django.contrib import auth
from django.contrib.auth.models import Permission
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.utils.itercompat import is_iterable
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
    )
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_role"

    def __str__(self):
        return self.name

    @transaction.atomic
    def save(self, *args, **kwargs):
        """
        This method checks if there is any default role available, if not
        id sets current record as default.
        Else, if current record is set to default and there is already other
        record which is set as default, we will turn is_default flag for all
        other records as False.
        """
        qs = Role.objects.filter(is_default=True)

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        default_exists = qs.exists()
        if not default_exists:
            self.is_default = True
        elif self.is_default and default_exists:
            Role.objects.exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_permissions(user, obj, from_name):
    permissions = set()
    name = "get_%s_permissions" % from_name
    for backend in auth.get_backends():
        if hasattr(backend, name):
            permissions.update(getattr(backend, name)(user, obj))
    return permissions


def _user_has_perm(user, perm, obj):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, "has_perm"):
            continue
        try:
            if backend.has_perm(user, perm, obj):
                return True
        except PermissionDenied:
            return False
    return False


def _user_has_module_perms(user, app_label):
    """
    A backend can raise `PermissionDenied` to short-circuit permission checking.
    """
    for backend in auth.get_backends():
        if not hasattr(backend, "has_module_perms"):
            continue
        try:
            if backend.has_module_perms(user, app_label):
                return True
        except PermissionDenied:
            return False
    return False


class PermissionsMixin(models.Model):
    """
    Add the fields and methods necessary to support the Group and Permission
    models using the ModelBackend.
    """

    is_superuser = models.BooleanField(
        _("superuser status"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_set",
        related_query_name="user",
    )

    class Meta:
        abstract = True

    def get_user_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has directly.
        Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, "user")

    def get_all_permissions(self, obj=None):
        return _user_get_permissions(self, obj, "all")

    def has_perm(self, perm, obj=None):
        """
        Return True if the user has the specified permission. Query all
        available auth backends, but return immediately if any backend returns
        True. Thus, a user who has permission from a single auth backend is
        assumed to have permission in general. If an object is provided, check
        permissions for that object.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True

        return _user_has_perm(self, perm, obj)

    def has_perms(self, perm_list, obj=None):
        """
        Return True if the user has each of the specified permissions. If
        object is passed, check if the user has all required perms for it.
        """
        if not is_iterable(perm_list) or isinstance(perm_list, str):
            raise ValueError("perm_list must be an iterable of permissions.")
        return all(self.has_perm(perm, obj) for perm in perm_list)

    def has_module_perms(self, app_label):
        """
        Return True if the user has any permissions in the given app label.
        Use similar logic as has_perm(), above.
        """
        # Active superusers have all permissions.
        if self.is_active and self.is_superuser:
            return True
        return _user_has_module_perms(self, app_label)


def _get_default_role():
    try:
        role = Role.objects.filter(is_default=True).get()
    except Role.DoesNotExist:
        raise "DefaultRoleNotFound"
    return role


class RolePermissionsMixin(PermissionsMixin):
    role = models.ForeignKey(
        Role,
        verbose_name=_("roles"),
        blank=True,
        help_text=_(
            "The role that user has. A user will get all permissions "
            "granted to their role"
        ),
        on_delete=models.PROTECT,
        null=True,
    )

    class Meta:
        abstract = True

    def get_role_permissions(self, obj=None):
        """
        Return a list of permission strings that this user has through their
        role. Query all available auth backends. If an object is passed in,
        return only permissions matching this object.
        """
        return _user_get_permissions(self, obj, "role")

    def save(self, *args, **kwargs):
        if not self.role and not self.is_superuser:
            self.role = _get_default_role()
        super().save(*args, **kwargs)
