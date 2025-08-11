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

        new_user = User(firstname='Guest',
                        lastname='User',
                        fullname='Guest User',
                        username='guestuser',
                        phone='+254700112233',
                        email='guestuser@mail.com',
                        role_id=user_role.id,
                        status=UserStatus.ACTIVE,
                        created_by='superadmin',
                        updated_by='superadmin')
        new_user.set_password('GuestMan@123.?')

        db.session.add(admin_user)
        db.session.add(new_user)

        db.session.commit()
        print('System Users is created successfully!')

    # Check if categories already exist if not create defaults
    if not Category.query.first():
        default_categories = [
            Category(name='Food & Dining', description='Food Stuff', icon='🍽️',
                     user_id=admin_user.id),
            Category(name='Transportation', description='Transport Stuff', icon='🚗',
                     user_id=admin_user.id),
            Category(name='Shopping', description='Shopping Stuff', icon='🛍️',
                     user_id=admin_user.id),
            Category(name='Entertainment', description='Entertainment Stuff', icon='🎬',
                     user_id=admin_user.id),
            Category(name='Bills & Utilities', description='Bills & Utility', icon='💡',
                     user_id=admin_user.id),
            Category(name='Healthcare', description='Healthcare & Wellbeing', icon='🏥',
                     user_id=admin_user.id),
            Category(name='Salary', description='Salary Stuff', icon='💼',
                     user_id=admin_user.id),
            Category(name='Other Income', description='Side Hustle Stuff', icon='💰',
                     user_id=admin_user.id),
        ]

        for category in default_categories:
            db.session.add(category)
        db.session.commit()

        print('Categories created successfully!')

    print('Database is initialized successfully!')

# End of file
