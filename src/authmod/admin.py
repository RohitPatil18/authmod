from django.contrib import admin

from authmod import models


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "is_default",
    )
    list_display_links = ("id", "name")
    list_filter = ("is_default",)
