from flask_migrate import Migrate
from alembic.config import Config
from alembic import command
from app import create_app, db
import os

app = create_app()
migrate = Migrate(app, db)

def initialize_migrations():
    with app.app_context():
        # Initialize the migrations directory
        if not os.path.exists('migrations'):
            os.makedirs('migrations')
        alembic_cfg = Config()
        alembic_cfg.set_main_option("script_location", "migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])
        command.init(alembic_cfg, "migrations")
        print("Migrations directory initialized.")

def run_migrations():
    with app.app_context():
        # Setup Alembic configuration
        alembic_cfg = Config(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'migrations', 'alembic.ini'))
        alembic_cfg.set_main_option("script_location", "migrations")
        alembic_cfg.set_main_option("sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])

        # Generate a new migration
        command.revision(alembic_cfg, message="Apply database changes", autogenerate=True)
        print("Migration script generated.")

        # Apply the migration
        command.upgrade(alembic_cfg, "head")
        print("Database upgraded.")

if __name__ == '__main__':
    # Initialize migrations if not already initialized
    if not os.path.exists('migrations'):
        initialize_migrations()

    # Run migrations to apply changes
    run_migrations()
