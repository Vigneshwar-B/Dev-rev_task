from flask import render_template, request, redirect, session
from models import User, Flight, Booking, Employee
from utils import check_database_tables
from app import app, db

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
        flights = Flight.query.filter(Flight.departure_time.date() == date).all()
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

        new_flight = Flight(
            flight_number=flight_number,
            departure_time=departure_time,
            total_seats=total_seats,
            available_seats=available_seats,
            arrival_name=arrival_name,
            departure_name=departure_name
        )
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

        new_flight = Flight(
            flight_number=flight_number,
            departure_time=departure_time,
            total_seats=total_seats,
            available_seats=available_seats,
            arrival_name=arrival_name,
            departure_name=departure_name
        )
        db.session.add(new_flight)
        db.session.commit()

        return redirect('/admin')

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

