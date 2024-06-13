from app import create_app, db
from app.models.models import User  # Adjust the import according to your project structure

def list_all_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        for user in users:
            print(f"Username: {user.username}, Email: {user.email}")

if __name__ == "__main__":
    list_all_users()
