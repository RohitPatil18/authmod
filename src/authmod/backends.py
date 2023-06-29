from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.db.models import Exists, OuterRef, Q

UserModel = get_user_model()


class RoleBasedModelBackend(ModelBackend):
    def _get_user_permissions(self, user_obj):
        return user_obj.user_permissions.all()

    def _get_role_permissions(self, user_obj):
        user_groups_field = get_user_model()._meta.get_field("role")
        user_groups_query = "role__%s" % user_groups_field.related_query_name()
        return Permission.objects.filter(**{user_groups_query: user_obj})

    def get_role_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from the
        role they are assigned.
        """
        return self._get_permissions(user_obj, obj, "role")

    def get_all_permissions(self, user_obj, obj=None):
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_role_permissions(user_obj, obj=obj),
        }

    def with_perm(self, perm, is_active=True, include_superusers=True, obj=None):
        """
        Return users that have permission "perm". By default, filter out
        inactive users and include superusers.
        """
        if isinstance(perm, str):
            try:
                app_label, codename = perm.split(".")
            except ValueError:
                raise ValueError(
                    "Permission name should be in the form "
                    "app_label.permission_codename."
                )
        elif not isinstance(perm, Permission):
            raise TypeError(
                "The `perm` argument must be a string or a permission instance."
            )

        if obj is not None:
            return UserModel._default_manager.none()

        permission_q = Q(role__user=OuterRef("pk")) | Q(user=OuterRef("pk"))
        if isinstance(perm, Permission):
            permission_q &= Q(pk=perm.pk)
        else:
            permission_q &= Q(codename=codename, content_type__app_label=app_label)

        user_q = Exists(Permission.objects.filter(permission_q))
        if include_superusers:
            user_q |= Q(is_superuser=True)
        if is_active is not None:
            user_q &= Q(is_active=is_active)

        return UserModel._default_manager.filter(user_q)
