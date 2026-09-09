"""
app/forms/__init__.py - This module imports all form classes from the submodules and 
                        defines the __all__ variable for easy imports.
"""

from .auth import (LoginForm, SignupForm, SetPasswordForm, TwoFactorForm,
                   ResendVerificationForm, RequestResetForm,
                   ResetPasswordForm, ChangePasswordForm)
from .shared import ConfirmForm, DeleteForm
from .user import (ProfileForm, Enable2FAForm, Disable2FAForm)
from .role import CreateRoleForm, UpdateRoleForm
from .permission import CreatePermissionForm, UpdatePermissionForm
from .workspace import CreateWorkspaceForm, UpdateWorkspaceForm
from .wmember import CreateWMemberForm, UpdateWMemberForm

__all__ = [
    # Auth
    "LoginForm", "SignupForm", "SetPasswordForm", "TwoFactorForm", "ResendVerificationForm",
    "RequestResetForm", "ResetPasswordForm", "ChangePasswordForm",
    # Shared
    "ConfirmForm", "DeleteForm",
    # User
    "ProfileForm", "Enable2FAForm", "Disable2FAForm",
    # Role
    "CreateRoleForm", "UpdateRoleForm",
    # Permission
    "CreatePermissionForm", "UpdatePermissionForm",
    # Workspace
    "CreateWorkspaceForm", "UpdateWorkspaceForm",
    # Workspace Member
    "CreateWMemberForm", "UpdateWMemberForm"
    
]

# End of file