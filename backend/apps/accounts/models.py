
from django.db import models
from django.conf import settings


class UserProfile(models.Model):
    """اطلاعات تکمیلی حساب کاربری"""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="حساب کاربری"
    )

    display_name = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="نام نمایشی"
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="شماره تماس"
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
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل کاربران"

    def __str__(self):
        return self.display_name or self.user.username
