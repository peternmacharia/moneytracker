"""
Module: seed_data.py
Description: This module contains the init_data() function which seeds the database
with initial data for development and testing purposes.
"""

from datetime import date, timedelta, datetime, timezone
from app.extensions import db
from app.models import (
    User, Role, Permission, RolePermission, Notification, NotificationCategory
)

def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


def init_data():
    """
    Initialize the database with seed data.
    """
    print("=" * 60)
    print("Initializing database with seed data...")
    print("=" * 60)

    try:
        # ──────────────────────────────────────────────────────────────────────
        # 1. ROLES
        # ──────────────────────────────────────────────────────────────────────
        print("\n📋 Creating Roles...")
        role_defs = [
            ("super", "Full system access with all permissions"),
            ("admin", "Permission to manage the system"),
            ("user", "System user with basic access"),
        ]

        created_roles = 0
        role_objects = {}
        for name, desc in role_defs:
            role = Role.query.filter_by(name=name).first()
            if role:
                role_objects[name] = role
                print(f"⏭ Role '{name}' already exists — skipped.")
                continue
            role = Role(name=name, description=desc, is_active=True)
            db.session.add(role)
            db.session.flush()
            role_objects[name] = role
            created_roles += 1
            print(f"  ✅ Role '{name}' created.")

        db.session.commit()
        print(f"  ✔ Created {created_roles} role(s).")

        # Role references for easy access
        super_admin = role_objects.get("super")
        system_user = role_objects.get("user")

        # ──────────────────────────────────────────────────────────────────────
        # 2. PERMISSIONS
        # ──────────────────────────────────────────────────────────────────────
        print("\n📋 Creating Permissions...")
        permission_defs = [
            ("user:view",   "user", "view"),
            ("user:create", "user", "create"),
            ("user:update", "user", "update"),
            ("user:delete", "user", "delete"),

            ("role:view",   "role", "view"),
            ("role:create", "role", "create"),
            ("role:update", "role", "update"),
            ("role:delete", "role", "delete"),

            ("permission:view",     "permission", "view"),
            ("permission:create",   "permission", "create"),
            ("permission:update",   "permission", "update"),
            ("permission:delete",   "permission", "delete"),

            ("workspace:view",     "workspace", "view"),
            ("workspace:create",   "workspace", "create"),
            ("workspace:update",   "workspace", "update"),
            ("workspace:delete",   "workspace", "delete"),

            ("workspacerole:view",     "workspacerole", "view"),
            ("workspacerole:create",   "workspacerole", "create"),
            ("workspacerole:update",   "workspacerole", "update"),
            ("workspacerole:delete",   "workspacerole", "delete"),

            ("workspacepermission:view",     "workspacepermission", "view"),
            ("workspacepermission:create",   "workspacepermission", "create"),
            ("workspacepermission:update",   "workspacepermission", "update"),
            ("workspacepermission:delete",   "workspacepermission", "delete"),

            ("workspacemember:view",     "workspacemember", "view"),
            ("workspacemember:create",   "workspacemember", "create"),
            ("workspacemember:update",   "workspacemember", "update"),
            ("workspacemember:delete",   "workspacemember", "delete"),
        ]

        created_perms = 0
        permission_objects = {}
        for name, resource, action in permission_defs:
            perm = Permission.query.filter_by(name=name).first()
            if perm:
                permission_objects[name] = perm
                continue
            perm = Permission(name=name, resource=resource, action=action)
            db.session.add(perm)
            db.session.flush()
            permission_objects[name] = perm
            created_perms += 1

        db.session.commit()
        print(f"✔ Created {created_perms} permission(s).")

        # ──────────────────────────────────────────────────────────────────────
        # 3. ROLE PERMISSIONS
        # ──────────────────────────────────────────────────────────────────────
        print("\n📋 Assigning Permissions to Roles...")

        # all_perms = Permission.query.all()
        assigned_count = 0

        # Super Admin gets ALL permissions
        super_admin_perms = [
            "user:view", "user:create", "user:update", "user:delete",
            "permission:view", "permission:create", "permission:update", "permission:delete",
            "role:view", "role:create", "role:update", "role:delete",
        ]
        for perm_name in super_admin_perms:
            perm = permission_objects.get(perm_name)
            if not perm:
                print(f"⚠️ Permission '{perm_name}' not found — skipping.")
                continue
            existing = RolePermission.query.filter_by(
                role_id=super_admin.id, permission_id=perm.id
            ).first()
            if not existing:
                db.session.add(RolePermission(
                    role_id=super_admin.id,
                    permission_id=perm.id
                ))
                assigned_count += 1

        # System user gets most permissions
        system_user_perms = [
            "workspace:view", "workspace:create", "workspace:update", "workspace:delete",
            "workspacemember:view", "workspacemember:create", "workspacemember:update", "workspacemember:delete",
            "workspacepermission:view", "workspacepermission:create", "workspacepermission:update", "workspacepermission:delete",
            "workspacerole:view", "workspacerole:create", "workspacerole:update", "workspacerole:delete",
        ]
        for perm_name in system_user_perms:
            perm = permission_objects.get(perm_name)
            if perm:
                if not perm:
                    print(f"⚠️ Permission '{perm_name}' not found — skipping.")
                    continue
                existing = RolePermission.query.filter_by(
                    role_id=system_user.id, permission_id=perm.id
                ).first()
                if not existing:
                    db.session.add(RolePermission(
                        role_id=system_user.id,
                        permission_id=perm.id
                    ))
                    assigned_count += 1

        db.session.commit()
        print(f"  ✔ Assigned {assigned_count} permission(s) to roles.")


        # ──────────────────────────────────────────────────────────────────────
        # 4. USERS
        # ──────────────────────────────────────────────────────────────────────
        print("\n👤 Creating Users...")
        user_defs = [
            ("admin@techcorp.co.ke", "John", "Kariuki", "KENYA", "KES", "Africa/Nairobi", super_admin),
            ("user@techcorp.co.ke", "Mary", "Wanjiru", "KENYA", "KES", "Africa/Nairobi", system_user),
        ]

        created_users = 0
        user_objects = {}
        for email, firstname, lastname, country, currency, timezone, role in user_defs:
            existing = User.query.filter_by(email=email).first()
            if existing:
                user_objects[email] = existing
                print(f"  ⏭ User '{email}' already exists — skipped.")
                continue
            user = User(
                email=email,
                firstname=firstname,
                lastname=lastname,
                country=country,
                currency=currency,
                timezone=timezone,
                role_id=role.id,
                is_active=True,
                is_email_verified=True,
                is_locked=False
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            user_objects[email] = user
            created_users += 1
            print(f"  ✅ User '{email}' created.")

        db.session.commit()
        print(f"  ✔ Created {created_users} user(s).")


        # ──────────────────────────────────────────────────────────────────────
        # 5. NOTIFICATIONS
        # ──────────────────────────────────────────────────────────────────────
        print("\n🔔 Creating Notifications...")

        user_john = user_objects.get("admin@techcorp.co.ke")
        user_mary = user_objects.get("user@techcorp.co.ke")

        notification_defs = [
            (user_john, "Welcome to TechCorp", "Welcome to the Asset Management System!",
             NotificationCategory.INFO, False, False),
            (user_mary, "System Update", "Welcome to the Asset Management System!",
             NotificationCategory.INFO, False, False),
            (user_mary, "System Update", "System maintenance scheduled for this weekend.",
             NotificationCategory.WARNING, False, False),
        ]

        created_notifications = 0
        for user, title, message, n_category, is_urgent, is_read in notification_defs:
            if not user:
                print(f"⚠️ User not found for notification '{title}' — skipping.")
                continue

            notify = Notification(
                user_id=user.id,
                title=title,
                message=message,
                category=n_category,
                is_urgent=is_urgent,
                is_read=is_read,
                created_at=utc_now(),
                read_at=utc_now() if is_read else None
            )
            db.session.add(notify)
            created_notifications += 1
            print(f"  ✅ Notification '{title}' created.")

        db.session.commit()
        print(f"  ✔ Created {created_notifications} notification(s).")


        print("\n" + "=" * 60)
        print("✅ SEED DATA COMPLETE!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"  • Roles: {created_roles}")
        print(f"  • Users: {created_users}")
        print("\n🔑 Default Login Credentials:")
        print("  • admin@techcorp.co.ke / password123 (Super Admin)")
        print("  • system@techcorp.co.ke / password123 (System User)")
        print("=" * 60)

    except Exception as e:
        db.session.rollback()
        print(f"\n✗ Error seeding data: {str(e)}")
        raise
