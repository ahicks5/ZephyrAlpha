import csv
import sys
import os
from app import create_app, db
from app.models.models import User  # Adjust the import according to your project structure

CSV_PATH = '/var/www/html/users.csv'

def list_all_users_to_csv(csv_filename=CSV_PATH):
    app = create_app()
    with app.app_context():
        users = User.query.all()
        column_names = [column.name for column in User.__table__.columns]
        column_names.append('action')  # Add action column
        with open(csv_filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)  # Write the header
            for user in users:
                row = [getattr(user, column) for column in User.__table__.columns.keys()]
                row.append('')  # Empty action column
                writer.writerow(row)
    print(f"Users data has been written to {csv_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py [download]")
        sys.exit(1)

    action = sys.argv[1].lower()
    if action == "download":
        list_all_users_to_csv()
    else:
        print("Invalid action. Use 'download'.")
        sys.exit(1)
