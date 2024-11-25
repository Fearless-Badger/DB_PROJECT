#Import Flask, Config file and PyMySQL

from flask import Flask, render_template, request, redirect, url_for, flash, session
from config import Config
import pymysql

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config['SECRET_KEY']



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
            else:
                user_authenticated = verify_secretary(email, int(identification_num))
                if user_authenticated == False:
                    user_authenticated = employee_login_helper(email, identification_num)
                    if user_authenticated:
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
def secretary_home():
    return render_template('secretary_home.html')

@app.route('/coordinator_home')
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
def add_employee():
    if request.method == 'POST':

        open = not verify_employee(request.form.get('employee_id'))
        if not open:
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
@app.route('/delete_employee')
def delete_employee():
    return render_template('delete_employee.html')

# Build & Implement
# Get the employee ID
#         Employee email
#         Program ID
#         Program Name
@app.route('/enroll_employee')
def enroll_employee():
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


@app.route('/view_health_metric')
def view_health_metric():
    con = get_db_connection()
    try:
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
        return render_template('view_health_metric.html', health_metrics=health_metrics)
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template('view_health_metric.html', health_metrics=[])
    finally:
        con.close()


@app.route('/create_health_metric', methods=['GET', 'POST'])
def create_health_metric():
    """
    Route to allow wellness coordinators or secretaries to create health metrics for employees.
    """

    if request.method == 'POST':
        # Get the combined input for employee name or ID
        employee_name_or_id = request.form.get('employee_name_or_id')

        if not employee_name_or_id:
            flash("Please provide an employee name or ID.")
            return render_template('create_health_metric.html')

        # Determine if input is numeric (ID) or a string (name)
        con = get_db_connection()
        try:
            with con.cursor() as cursor:
                if employee_name_or_id.isdigit():
                    # Input is an ID
                    query = "SELECT * FROM employee WHERE employee_id = %s"
                    cursor.execute(query, (employee_name_or_id,))
                else:
                    # Input is a name
                    query = "SELECT * FROM employee WHERE fname LIKE %s OR lname LIKE %s"
                    cursor.execute(query, (f"%{employee_name_or_id}%", f"%{employee_name_or_id}%"))

                employee = cursor.fetchone()

                if not employee:
                    flash("No employee found matching the provided name or ID.")
                    return render_template('create_health_metric.html')

                # Extract the employee ID from the found record
                employee_id = employee['employee_id']

                # Gather the health metric data from the form
                cholesterol = request.form.get('cholesterol_levels')
                resting_heart_rate = request.form.get('resting_heart_rate')
                systolic_bp = request.form.get('systolic_blood_pressure')
                diastolic_bp = request.form.get('diastolic_blood_pressure')
                bmi = request.form.get('bmi')

                # Validate the inputs (ensure numbers are valid where applicable)
                try:
                    cholesterol = float(cholesterol) if cholesterol else None
                    resting_heart_rate = float(resting_heart_rate) if resting_heart_rate else None
                    systolic_bp = int(systolic_bp) if systolic_bp else None
                    diastolic_bp = int(diastolic_bp) if diastolic_bp else None
                    bmi = float(bmi) if bmi else None
                except ValueError:
                    flash("Please enter valid values for health metrics.")
                    return render_template('create_health_metric.html')

                # Insert the health metric data into the database
                insert_query = """
                    INSERT INTO health_metrics (employee_id, cholesterol_levels, resting_heart_rate, 
                                                blood_pressure_systolic, blood_pressure_diastolic, bmi)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (employee_id, cholesterol, resting_heart_rate, systolic_bp, diastolic_bp, bmi))
                con.commit()

                flash("Health metrics successfully added for the employee.")
                return redirect(url_for('view_health_metric'))

        except Exception as e:
            print(f"An error occurred: {e}")
            flash("An error occurred while processing the request. Please try again.")
            return render_template('create_health_metric.html')
        finally:
            con.close()

    else:  # GET request: display the form to create health metrics
        return render_template('create_health_metric.html')


@app.route('/view_enrollment_list')
def view_enrollment_list():
    """
    Return list of all employees enrolled in a specific program.
    Employee fname, lname, department, and work email should be returned
    and displayed on a table

    Requirements: Program ID, Program Name
    """
    return render_template('view_enrollment_list.html')


# Maybe
@app.route('/view_department_breakdown')
def view_department_breakdown():
    """
    To Be built

    Requirements: DepartmentID

    Returns a list of all employees in the department.

    Optional Goal : 
        - return the names of the wellness programs that employees may be enrolled in                
    """

    return render_template('view_department_breakdown.html')

@app.route('/health_highlight')
def health_highlight():
    """
    
    Requirements : None

    Returns two employees who have shown exceptional
    Health improvements in their metrics.

    The employee fname, lname should be displayed.
    Select the metrics that have improved the most,
    and display the "before" and "after" metric. 
    
    ONLY the improved metric(s) should be displayed.

    Optional goals: 
        - Display the delta value for each improved metric
        - 

    """
    return render_template('health_highlight.html')

# DELETE
@app.route('/successful_program')
def successful_program():
    """
    
    Requirements : None

    Returns : Information program with significant 
              health improvements in enrolled employees

    Goals :  TBD

    """
    return render_template('successful_program.html')











# Create Connection
def get_db_connection():
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
        con.close()
    
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
