from django.contrib import admin

from .models import (
    AccountConfiguration,
    BranchMembership,
    Role,
    UserProfile,
)


@admin.register(AccountConfiguration)
class AccountConfigurationAdmin(admin.ModelAdmin):
    list_display = ("cafe", "operating_mode", "owner", "setup_completed")
    list_filter = ("operating_mode", "setup_completed")
    search_fields = ("cafe__name", "owner__username", "owner__email")
    autocomplete_fields = ("cafe", "owner")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "phone", "updated_at")
    search_fields = ("display_name", "user__username", "user__first_name",
                     "user__last_name", "phone")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "cafe", "is_active")
    list_filter = ("is_active", "cafe")
    search_fields = ("name", "code", "cafe__name")
    autocomplete_fields = ("cafe",)
    filter_horizontal = ("permissions",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(BranchMembership)
class BranchMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "branch", "role", "is_active", "created_at")
    list_filter = ("is_active", "branch", "role")
    search_fields = ("user__username", "user__first_name", "user__last_name",
                     "branch__name", "role__name")
    autocomplete_fields = ("user", "branch", "role")
    readonly_fields = ("created_at", "updated_at")
