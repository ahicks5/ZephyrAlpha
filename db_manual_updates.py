from app import create_app, db
from app.models.models import User

def promote_user_to_admin(username):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            user.account_status = 'admin'
            db.session.commit()
            print(f"User {username} has been promoted to admin.")
        else:
            print(f"User {username} not found.")

if __name__ == "__main__":
    promote_user_to_admin('arhicks14')
