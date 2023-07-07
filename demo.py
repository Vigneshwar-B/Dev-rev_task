from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import psycopg2
from sqlalchemy import func

app = Flask(__name__)
app.secret_key = "vigneshwar"  # Set your secret key for session management

# Configure PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://vigneshwar:OlmCvOoTmhP2IUruhWNgib9chYC1BsQQ@dpg-cijs4ltph6euh7hqi7g0-a.oregon-postgres.render.com/demo_35ax'
db = SQLAlchemy(app)

# Define the models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(255), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    arrival_name = db.Column(db.String(255), nullable=False)
    departure_name = db.Column(db.String(255), nullable=False)
    bookings = db.relationship('Booking', backref='flight', lazy=True)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=True)
    no_of_ticket = db.Column(db.Integer, nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

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
@app.route('/')
def home():
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin':
            session['admin'] = username
            return redirect('/admin/dashboard')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid credentials')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        full_name = request.form['full_name']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('signup.html', error='Username already exists')

        if len(password) < 7:
            return render_template('signup.html', error='Password must be at least 7 characters long')

        new_user = User(username=username, password=password, email=email, full_name=full_name)

        db.session.add(new_user)
        db.session.commit()

        return redirect('/login')

    return render_template('signup.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        date = request.form['date']
        flights = Flight.query.filter(func.date_trunc('day', Flight.departure_time) == date).all()
        return render_template('dashboard.html', flights=flights)

    return render_template('dashboard.html')

@app.route('/dashboard/user')
def user_dashboard():
    if 'username' not in session:
        return redirect('/login')

    username = session['username']
    user = User.query.filter_by(username=username).first()
    bookings = Booking.query.filter_by(user_id=user.id).all()
    return render_template('user_dashboard.html', bookings=bookings)



@app.route('/book_flight/<int:flight_id>', methods=['GET', 'POST'])
def book_flight(flight_id):
    flight = Flight.query.get(flight_id)

    if request.method == 'POST':
        num_tickets = int(request.form['num_tickets'])

        if num_tickets <= flight.available_seats:
            flight.available_seats -= num_tickets
            db.session.commit()

            username = session.get('username')
            user = User.query.filter_by(username=username).first()

            new_booking = Booking(user_id=user.id, flight_id=flight_id, no_of_ticket=num_tickets)
            db.session.add(new_booking)
            db.session.commit()

            return redirect('/dashboard')
        else:
            return render_template('ticket_counter.html', flight=flight, error='Not enough available seats')

    return render_template('ticket_counter.html', flight=flight)



@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        employee = Employee.query.filter_by(name=username, password=password).first()
        if employee:
            session['admin'] = username
            return redirect('/admin/dashboard')
        else:
            return render_template('admin_login.html', error='Invalid credentials')

    return render_template('admin_login.html')

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_employee = Employee.query.filter_by(name=username).first()
        if existing_employee:
            return render_template('admin_signup.html', error='Username already exists')

        new_employee = Employee(name=username, password=password)

        db.session.add(new_employee)
        db.session.commit()

        return redirect('/admin/login')

    return render_template('admin_signup.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        return redirect('/admin/login')

    if request.method == 'POST':
        flight_number = request.form['flight_number']
        departure_time = request.form['departure_time']
        total_seats = request.form['total_seats']
        available_seats = request.form['available_seats']
        arrival_name = request.form['arrival_name']
        departure_name = request.form['departure_name']

        new_flight = Flight(flight_number=flight_number, departure_time=departure_time,
                            total_seats=total_seats, available_seats=available_seats,
                            arrival_name=arrival_name, departure_name=departure_name)
        db.session.add(new_flight)
        db.session.commit()

        return redirect('/admin/dashboard')

    else:
        flights = Flight.query.all()
        return render_template('admin_dashboard.html', flights=flights)
        

@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'admin' not in session:
        return redirect('/admin/login')

    if request.method == 'POST':
        flight_number = request.form['flight_number']
        departure_time = request.form['departure_time']
        total_seats = request.form['total_seats']
        available_seats = total_seats 
        arrival_name = request.form['arrival_name']
        departure_name = request.form['departure_name']

        new_flight = Flight(flight_number=flight_number, departure_time=departure_time,
                            total_seats=total_seats, available_seats=available_seats,
                            arrival_name=arrival_name, departure_name=departure_name)
        db.session.add(new_flight)
        db.session.commit()

        return redirect('/admin/dashboard')

    return render_template('create_flight.html')



@app.route('/admin/get_flight/<int:flight_id>', methods=['GET'])
def get_flight(flight_id):
    flight = Flight.query.get(flight_id)
    return render_template('flight_info.html', flight=flight)

@app.route('/admin/edit_flight/<int:flight_id>', methods=['GET', 'POST'])
def edit_flight(flight_id):
    flight = Flight.query.get(flight_id)

    if request.method == 'POST':
        flight.flight_number = request.form['flight_number']
        flight.departure_time = request.form['departure_time']
        flight.total_seats = request.form['total_seats']
        flight.available_seats = request.form['available_seats']
        flight.arrival_name = request.form['arrival_name']
        flight.departure_name = request.form['departure_name']
        db.session.commit()
        return redirect('/admin/dashboard')

    return render_template('edit_flight.html', flight=flight)


@app.route('/admin/delete_flight/<int:flight_id>', methods=['POST'])
def delete_flight(flight_id):
    flight = Flight.query.get(flight_id)
    if not flight:
        return redirect('/admin/dashboard')  

    bookings = Booking.query.filter_by(flight_id=flight.id).all()
    for booking in bookings:
        db.session.delete(booking)

    # Delete the flight
    db.session.delete(flight)
    db.session.commit()

    return redirect('/admin/dashboard')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect('/login')

    return redirect('/login')


if __name__ == '__main__':
    check_database_tables()
    app.run(debug=True) 