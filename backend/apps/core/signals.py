
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

from .models import AuditLog
from .middleware import get_current_user, get_current_ip

TRACKED_APPS = {
    "core",
    "accounts",
    "catalog",
    "sales",
    "inventory",
    "purchasing",
    "finance",
    "customers",
    "staff",
    "floor",
    "reports",
}


def should_track(sender):
    return (
        sender._meta.app_label in TRACKED_APPS
        and sender is not AuditLog
        and not sender._meta.proxy
    )


@receiver(pre_save)
def capture_old_values(sender, instance, **kwargs):
    if not should_track(sender):
        return

    if not instance.pk:
        instance._audit_old_values = None
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        instance._audit_old_values = None
        return

    instance._audit_old_values = {
        field.name: getattr(old_instance, field.attname)
        for field in sender._meta.concrete_fields
        if not field.primary_key
    }


@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    if not should_track(sender):
        return

    old_values = getattr(instance, "_audit_old_values", None)

    if created:
        action = AuditLog.ActionType.CREATE
        description = "رکورد جدید ایجاد شد."
    else:
        action = AuditLog.ActionType.UPDATE

        if old_values is None:
            return

        changed_fields = []

        for field in sender._meta.concrete_fields:
            if field.primary_key:
                continue

            old_value = old_values.get(field.name)
            new_value = getattr(instance, field.attname)

            if old_value != new_value:
                changed_fields.append(field.verbose_name or field.name)

        if not changed_fields:
            return

        description = (
            "فیلدهای تغییرکرده: "
            + "، ".join(map(str, changed_fields))
        )

    AuditLog.objects.create(
        user=get_current_user(),
        ip_address=get_current_ip(),
        action=action,
        model_name=sender._meta.label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        description=description,
    )


@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if not should_track(sender):
        return

    AuditLog.objects.create(
        user=get_current_user(),
        ip_address=get_current_ip(),
        action=AuditLog.ActionType.DELETE,
        model_name=sender._meta.label,
        object_id=str(instance.pk),
        object_repr=str(instance)[:255],
        description="رکورد حذف شد.",
    )
