#Configure SQLAlchemy connection string based on docker-compose environment variables
import os
from sqlalchemy import create_engine
import runpy
import sys

DB_USER = os.getenv('DB_USER', 'student')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password123')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'contact_db')

SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@localhost:{DB_PORT}/{DB_NAME}'
print("SQLAlchemy Database URI:", SQLALCHEMY_DATABASE_URI)
# Example usage with SQLAlchemy
engine = create_engine(SQLALCHEMY_DATABASE_URI)

engine.connect()  # This will attempt to connect to the database
runpy.run_path("COP4538-Code\\app.py", run_name="__main__")
