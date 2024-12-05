#Import Flask, Config file and PyMySQL

from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
import pymysql
from functools import wraps
from datetime import timedelta

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']

app.permanent_session_lifetime = timedelta(minutes = 30) # max time

# use below decorator
#
# @cred_check('')
def cred_check(*roles):
    def decorator(fun):
        @wraps(fun)
        def wrapped_fun(*args, **kwargs):
            if session.get('role') not in roles:
                flash('You do not have permission to access this page.')
                return redirect(url_for('login'))
            return fun(*args, **kwargs)
        return wrapped_fun
    return decorator

#START HERE
@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        identification_num = request.form.get('ID Number')
        email = request.form.get('email-address')
        credentials = request.form.get('credentials')

        is_coordinator = False
        user_authenticated = False
        is_worker = False

        if identification_num and email:

            try: 
                identification_num = int(identification_num)
            except ValueError:
                flash("ID number must be a number")
                return redirect(url_for('login'))
            
            
            if credentials:
                is_coordinator = verify_coordinator(email, int(identification_num), credentials)
                user_authenticated = is_coordinator
                if is_coordinator:
                    session['role'] = 'coordinator'
                    session['employee_id'] = identification_num
                    session['email'] = email
                    print("coordinator")
            else:
                user_authenticated = verify_secretary(email, int(identification_num))
                if user_authenticated:
                    session['role'] = 'secretary'
                    session['employee_id'] = identification_num
                    session['email'] = email
                    print('secretary')
                if user_authenticated == False:
                    user_authenticated = employee_login_helper(email, identification_num)
                    if user_authenticated:
                        session['role'] = 'worker'
                        session['employee_id'] = identification_num
                        session['email'] = email
                        print('worker')
                        is_worker = True
        else:
            flash("You must provide your ID number and email address")
            return redirect(url_for('login'))

        if user_authenticated and is_coordinator:
            return render_template('coordinator_home.html')
        elif user_authenticated and (is_worker == False):
            return render_template('secretary_home.html')
        elif user_authenticated and is_worker:
            return render_template('create_health_metric.html')
        else:
            flash('Incorrect Credentials')
            return redirect(url_for('login'))

    else: #GET
        return render_template('login.html')

# Logout user
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out")
    return redirect(url_for('login'))

# Return a list of all employees
@app.route('/employees')                                                                             # route app 
def employees():
    con = get_db_connection()                                                                        # create connection, assing to con
    try:                                                                                                    
        with con.cursor() as cursor:                                                                 # assign con.cursor to cursor
            cursor.execute('SELECT employee_id, fname, lname, role, work_email FROM employee')       # Execute Query, store results in cursor
            employees = cursor.fetchall()                                                            # store query results in employees
            return render_template('employees.html', employees=employees)                            # return template, as well as data to be displayed
    except Exception as e:                                                                           # Exception handling
        print(f"An error occurred: {e}")
        print("Config variables: ", app.config['DB_HOST'], app.config['DB_USER'], app.config['DB_PASSWORD'], app.config['DB_NAME'])
        return render_template('employees.html', error="Could not fetch employees.")
    finally:
        con.close()                                                                                  # Always use 'finally' to ensure DB connection gets closed

@app.route('/secretary_home')
@cred_check('secretary')
def secretary_home():
    return render_template('secretary_home.html')

@app.route('/coordinator_home')
@cred_check('coordinator')
def coordinator_home():
    return render_template('coordinator_home.html')


# goal: ensure no employee exists with the given ID, 
#       handle coordinator insertion
# status: Achieved
#
# work needed: 
#   - Frontend styling error when "Wellness Coordinator" is the selected role
#   - Frontend "flash" style adjustment
@app.route('/add_employee', methods =['GET', 'POST'])
@cred_check('worker', 'secretary', 'coordinator')
def add_employee():
    if request.method == 'POST':

        emp_id = request.form.get('employee_id')
        # check if ID number is associated with an existing worker
        taken = verify_employee(emp_id)
        if taken:
            flash("Employee ID number is taken!")
            return render_template('add_employee.html')
        
        if open:
            con = get_db_connection()
            try:
                with con.cursor() as cursor:
                    insert ="""
                                INSERT INTO employee (employee_id, fname, middle_initial, lname, `role` , phone_number, department_id, work_email)
                                VALUES
                                (%s, %s, %s, %s, %s, %s, %s, %s)
                            """
                    
                    cursor.execute(insert, 
                                   (request.form.get('employee_id'),
                                    request.form.get('fname'),
                                    request.form.get('middle_initial'),
                                    request.form.get('lname'),
                                    request.form.get('role'),
                                    request.form.get('phone_number'),
                                    request.form.get('department_id'),
                                    request.form.get('work_email')))
                    
                    con.commit() # commit insert

                    
                    if request.form.get('role') == 'coordinator':
                        wc_insert = """
                                        INSERT INTO wellness_coordinator (employee_id, area_of_expertise, coordinator_credentials)
                                        VALUES (%s, %s, %s)
                                    """
                        
                        cursor.execute(wc_insert,(
                                       request.form.get('employee_id'),
                                       request.form.get('area_of_expertise'),
                                       request.form.get('coordinator_credentials')))
                        
                        con.commit()

            except Exception as e:
                print(f"An error occurred in add_employee routing: {e}")
                flash("error")
                return render_template('add_employee.html')
            finally:
                con.close()

            if verify_employee(request.form.get('employee_id')):
                flash('Success!')
                return render_template('add_employee.html')
            else:
                flash('Validation Error: 243')
                return render_template('add_employee.html')
    else:
        return render_template('add_employee.html')

#   Build & Implement
# - Only the workers or secretaries may be deleted using this tool
#
#
# TO-DO : 
# Validate the input using the function "verify_coordinator_alt" to first check if the employee ID
# Belongs to a coordinator. Provide the user feedback is the employee ID belongs to a coordinator. - Micah
@app.route('/delete_employee', methods=['GET', 'POST'])
@cred_check('secretary', 'coordinator')
def delete_employee():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')

        if employee_id:
            try:
                employee_id = int(employee_id)  # Convert to integer
            except ValueError:
                flash("Employee ID must be a number.")
                return redirect(url_for('delete_employee'))

            con = get_db_connection()  # Establish database connection
            try:
                with con.cursor() as cursor:
                    # Check if the employee exists
                    cursor.execute("SELECT * FROM employee WHERE employee_id = %s", (employee_id,))
                    employee = cursor.fetchone()

                    if employee:
                        # Delete the employee
                        cursor.execute("DELETE FROM employee WHERE employee_id = %s", (employee_id,))
                        con.commit()  # Commit the changes
                        flash(f'Employee with ID {employee_id} has been deleted successfully.')
                    else:
                        flash(f'No employee found with ID {employee_id}.')
            except Exception as e:
                print(f"An error occurred while deleting the employee: {e}")
                flash("An error occurred while trying to delete the employee.")
            finally:
                con.close()  # Ensure the connection is closed

            return redirect(url_for('delete_employee'))  # Redirect to the same page after handling the form

    return render_template('delete_employee.html')  # Render the delete employee page for GET request

# Build & Implement
# Get the employee ID
#         Employee email
#         Program ID
#         Program Name
@app.route('/enroll_employee', methods = ['GET', 'POST'])
@cred_check('secretary', 'coordinator')
def enroll_employee():
    if request.method == 'GET':
        return render_template('enroll_employee.html')
    
    emp_id = int(request.form.get('employee_id'))
    prg_id = int(request.form.get('program_id'))

    flash("Blahhh")

    print(f"{emp_id=}, {prg_id=}")
    return render_template('enroll_employee.html')

# Build & Implement
# 
# 
# TO-DO : 
# DELETE "Coordinator_Credentials" From frontend. it is not needed
# CHANGE "Area of Expertise" TO "Program ID" on frontend. The "Area of Expertise" field is currently used to pass the "program_id" to the backend
# ADJUST flash messages display location
# 
# micah - 
# validate input dates(low priority)
@app.route('/add_wellness_program', methods = ['GET', 'POST'])
@cred_check('secretary', 'coordinator')
def add_wellness_program():
    """
    
    UNFINISHED - Delete Coordinator "Area of Expertise" , "Coordinator Credentials" From frontend

    Requirements
        Program Details     - Program Name, Start Date, End Date, Type
        Coordinator Details - Coordinator ID

        
    ARGS PASSED - 
    program_name
    program_type
    start_date
    end_date

    coordinator_id
    program ID             - USING FRONTEND "expertise"
    
    """
    if request.method == 'POST':
        
        program_name   = str(request.form.get('program_name'))
        program_type   = str(request.form.get('program_type'))
        start_date     = str(request.form.get('start_date'))
        end_date       = str(request.form.get('end_date'))
        coordinator_id = int(request.form.get('coordinator_id'))
        program_id     = int(request.form.get('expertise'))

        id_number_available = not verify_program(program_id)
        valid_coord = verify_coordinator_alt(coordinator_id)

        if not id_number_available:
            flash("That Program ID number is taken!")
            return render_template('add_wellness_program.html')
        elif not valid_coord:
            flash("Coordinator ID must be valid!")
            return render_template('add_wellness_program.html')

        if id_number_available and valid_coord:
            con = get_db_connection()
            try:
                with con.cursor() as cursor:
                    query = """
                                INSERT INTO wellness_program(program_id, employee_id, end_date, program_name, start_date, type)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """
                    
                    cursor.execute(query, (program_id, coordinator_id, 
                                           end_date, program_name, 
                                           start_date, get_type(program_type)))
                    con.commit()

                    query_2 = """
                                INSERT INTO coordinated_by(employee_id, program_id)
                                VALUES (%s, %s)
                              """
                    
                    cursor.execute(query_2, (coordinator_id, program_id))

                    con.commit()

            except Exception as e:
                print(f"An error occurred in routing for add_wellness_program : {e}")
                flash("Routing Error - Check MySQL Server Status")
                return render_template('add_wellness_program.html')
            finally:
                con.close()

        if verify_program(program_id):
            flash('Success!')
            return render_template('add_wellness_program.html')
        else: # Insertion unsuccessful
            flash('Validation error : add_wellness_program Routing')
            return render_template('add_wellness_program.html')
    else: # GET
        return render_template('add_wellness_program.html')


@app.route('/view_health_metric', methods = ['GET'])
@cred_check('coordinator')
def view_health_metric():
    try:
        con = get_db_connection()
        with con.cursor(pymysql.cursors.DictCursor) as cursor:
            # Query to fetch latest health metrics
            query = """
                SELECT fname AS 'First Name', 
                       lname AS 'Last Name', 
                       resting_heart_rate AS 'Resting BPM', 
                       cholesterol_levels AS 'Cholesterol', 
                       blood_pressure_systolic AS 'Sys', 
                       blood_pressure_diastolic AS 'DBP', 
                       bmi AS 'BMI',
                       date_measured AS 'Date Measured'
                FROM employee
                LEFT JOIN health_metrics
                ON employee.employee_id = health_metrics.employee_id
                WHERE date_measured = (
                    SELECT MAX(date_measured) 
                    FROM health_metrics 
                    WHERE health_metrics.employee_id = employee.employee_id
                )
                ORDER BY date_measured DESC;
            """
            cursor.execute(query)
            health_metrics = cursor.fetchall()
            print(f"Health Metrics: {health_metrics}")
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('view_health_metric.html', health_metrics=[])
    finally:
        print("Closing database connection.")
        con.close()
        print("Closed.")


    # Ensure to render the template outside the try catch block, in order
    # to avoid the connection block Flask performs when a DB connection is not closed.
    # This happens because Flask is single threaded (by default)
    return render_template('view_health_metric.html', health_metrics=health_metrics)
    


@app.route('/create_health_metric', methods=['GET', 'POST'])
@cred_check('coordinator')
def create_health_metric():
    debug = True
    con = None  # Initialize con variable to avoid UnboundLocalError
    if request.method == 'POST':
        if debug : 
            print("meow1")
            print(f"Form Data: {request.form}")
        # Extracting the data from the form
        try:
            employee_id = request.form.get('employee_id')  # Expecting employee_id from the form
            date_measured = request.form.get('date_measured')
            cholesterol_levels = request.form.get('cholesterol_levels')
            resting_heart_rate = request.form.get('resting_heart_rate')
            blood_pressure_systolic = request.form.get('blood_pressure_systolic')
            blood_pressure_diastolic = request.form.get('blood_pressure_diastolic')
            bmi = request.form.get('bmi')
            

            # Validate inputs and handle default values if necessary
            if not employee_id or not date_measured:
                flash("Employee ID and Date Measured are required fields.", "danger")
                return render_template('create_health_metric.html')
            if debug : print("meow2")
            # Convert values to appropriate types if available, otherwise leave as None
            cholesterol_levels = int(cholesterol_levels) if cholesterol_levels else None
            resting_heart_rate = int(resting_heart_rate) if resting_heart_rate else None
            blood_pressure_systolic = int(blood_pressure_systolic) if blood_pressure_systolic else None
            blood_pressure_diastolic = int(blood_pressure_diastolic) if blood_pressure_diastolic else None
            bmi = float(bmi) if bmi else None

            # Establish database connection
            con = get_db_connection()

            if debug and con:
                print("Connection Recieved")
            elif debug and not con:
                print("Connection unsuccessful")

            with con.cursor() as cursor:
                # Check if the employee ID exists in the employee table
                cursor.execute('SELECT COUNT(*) FROM employee WHERE employee_id = %s', (employee_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    flash("Employee ID does not exist.", "danger")
                    return render_template('create_health_metric.html')

                # Insert health metric data into the health_metrics table
                insert_query = """
                INSERT INTO health_metrics (employee_id, date_measured, cholesterol_levels, resting_heart_rate, 
                                            blood_pressure_systolic, blood_pressure_diastolic, bmi)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                if debug:
                    print(f"Query: {insert_query}")
                    print(f"Parameters: {employee_id=}, {date_measured=}, {cholesterol_levels=}, {resting_heart_rate=}, "
                          f"{blood_pressure_systolic=}, {blood_pressure_diastolic=}, {bmi=}")
    
                cursor.execute(insert_query, (employee_id, date_measured, cholesterol_levels, resting_heart_rate,
                                              blood_pressure_systolic, blood_pressure_diastolic, bmi))

                # Commit the transaction
                con.commit()
                flash("Health metric successfully added.", "success")
                if debug : print("meow3")

        except Exception as e:
            # Rollback in case of an error
            if con:
                con.rollback()  # Only call rollback if the connection was established
            flash(f"Error: {str(e)}", "danger")
            print(f"Error : {e}")
        finally:
            # Ensure the database connection is always closed
            if con:
                con.close()

        return redirect(url_for('create_health_metric'))  # Redirect back to the same page

    return render_template('create_health_metric.html')  # GET request: render the form


"""
needs to handle a GET request, not just post - Micah

Provided with a program ID, return contact info for enrolled employees
"""
@app.route('/view_enrollment_list', methods=['GET', 'POST'])
@cred_check('coordinator')
def view_enrollment_list():
    con = get_db_connection()
    enrollment_list = []
    program_ids = []

    try:
        with con.cursor() as cursor:
            # Fetch program IDs for dropdown
            cursor.execute("SELECT program_id FROM wellness_program")
            program_ids = [row['program_id'] for row in cursor.fetchall()]  # Transform to list

            if request.method == 'POST':
                program_id = request.form.get('program_id')
                if program_id:
                    query = """
                    SELECT
                        e.employee_id AS "Employee ID",
                        CONCAT(e.fname, ' ', e.lname) AS "Employee Name",
                        wp.program_id AS "Program ID",
                        wp.program_name AS "Program Name"
                    FROM
                        participates_in pi
                    JOIN
                        employee e ON pi.employee_id = e.employee_id
                    JOIN
                        wellness_program wp ON pi.program_id = wp.program_id
                    WHERE
                        wp.program_id = %s
                    ORDER BY
                        e.employee_id, wp.program_name;
                    """
                    cursor.execute(query, (program_id,))
                    enrollment_list = cursor.fetchall()
            else:
                # Default to show all enrollments
                cursor.execute("""
                SELECT
                    e.employee_id AS "Employee ID",
                    CONCAT(e.fname, ' ', e.lname) AS "Employee Name",
                    wp.program_id AS "Program ID",
                    wp.program_name AS "Program Name"
                FROM
                    participates_in pi
                JOIN
                    employee e ON pi.employee_id = e.employee_id
                JOIN
                    wellness_program wp ON pi.program_id = wp.program_id
                ORDER BY
                    e.employee_id, wp.program_name;
                """)
                enrollment_list = cursor.fetchall()

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        con.close()

    return render_template('view_enrollment_list.html', program_ids=program_ids, enrollment_list=enrollment_list)

# "No data available for department breakdown." - Micah
@app.route('/view_department_breakdown')
@cred_check('coordinator')
def view_department_breakdown():
    """
    Return a breakdown of departments and their respective employee counts.
    """
    con = get_db_connection()  # Establish database connection
    try:
        with con.cursor() as cursor:
            # Query to fetch department breakdown using department_id as department name
            cursor.execute("""
                SELECT department_id AS department_name, COUNT(employee_id) AS employee_count
                FROM employee
                GROUP BY department_id;
            """)
            department_breakdown = cursor.fetchall()  # Fetch all department records
            return render_template('view_department_breakdown.html', department_breakdown=department_breakdown)
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('view_department_breakdown.html', error="Could not fetch department breakdown.")
    finally:
        con.close()  # Ensure the connection is closed
        








# Create Connection
#
# Don't change this function 
def get_db_connection():
    print("Getting database connection from get_db_connection")
    return pymysql.connect(
        host = app.config['DB_HOST'],
        user = app.config['DB_USER'],
        password = app.config['DB_PASSWORD'],
        db = app.config['DB_NAME'],
        cursorclass=pymysql.cursors.DictCursor
    )

# This function returns true if the credentials correspond to a coordinator in the database, false otherwise
def verify_coordinator(email, id_num, cred):
    con = get_db_connection()
    result = False

    try:
        with con.cursor() as cursor:
            query = """
                    SELECT e.employee_id, e.work_email, wc.coordinator_credentials 
                        FROM employee e
                        JOIN wellness_coordinator wc ON e.employee_id = wc.employee_id
                        WHERE e.work_email = %s AND e.employee_id = %s AND e.role = 'coordinator' AND wc.coordinator_credentials = %s
                    """
            cursor.execute(query, (email, id_num, cred))
            row = cursor.fetchone()

            if row and row['work_email'] == email and int(row['employee_id']) == int(id_num) and row['coordinator_credentials'] == cred:
                result = True
            else:
                print("Coordinator Authentication failed in verify_coordinator")

    except Exception as e:
        print(f"An error occurred in verify_coordinator: {e}")
        result = False
        return render_template('add_wellness_program.html')
    
    finally:
        print("Closing database connection.")
        con.close()
        print("Closed!")
    
    return result



# This funcion returns true if the credentials provided correspond to a secretary in the databse, false otehrwise
def verify_secretary(email, id_num):
    con = get_db_connection()
    result = False

    try:
        with con.cursor() as cursor:
            query = """
                        SELECT employee_id, work_email, role 
                        FROM employee 
                        WHERE work_email = %s AND employee_id = %s AND role = 'secretary'
                    """
            cursor.execute(query, (email, id_num))
            row = cursor.fetchone()

            if row and row['work_email'] == email and int(row['employee_id']) == int(id_num):
                result = True
            else:
                print("Employee not a secretary : DEBUG : in verify_secretary")
    except Exception as e:
        print(f"An error occurred in verify_secretary: {e}")
        result = False
    finally:
        con.close()
    return result


# Returns True if employee exists in DB with provided id_num
def verify_employee(id_num):
    con = get_db_connection()
    result = False
    try:
        with con.cursor() as cursor:
            query = """
                        SELECT employee_id 
                        FROM employee
                        WHERE employee_id = %s
                    """
            cursor.execute(query, (id_num))
            if cursor.fetchone():
                result = True
            else:
                result = False
    except Exception as e:
        print(f"An error occurred in verify_employee: {e}")
        result = False
    finally:
        con.close()
    return result
    

# return true if program exists with ID
def verify_program(program_id):
    con = get_db_connection()
    result = False
    try:
        with con.cursor() as cursor:
            query = """
                        SELECT program_id
                        FROM wellness_program
                        WHERE program_id = %s
                    """
            cursor.execute(query, (program_id))
            if cursor.fetchone():
                result = True
            else:
                result = False
    except Exception as e:
        print(f"An error occurred in verify_program : {e}")
        result = False
    finally:
        con.close()
    return result

# return DB program type according to selection
def get_type(program_type):
    master_dict = {
        "Bmi Reduction Program" : "bmi",
        "Blood Pressure Monitoring" : "blood_pressure",
        "Heart Rate Control" : "heart_rate",
        "Cholesterol Management" : "cholesterol",
        "Mental Health Session" : "heart_rate",
        "Nutrition Program" : "bmi",
        "Fitness Challenge" : "bmi",
        "Other" : "bmi"
    }
    return master_dict.get(program_type, "bmi")

# True if employee ID belongs to a coordinator
def verify_coordinator_alt(emp_id):
    con = get_db_connection()
    result = False
    try: 
        with con.cursor() as cursor:
            query = """
                        SELECT employee_id
                        FROM wellness_coordinator
                        WHERE employee_id = %s
                    """
            cursor.execute(query, (emp_id))
            if cursor.fetchone():
                result = True
    except Exception as e:
        print(f"Invalid : Determined in verify_coordinator function call : {e}")
    finally:
        con.close()
    return result

# Return true if employee is a worker, false otherwise
def employee_login_helper(email, id_num):
    con = get_db_connection()
    result = False
    try:
        with con.cursor() as cursor:
            Role_Query        = """
                                    SELECT role
                                    FROM employee
                                    WHERE work_email = %s
                                    AND employee_id = %s
                                """
            cursor.execute(Role_Query, (email, id_num))
            role_row = cursor.fetchone()
            if role_row and role_row['role'] == 'worker':
                result = True
    except Exception as e:
        print(f"An error occurred in employee_login_helper: {e}")
    finally:
        con.close()
    return result



# Add "verify coordinator_alt(employee_id)" for /add_wellness_program
# Complete input validation for adding a program
# It must check coordinator is a valid coordinator
