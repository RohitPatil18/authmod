from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from users import models


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = models.User
        fields = (
            "first_name",
            "last_name",
            "email_address",
            "user_permissions",
            "role",
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = models.User
        fields = (
            "first_name",
            "last_name",
            "email_address",
            "user_permissions",
            "role",
        )


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ("first_name", "last_name", "email_address", "role")
    list_filter = ("role",)
    fieldsets = (
        (None, {"fields": ("email_address", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Additional", {"fields": ("role",)}),
    )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {"fields": ("email_address", "password1", "password2")}),
        ("Personal info", {"fields": ("first_name", "last_name")}),
        ("Additional", {"fields": ("role",)}),
    )
    search_fields = ("email_address", "first_name", "last_name")
    ordering = ("-id",)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(models.User, UserAdmin)

admin.site.unregister(Group)
