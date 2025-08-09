"""
Models configuration file
"""

from app.extensions import db

# Log and Auth Models
from app.models.auditlog import Auditlog
from app.models.role import Role
from app.models.user import User, UserStatus

# Other Models
from app.models.category import Category
from app.models.transaction import Transaction, TType


def init_default_data():
    """
    A function to setup database and initialize table with default data
    """

    # Check if categories already exist if not create defaults
    if not Category.query.first():
        default_categories = [
            Category(name='Food & Dining', color='#ef4444', icon='🍽️',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Transportation', color='#3b82f6', icon='🚗',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Shopping', color='#8b5cf6', icon='🛍️',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Entertainment', color='#f59e0b', icon='🎬',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Bills & Utilities', color='#6b7280', icon='💡',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Healthcare', color='#10b981', icon='🏥',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Salary', color='#22c55e', icon='💼',
                     created_by='superadmin', updated_by='superadmin'),
            Category(name='Other Income', color='#06b6d4', icon='💰',
                     created_by='superadmin', updated_by='superadmin'),
        ]

        for category in default_categories:
            db.session.add(category)
        db.session.commit()

        print('Categories created successfully!')


    # Check if roles already exist if not create role ADMIN and USER
    if not Role.query.first():
        admin_role = Role(name='ADMIN', created_by='superadmin', updated_by='superadmin')
        user_role = Role(name='USER', created_by='superadmin', updated_by='superadmin')

        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()

        print('Roles created successfully!')

    # Check if users already exist if not create admin user
    if not User.query.first():
        admin_user = User(firstname='Super',
                          lastname='Admin',
                          fullname='Super Admin',
                          username='superadmin',
                          phone='+254700112233',
                          email='adminuser@mail.com',
                          role_id=admin_role.id,
                          status=UserStatus.ACTIVE,
                          created_by='superadmin',
                          updated_by='superadmin')
        admin_user.set_password('SuperMan@123.?')

        new_user = User(firstname='Dev',
                        lastname='Thunder',
                        fullname='Dev Thunder',
                        username='devthunder',
                        phone='+254700112233',
                        email='devpthunder@gmail.com',
                        role_id=user_role.id,
                        status=UserStatus.ACTIVE,
                        created_by='superadmin',
                        updated_by='superadmin')
        new_user.set_password('SuperMan@123.?')

        db.session.add(admin_user)
        db.session.add(new_user)

        db.session.commit()
        print('Admin User is created successfully!')

    print('Database is initialized successfully!')

# End of file
