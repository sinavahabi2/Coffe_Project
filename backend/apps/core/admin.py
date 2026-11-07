
from django.contrib import admin
from .models import CafeProfile, Branch, AuditLog

@admin.register(CafeProfile)
class CafeProfileAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "currency",
        "is_active",
    )

    list_filter = ("is_active",)
    search_fields = ("name", "legal_name", "phone")


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "cafe",
        "is_main",
        "is_active",
    )

    list_filter = ("is_active", "is_main", "cafe")
    search_fields = ("name", "code", "address")



@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "action",
        "model_name",
        "object_id",
        "user",
        "created_at",
    )

    list_filter = (
        "action",
        "model_name",
        "created_at",
    )

    search_fields = (
        "model_name",
        "object_id",
        "object_repr",
        "description",
        "user__username",
    )

    readonly_fields = (
        "user",
        "action",
        "model_name",
        "object_id",
        "object_repr",
        "description",
        "ip_address",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
