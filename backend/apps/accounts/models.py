from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import CafeProfile, Branch


class AccountConfiguration(models.Model):
    """تنظیمات شیوه مدیریت حساب‌های کاربری مجموعه."""

    class OperatingMode(models.TextChoices):
        SINGLE = "SINGLE", "تک‌کاربره"
        MULTI = "MULTI", "چندکاربره"

    cafe = models.OneToOneField(
        CafeProfile,
        on_delete=models.CASCADE,
        related_name="account_configuration",
        verbose_name="مجموعه کافه",
    )
    operating_mode = models.CharField(
        max_length=10,
        choices=OperatingMode.choices,
        default=OperatingMode.SINGLE,
        verbose_name="شیوه استفاده",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_cafe_account_configurations",
        verbose_name="مالک حساب",
    )
    setup_completed = models.BooleanField(
        default=False,
        verbose_name="راه‌اندازی اولیه تکمیل شده",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "تنظیمات حساب‌های کاربری"
        verbose_name_plural = "تنظیمات حساب‌های کاربری"

    def __str__(self):
        return f"{self.cafe} - {self.get_operating_mode_display()}"


class UserProfile(models.Model):
    """اطلاعات تکمیلی حساب کاربری؛ احراز هویت همچنان با User خود Django است."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="حساب کاربری",
    )
    display_name = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="نام نمایشی",
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name="شماره تماس")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"

    def __str__(self):
        return self.display_name or self.user.get_username()


class Role(models.Model):
    """نقش قابل تعریف برای کارکنان هر مجموعه."""

    cafe = models.ForeignKey(
        CafeProfile,
        on_delete=models.CASCADE,
        related_name="roles",
        verbose_name="مجموعه کافه",
    )
    name = models.CharField(max_length=100, verbose_name="عنوان نقش")
    code = models.SlugField(max_length=50, verbose_name="کد نقش")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    permissions = models.ManyToManyField(
        "auth.Permission",
        blank=True,
        related_name="cafe_roles",
        verbose_name="دسترسی‌ها",
    )
    is_system = models.BooleanField(
        default=False,
        editable=False,
        verbose_name="نقش سیستمی",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "نقش کاربری"
        verbose_name_plural = "نقش‌های کاربری"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["cafe", "code"],
                name="unique_role_code_per_cafe",
            ),
        ]

    def __str__(self):
        return f"{self.name} - {self.cafe}"


class BranchMembership(models.Model):
    """اتصال کاربر به یک شعبه و نقش او در همان شعبه."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="branch_memberships",
        verbose_name="کاربر",
    )
    branch = models.ForeignKey(
        Branch,
        on_delete=models.PROTECT,
        related_name="memberships",
        verbose_name="شعبه",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="memberships",
        verbose_name="نقش",
    )
    is_active = models.BooleanField(default=True, verbose_name="عضویت فعال")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ عضویت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "عضویت کاربر در شعبه"
        verbose_name_plural = "عضویت کاربران در شعبه‌ها"
        ordering = ["branch__code", "user__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "branch"],
                name="unique_user_membership_per_branch",
            ),
        ]
        indexes = [
            models.Index(fields=["branch", "is_active"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def clean(self):
        super().clean()
        if self.branch_id and self.role_id:
            branch_cafe_id = self.branch.cafe_id
            role_cafe_id = self.role.cafe_id
            if branch_cafe_id != role_cafe_id:
                raise ValidationError({
                    "role": "نقش انتخاب‌شده متعلق به مجموعه این شعبه نیست."
                })

    def __str__(self):
        return f"{self.user} - {self.branch} - {self.role}"
