from flask import Blueprint, render_template, redirect, url_for, session
from flask_login import current_user, login_required
from app.models.models import User

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if current_user.account_status != 'admin':
        return redirect(url_for('game.index'))  # Adjust this to your non-admin dashboard route

    users = User.query.all()
    user_count = User.query.count()
    return render_template('admin_dashboard.html', users=users, user_count=user_count)
