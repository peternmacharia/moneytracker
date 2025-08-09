"""
Authentication configuration file that contains auth views and routes.
"""

from datetime import datetime
from io import BytesIO
import base64
import pyotp
import qrcode
# import functools
from flask import (Blueprint, current_app as app, flash, redirect,
                   render_template, url_for, request, session)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app.models.user import User
from app.forms.auth import LoginForm, TwoFactorForm
from app.extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_2fa_secret():
    """
    Generate a random secret key for 2FA
    """
    return pyotp.random_base32()

# Function to generate a QR code containing the TOTP URI
def generate_2fa_qrcode(username, secret):
    """
    Generate a QR code containing the TOTP URI
    """
    # Create a TOTP provisioning URI
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(username, issuer_name="UNTOLD IMS")

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)

    # Create image and convert to base64 for embedding in HTML
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


# Route to enable 2FA
@auth_bp.route('/enable_2fa/', methods=['GET', 'POST'])
@login_required
def enable_2fa():
    """
    Enable 2FA for the current user
    """
    form = TwoFactorForm()

    if request.method == 'GET':
        # Generate a new secret key
        secret = generate_2fa_secret()

        # Store secret temporarily in session
        session['temp_2fa_secret'] = secret

        # Generate QR code
        qrcode_data = generate_2fa_qrcode(current_user.username, secret)

        return render_template('auth/enable_2fa.html',
                               form=form,
                               secret=secret,
                               qrcode_data=qrcode_data,
                               title='Enable 2FA',
                               SETTINGS=True,
                               PROFILE=True)

    elif request.method == 'POST':
        # Get the temporary secret from session
        secret = session.get('temp_2fa_secret')
        if not secret:
            flash('Session expired. Please try again.', 'danger')
            return redirect(url_for('auth.enable_2fa'))

        # Get the verification code provided by the user
        # verification_code = request.form.get('verification_code')
        verification_code = form.verification_code.data
        if not verification_code:
            flash('Verification code is required.', 'danger')
            return redirect(url_for('auth.enable_2fa'))

        # Verify the code
        totp = pyotp.TOTP(secret)
        if totp.verify(verification_code):
            # Save the secret to the user's account
            current_user.two_factor_secret = secret
            current_user.is_2fa_enabled = True
            db.session.commit()

            # Clear the temporary secret from session
            session.pop('temp_2fa_secret', None)

            flash('Two-factor authentication enabled successfully!', 'success')
            return redirect(url_for('profile.about'))
        else:
            flash('Invalid verification code. Please try again.', 'danger')
            return redirect(url_for('auth.enable_2fa'))

# Route to disable 2FA
@auth_bp.route('/disable_2fa/', methods=['POST'])
@login_required
def disable_2fa():
    """
    Disable 2FA for the current user
    """
    current_user.is_2fa_enabled = False
    current_user.two_factor_secret = None
    db.session.commit()

    flash('Two-factor authentication has been disabled.', 'success')
    return redirect(url_for('profile.about'))


@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    """
    The Login View
    """
    app.logger.info('Login page accessed')
    form = LoginForm()

    if request.method == 'POST':
        email = form.email.data
        password = form.password.data

        error = None

        user = User.query.filter_by(email=email).first()

        if error:
            flash(error)
            app.logger.warning('Error accessing and submitting login page!')
        else:
            if user and check_password_hash(user.password, password):
                if user.is_2fa_enabled:
                    session['user_id_for_2fa'] = user.id
                    app.logger.info('User accessed 2fa verification page')
                    return redirect(url_for('auth.verify_2fa'))
                else:
                    login_user(user)
                    user.last_login = datetime.now()
                    db.session.commit()
                    # app.logger.info('Logged in Successfully!')
                    if user.role.name == 'ADMIN':
                        app.logger.info('%s admin login successfully', current_user.username)
                        flash("Admin Logged in successfully!", "success")
                        return redirect(url_for('base.admin'))
                    elif user.role.name == 'USER':
                        app.logger.info('%s user login successfully', current_user.username)
                        flash("User Logged in successfully!", "success")
                        return redirect(url_for('base.user'))

            app.logger.warning('Login attempt Failed!')
            flash("Login Unsuccessful. Please check email and password", "danger")
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html', form=form, title='Login')


# Route for 2FA verification
@auth_bp.route('/verify_2fa/', methods=['GET', 'POST'])
def verify_2fa():
    """
    The 2FA Verification View
    """

    form = TwoFactorForm()

    # Check if we have a user waiting for 2FA verification
    user_id = session.get('user_id_for_2fa')
    app.logger.info('User accessed 2fa verification page')
    if not user_id:
        app.logger.info('Login to access 2fa setup page!')
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    if not user:
        session.pop('user_id_for_2fa', None)
        app.logger.info('Login to access 2fa setup page!')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        verification_code = form.verification_code.data
        # verification_code = request.form.get('verification_code')

        # Verify the TOTP code
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(verification_code):
            # Clear the 2FA session data
            session.pop('user_id_for_2fa', None)

            # Log the user in
            login_user(user)
            user.last_login = datetime.now()
            db.session.commit()
            flash('Logged in successfully!', 'success')

            app.logger.info('User 2fa setup is successful')
            return redirect(url_for('base.dashboard'))
        else:
            app.logger.warning('User provided a wrong 2fa verification code!')
            flash('Invalid verification code. Please try again.', 'danger')

    return render_template('auth/verify_2fa.html',
                           form=form,
                           title='Verify 2FA',
                           SETTINGS=True,
                           PROFILE=True)


@auth_bp.route('/logout/')
@login_required
def logout():
    """
    The Logout view
    """
    # session.clear()
    app.logger.info('%s logged out successfully!', current_user.username)
    logout_user()
    # Flash a logout message
    flash("You have been successfully logged out!", "success")
    return render_template('auth/logout.html', title='Logout')

# End of file
