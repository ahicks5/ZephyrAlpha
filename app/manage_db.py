import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db  # Ensure this matches your actual module structure

def drop_all_tables():
    app = create_app()
    with app.app_context():
        db.drop_all()
        print("All tables dropped.")

def create_all_tables():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("All tables created.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manage_db.py <drop|create|recreate>")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "drop":
        drop_all_tables()
    elif command == "create":
        create_all_tables()
    elif command == "recreate":
        drop_all_tables()
        create_all_tables()
    else:
        print("Invalid command. Use 'drop', 'create', or 'recreate'.")
        sys.exit(1)
