from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import bp
from app.models.user import User
from app.extensions import db
from app.blueprints.auth.forms import LoginForm, RegisterForm, ResetPasswordRequestForm, ResetPasswordForm


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('workspaces.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('workspaces.dashboard')
            return redirect(next_page)
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html', form=form)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('workspaces.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('workspaces.dashboard'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        # For MVP, just show a message
        # In production, send email with reset token
        flash('Password reset functionality coming soon', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('workspaces.dashboard'))
    
    # For MVP, token validation is placeholder
    form = ResetPasswordForm()
    if form.validate_on_submit():
        flash('Password reset functionality coming soon', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
