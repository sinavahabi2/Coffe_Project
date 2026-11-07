from django.db.models import Q

from apps.core.models import Branch

from .models import AccountConfiguration, BranchMembership


def user_has_branch_permission(user, branch, permission_codename, app_label=None):
    """
    بررسی دسترسی کاربر در یک شعبه.

    مالک مجموعه و superuser دسترسی کامل دارند.
    در حالت تک‌کاربره فقط مالک مجاز است.
    در حالت چندکاربره دسترسی از نقش عضویت همان شعبه خوانده می‌شود.
    """
    if not user or not user.is_authenticated or not branch:
        return False

    if user.is_superuser:
        return True

    configuration = (
        AccountConfiguration.objects
        .filter(cafe_id=branch.cafe_id)
        .first()
    )
    if configuration is None:
        return False

    if configuration.owner_id == user.pk:
        return True

    if configuration.operating_mode == AccountConfiguration.OperatingMode.SINGLE:
        return False

    membership = (
        BranchMembership.objects
        .filter(user=user, branch=branch, is_active=True, role__is_active=True)
        .select_related("role")
        .first()
    )
    if membership is None:
        return False

    permissions = membership.role.permissions.all()
    if app_label:
        return permissions.filter(
            content_type__app_label=app_label,
            codename=permission_codename,
        ).exists()

    return permissions.filter(codename=permission_codename).exists()


def get_user_active_branches(user):
    """برگرداندن QuerySet شعب فعال قابل دسترس برای کاربر."""
    if not user or not user.is_authenticated:
        return Branch.objects.none()

    if user.is_superuser:
        return Branch.objects.filter(is_active=True)

    owned_cafe_ids = AccountConfiguration.objects.filter(
        owner_id=user.pk
    ).values_list("cafe_id", flat=True)

    member_branch_ids = BranchMembership.objects.filter(
        user=user,
        is_active=True,
        role__is_active=True,
        branch__is_active=True,
    ).values_list("branch_id", flat=True)

    return (
        Branch.objects
        .filter(is_active=True)
        .filter(Q(cafe_id__in=owned_cafe_ids) | Q(pk__in=member_branch_ids))
        .distinct()
        .order_by("code")
    )
