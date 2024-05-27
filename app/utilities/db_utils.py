from time import sleep
# Import db from its initialized location, adjust according to your app structure
from ..database import db

def commit_db_periodically():
    from flask import current_app
    with current_app.app_context():
        while True:
            sleep(3)  # Wait for 3 seconds before each commit
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error committing to DB: {e}")
                db.session.rollback()
