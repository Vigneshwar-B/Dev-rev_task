# Flight Booking System

A Flask-based web application to manage flight bookings for users and administrators. This application enables users to sign up, log in, view flights, and make bookings, while administrators can manage flights (create, edit, delete) through a secure dashboard.

## Features

- **User Registration & Login**: Users can sign up, log in, and view available flights for booking.
- **Flight Booking**: Users can book flights based on available seats.
- **Admin Dashboard**: Admins can add, edit, view, and delete flights.
- **Role-Based Access**: Separate login for users and administrators.

## Project Structure

- **app.py**: Main application file with route handling.
- **models.py**: Defines database models for Users, Flights, Bookings, and Employees.
- **templates/**: HTML templates for rendering pages.
- **static/**: Folder for static resources (CSS, images, etc.).
- **requirements.txt**: Required dependencies.

## Getting Started

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd flight-booking-system
    ```

2. **Set Up Environment**:
    - Install dependencies:
      ```bash
      pip install -r requirements.txt
      ```
    - Configure PostgreSQL database URI in `app.py`:
      ```python
      app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<username>:<password>@<host>/<database>'
      ```

3. **Database Initialization**:
    ```bash
    python
    >>> from app import db
    >>> db.create_all()
    ```

4. **Run the Application**:
    ```bash
    python app.py
    ```
    Access the app at `http://127.0.0.1:5000`.

## Usage

- **User Functions**:
  - Register and log in to book flights.
  - View all available flights and book based on seats available.

- **Admin Functions**:
  - Log in with admin credentials to manage flights.
  - Access the admin dashboard to add, update, and delete flights.

## Dependencies

- Flask
- Flask-SQLAlchemy
- psycopg2

## License

This project is licensed under the MIT License.

---

This `README.md` provides a quick overview of your project, setup instructions, features, and dependencies. Adjust the database URI and any paths as needed based on your environment.
