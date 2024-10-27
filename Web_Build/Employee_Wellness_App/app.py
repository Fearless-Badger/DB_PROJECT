#Import Flask, Config file and PyMySQL
from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
import pymysql

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

# Create Connection
def get_db_connection():
    return pymysql.connect(
        host = app.config['DB_HOST'],
        user = app.config['DB_USER'],
        password = app.config['DB_PASSWORD'],
        db = app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

# Render index.html
@app.route('/')
def index():
    return render_template('index.html')

# Return a list of all employees
@app.route('/employees')
def employees():
    con = get_db_connection()
    try:
        with con.cursor() as cursor:
            cursor.execute('SELECT employee_id, fname, lname, role, work_email FROM employee')
            employees = cursor.fetchall()
            return render_template('employees.html', employees=employees)
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Config variables: ", app.config['DB_HOST'], app.config['DB_USER'], app.config['DB_PASSWORD'], app.config['DB_NAME'])
        return render_template('employees.html', error="Could not fetch employees.")
    finally:
        con.close()

# Not yet implemented
@app.route('/secretary_home')
def secretary_home():
    return render_template('secretary_home.html')

@app.route('/coordinator_home')
def coordinator_home():
    return render_template('coordinator_home.html')

@app.route('/add_employee', methods =['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        pass
    return render_template('add_employee.html')

@app.route('/delete_employee')
def delete_employee():
    return render_template('delete_employee.html')

@app.route('/enroll_employee')
def enroll_employee():
    return render_template('enroll_employee.html')

@app.route('/add_wellness_program')
def add_wellness_program():
    return render_template('add_wellness_program.html')

@app.route('/view_health_metric')
def view_health_metric():
    return render_template('view_health_metric.html')

@app.route('/create_health_metric')
def create_health_metric():
    return render_template('create_health_metric.html')

@app.route('/view_enrollment_list')
def view_enrollment_list():
    return render_template('view_enrollment_list.html')

@app.route('/view_department_breakdown')
def view_department_breakdown():
    return render_template('view_department_breakdown.html')

@app.route('/health_highlight')
def health_highlight():
    return render_template('health_highlight.html')

@app.route('/successful_program')
def successful_program():
    return render_template('successful_program.html')

