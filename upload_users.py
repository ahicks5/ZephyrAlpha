import csv
import sys
import os
from app import create_app, db
from app.models.models import User  # Adjust the import according to your project structure

CSV_PATH = '/var/www/html/users.csv'

def upload_users_from_csv(csv_filename=CSV_PATH):
    app = create_app()
    with app.app_context():
        if not os.path.exists(csv_filename):
            print(f"File {csv_filename} does not exist.")
            return

        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            column_names = reader.fieldnames
            for row in reader:
                action = row.get('action', '').strip().lower()
                if action == 'delete':
                    user = User.query.get(row['id'])
                    if user:
                        db.session.delete(user)
                        print(f"Deleted user {user.id}")
                else:
                    user = User.query.get(row['id'])
                    if user:
                        for column in column_names:
                            if column != 'action':
                                setattr(user, column, row[column])
                    else:
                        new_user_data = {column: row[column] for column in column_names if column != 'action'}
                        new_user = User(**new_user_data)
                        db.session.add(new_user)
            db.session.commit()
    print(f"Users data has been updated from {csv_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py [upload]")
        sys.exit(1)

    action = sys.argv[1].lower()
    if action == "upload":
        upload_users_from_csv()
    else:
        print("Invalid action. Use 'upload'.")
        sys.exit(1)
