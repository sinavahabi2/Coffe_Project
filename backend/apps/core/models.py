from django.db import models
from django.db.models import Q
from django.conf import settings


class CafeProfile(models.Model):
    """اطلاعات اصلی مجموعه کافه"""

    name = models.CharField(
        max_length=150,
        verbose_name="نام کافه"
    )

    legal_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="نام حقوقی"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="ایمیل"
    )

    address = models.TextField(
        blank=True,
        verbose_name="آدرس"
    )

    currency = models.CharField(
        max_length=3,
        default="IRR",
        verbose_name="واحد پول"
    )

    timezone = models.CharField(
        max_length=50,
        default="Asia/Tehran",
        verbose_name="منطقه زمانی"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین ویرایش"
    )

    class Meta:
        verbose_name = "مشخصات کافه"
        verbose_name_plural = "مشخصات کافه"

    def __str__(self):
        return self.name


class Branch(models.Model):
    """مدیریت شعب کافه"""

    cafe = models.ForeignKey(
        CafeProfile,
        on_delete=models.PROTECT,
        related_name="branches",
        verbose_name="مجموعه کافه"
    )

    code = models.CharField(
        max_length=20,
        verbose_name="کد شعبه"
    )

    name = models.CharField(
        max_length=150,
        verbose_name="نام شعبه"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس"
    )

    address = models.TextField(
        blank=True,
        verbose_name="آدرس شعبه"
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name="شعبه اصلی"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین ویرایش"
    )

    class Meta:
        verbose_name = "شعبه"
        verbose_name_plural = "شعبه‌ها"
        ordering = ["code"]

        constraints = [
            models.UniqueConstraint(
                fields=["cafe", "code"],
                name="unique_branch_code_per_cafe"
            ),
            models.UniqueConstraint(
                fields=["cafe"],
                condition=Q(is_main=True),
                name="unique_main_branch_per_cafe"
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"




class AuditLog(models.Model):
    """ثبت سوابق عملیات کاربران سیستم"""

    class ActionType(models.TextChoices):
        CREATE = "CREATE", "ایجاد"
        UPDATE = "UPDATE", "ویرایش"
        DELETE = "DELETE", "حذف"
        LOGIN = "LOGIN", "ورود"
        LOGOUT = "LOGOUT", "خروج"
        OTHER = "OTHER", "سایر"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="کاربر"
    )

    action = models.CharField(
        max_length=10,
        choices=ActionType.choices,
        verbose_name="نوع عملیات"
    )

    model_name = models.CharField(
        max_length=100,
        verbose_name="نام مدل"
    )

    object_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="شناسه رکورد"
    )

    object_repr = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="عنوان رکورد"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="آدرس IP"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان عملیات"
    )

    class Meta:
        verbose_name = "سابقه عملیات"
        verbose_name_plural = "سوابق عملیات"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["model_name", "object_id"]),
            models.Index(fields=["action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.model_name}"
