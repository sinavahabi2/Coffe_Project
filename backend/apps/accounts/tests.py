from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.core.models import Branch, CafeProfile

from .models import AccountConfiguration, BranchMembership, Role
from .services import get_user_active_branches, user_has_branch_permission


User = get_user_model()


class AccountPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="cafe_owner",
            password="test-password-123",
        )
        self.employee = User.objects.create_user(
            username="barista",
            password="test-password-123",
        )
        self.cafe = CafeProfile.objects.create(name="کافه آزمایشی")
        self.branch = Branch.objects.create(
            cafe=self.cafe,
            code="MAIN",
            name="شعبه اصلی",
            is_main=True,
        )
        self.configuration = AccountConfiguration.objects.create(
            cafe=self.cafe,
            owner=self.owner,
            operating_mode=AccountConfiguration.OperatingMode.SINGLE,
        )
        self.role = Role.objects.create(
            cafe=self.cafe,
            name="باریستا",
            code="barista",
        )

    def test_owner_has_access_in_single_user_mode(self):
        self.assertTrue(
            user_has_branch_permission(
                self.owner, self.branch, "view_branch", "core"
            )
        )

    def test_other_user_has_no_access_in_single_user_mode(self):
        self.assertFalse(
            user_has_branch_permission(
                self.employee, self.branch, "view_branch", "core"
            )
        )

    def test_role_permission_grants_access_in_multi_user_mode(self):
        self.configuration.operating_mode = AccountConfiguration.OperatingMode.MULTI
        self.configuration.save(update_fields=["operating_mode"])

        permission = Permission.objects.get(
            content_type__app_label="core",
            codename="view_branch",
        )
        self.role.permissions.add(permission)
        BranchMembership.objects.create(
            user=self.employee,
            branch=self.branch,
            role=self.role,
        )

        self.assertTrue(
            user_has_branch_permission(
                self.employee, self.branch, "view_branch", "core"
            )
        )

    def test_membership_without_permission_is_denied(self):
        self.configuration.operating_mode = AccountConfiguration.OperatingMode.MULTI
        self.configuration.save(update_fields=["operating_mode"])
        BranchMembership.objects.create(
            user=self.employee,
            branch=self.branch,
            role=self.role,
        )

        self.assertFalse(
            user_has_branch_permission(
                self.employee, self.branch, "view_branch", "core"
            )
        )

    def test_inactive_membership_is_denied(self):
        self.configuration.operating_mode = AccountConfiguration.OperatingMode.MULTI
        self.configuration.save(update_fields=["operating_mode"])
        BranchMembership.objects.create(
            user=self.employee,
            branch=self.branch,
            role=self.role,
            is_active=False,
        )

        self.assertFalse(
            user_has_branch_permission(
                self.employee, self.branch, "view_branch", "core"
            )
        )

    def test_role_must_belong_to_same_cafe_as_branch(self):
        other_cafe = CafeProfile.objects.create(name="کافه دیگر")
        other_role = Role.objects.create(
            cafe=other_cafe,
            name="مدیر",
            code="manager",
        )
        membership = BranchMembership(
            user=self.employee,
            branch=self.branch,
            role=other_role,
        )

        with self.assertRaises(ValidationError):
            membership.full_clean()

    def test_active_branches_are_returned_as_branch_queryset(self):
        self.configuration.operating_mode = AccountConfiguration.OperatingMode.MULTI
        self.configuration.save(update_fields=["operating_mode"])
        BranchMembership.objects.create(
            user=self.employee,
            branch=self.branch,
            role=self.role,
        )

        branches = get_user_active_branches(self.employee)
        self.assertEqual(list(branches), [self.branch])
