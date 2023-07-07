import psycopg2
from sqlalchemy import func
from app import db, app

def check_database_tables():
    with app.app_context():
        try:
            conn = psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'])
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if the tables exist in the database
            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')")
            user_table_exists = cursor.fetchone()[0]

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'flight')")
            flight_table_exists = cursor.fetchone()[0]

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'booking')")
            booking_table_exists = cursor.fetchone()[0]

            cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'employee')")
            employee_table_exists = cursor.fetchone()[0]
            if not user_table_exists:
                db.create_all()

            if not flight_table_exists:
                db.create_all()

            if not booking_table_exists:
                db.create_all()

            if not employee_table_exists:
                db.create_all()

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            print(f"Error checking database tables: {e}")
