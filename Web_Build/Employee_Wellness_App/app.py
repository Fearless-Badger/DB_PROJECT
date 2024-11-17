#Import Flask, Config file and PyMySQL
from flask import Flask, render_template, request, redirect, url_for, flash, session
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
                print("Failed at line 67 in verify_secretary")
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
    





#START HERE
@app.route('/', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        identification_num = request.form.get('ID Number')
        email = request.form.get('email-address')
        credentials = request.form.get('credentials')

        is_coordinator = False
        user_authenticated = False

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
        else:
            flash("You must provide your ID number and email address")
            return redirect(url_for('login'))

        #session['user'] = 0 # replace with role for employee, if using sessions


        if user_authenticated and is_coordinator:
            return render_template('coordinator_home.html')
        elif user_authenticated:
            return render_template('secretary_home.html')
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

# Not yet implemented
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
@app.route('/add_wellness_program')
def add_wellness_program():
    return render_template('add_wellness_program.html')


@app.route('/view_health_metric')
def view_health_metric():
    """
        To be built

        Return data meant to fill a table
        with ALL health metrics for the specified employee

        Requirements: Get the employee name and employee ID number
    """
    return render_template('view_health_metric.html')


@app.route('/create_health_metric')
def create_health_metric():
    """
    DO NOT BUILD - Planning on DELETING this page
    """
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

@app.route('/successful_program')
def successful_program():
    """
    
    Requirements : None

    Returns : Information program with significant 
              health improvements in enrolled employees

    Goals :  TBD

    """
    return render_template('successful_program.html')

