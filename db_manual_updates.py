from datetime import datetime
from sqlalchemy import text, DDL, inspect, create_engine, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import pandas as pd
from app import create_app, db
from app.models.models import User

Base = declarative_base()

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

def add_columns_with_ddl():
    app = create_app()
    with app.app_context():
        engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
        connection = engine.connect()

        # Define DDL statements to add new columns
        ddl_signup_time = DDL('ALTER TABLE "user" ADD COLUMN signup_time TIMESTAMP DEFAULT NULL')
        ddl_favorite_teams = DDL('ALTER TABLE "user" ADD COLUMN favorite_teams TEXT')

        # Execute DDL statements
        try:
            connection.execute(ddl_signup_time)
            print("Column 'signup_time' added successfully.")
        except Exception as e:
            print(f"Error adding column 'signup_time': {e}")

        try:
            connection.execute(ddl_favorite_teams)
            print("Column 'favorite_teams' added successfully.")
        except Exception as e:
            print(f"Error adding column 'favorite_teams': {e}")

        # Reflect only the 'user' table
        try:
            user_table = db.Table('user', db.Model.metadata, autoload_with=engine)
            print("ORM reflection for 'user' table completed.")
        except Exception as e:
            print(f"Error reflecting 'user' table: {e}")

        # Verify that the columns were added
        #verify_user_table_schema()

        # Update existing users' signup_time with the current time if not already set
        #update_users_signup_time(engine)

def verify_user_table_schema():
    try:
        insp = inspect(db.engine)
        columns = insp.get_columns('user')
        column_names = [column['name'] for column in columns]
        print(f"Current columns in 'user' table: {column_names}")
        assert 'signup_time' in column_names, "signup_time column not found in user table."
        assert 'favorite_teams' in column_names, "favorite_teams column not found in user table."
        print("Schema verification completed successfully.")
    except Exception as e:
        print(f"Error during schema verification: {e}")

def update_users_signup_time(engine):
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        users = session.query(User).all()
        print(f"Found {len(users)} users.")
        for user in users:
            if user.signup_time is None:
                user.signup_time = datetime.utcnow()
        session.commit()
        print("Users' signup_time updated successfully.")
    except Exception as e:
        print(f"Error updating users' signup_time: {e}")

def list_tables():
    app = create_app()
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in the database:")
        for table in tables:
            print(table)

def inspect_database():
    app = create_app()
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in the database:")
        for table in tables:
            print(f"\nTable: {table}")
            columns = inspector.get_columns(table)
            column_info = []
            for column in columns:
                col_data = {
                    'Column': column['name'],
                    'Type': str(column['type']),
                    'Primary Key': False,
                    'Foreign Key': False,
                    'Indexed': False
                }
                column_info.append(col_data)
                print(f"Column: {column['name']} - Type: {column['type']}")

            primary_key = inspector.get_pk_constraint(table)
            for col in primary_key['constrained_columns']:
                for info in column_info:
                    if info['Column'] == col:
                        info['Primary Key'] = True
            print(f"Primary Key: {primary_key['constrained_columns']}")

            foreign_keys = inspector.get_foreign_keys(table)
            for fk in foreign_keys:
                for col in fk['constrained_columns']:
                    for info in column_info:
                        if info['Column'] == col:
                            info['Foreign Key'] = f"{fk['referred_table']}({fk['referred_columns']})"
                print(f"Foreign Key: {fk['constrained_columns']} references {fk['referred_table']}({fk['referred_columns']})")

            indexes = inspector.get_indexes(table)
            for index in indexes:
                for col in index['column_names']:
                    for info in column_info:
                        if info['Column'] == col:
                            info['Indexed'] = True
                print(f"Index: {index['name']} - Columns: {index['column_names']} - Unique: {index['unique']}")

            df = pd.DataFrame(column_info)
            df.to_csv(f"/var/www/html/{table}_schema.csv", index=False)
            print(f"Schema for table '{table}' saved to {table}_schema.csv")

def save_table_data_to_csv():
    app = create_app()
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("Tables in the database:")
        for table in tables:
            print(f"\nFetching data from table: {table}")
            df = pd.read_sql_table(table, con=engine)
            df.to_csv(f"/var/www/html/{table}.csv", index=False)
            print(f"Data for table '{table}' saved to {table}.csv")

from sqlalchemy import create_engine, DDL
from app import create_app

def test_database_ddl():
    # Create the Flask app context
    app = create_app()
    with app.app_context():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        connection = engine.connect()

        # Define DDL statements to add new columns
        ddl_signup_time = DDL('ALTER TABLE "user" ADD COLUMN signup_time TIMESTAMP DEFAULT NULL')
        ddl_favorite_teams = DDL('ALTER TABLE "user" ADD COLUMN favorite_teams TEXT')

        # Execute DDL statements
        try:
            connection.execute(ddl_signup_time)
            print("Column 'signup_time' added successfully.")
        except Exception as e:
            print(f"Error adding column 'signup_time': {e}")

        try:
            connection.execute(ddl_favorite_teams)
            print("Column 'favorite_teams' added successfully.")
        except Exception as e:
            print(f"Error adding column 'favorite_teams': {e}")

        connection.close()
        engine.dispose()
        print("Test completed successfully.")

import os
from flask_migrate import Migrate
from alembic import command
from alembic.config import Config
from app import create_app, db

app = create_app()
migrate = Migrate(app, db)

def run_migrations():
    with app.app_context():
        # Setup Alembic configuration
        alembic_cfg = Config(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'migrations', 'alembic.ini'))

        # Check if the migration directory exists, if not initialize it
        migrations_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'migrations')
        if not os.path.exists(migrations_dir):
            command.init(alembic_cfg, migrations_dir)
            print("Initialized the migrations directory.")

        # Generate a new migration
        command.revision(alembic_cfg, message="Add signup_time and favorite_teams columns to user table", autogenerate=True)
        print("Migration script generated.")

        # Apply the migration
        command.upgrade(alembic_cfg, "head")
        print("Database upgraded.")


def update_all_signup_times():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        updated_count = 0

        for user in users:
            if user.signup_time is None:
                user.signup_time = datetime.utcnow()
                updated_count += 1

        db.session.commit()
        print(f"Signup time updated for {updated_count} users.")


if __name__ == '__main__':
    update_all_signup_times()



