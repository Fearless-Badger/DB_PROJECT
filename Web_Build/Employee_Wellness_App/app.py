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
@app.route('/add_employee', methods =['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        pass
    return render_template('add_employee.html')