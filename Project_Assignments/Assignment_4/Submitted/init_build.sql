START TRANSACTION;

USE employee_wellness;

-- Disable foreign key checks to avoid issues during table creation
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables (if they exist) to start fresh
DROP TABLE IF EXISTS coordinated_by;
DROP TABLE IF EXISTS participates_in;
DROP TABLE IF EXISTS health_metrics;
DROP TABLE IF EXISTS wellness_coordinator;
DROP TABLE IF EXISTS wellness_program;
DROP TABLE IF EXISTS employee;

-- Re-Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Create tables

CREATE TABLE employee (
    employee_id INT PRIMARY KEY, 
    fname VARCHAR(20),
    middle_initial CHAR(1),
    lname VARCHAR(50),
    `role` ENUM('worker', 'secretary', 'coordinator'),
    phone_number VARCHAR(20),
    department_id ENUM('sales', 'marketing', 'finance', 'operations'), -- (sales, marketing, finance, operations)
    work_email VARCHAR(30)
);

CREATE TABLE wellness_coordinator (
    employee_id INT PRIMARY KEY,
    area_of_expertise VARCHAR(20),
    coordinator_credentials VARCHAR(10),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE wellness_program (
    program_id INT PRIMARY KEY,
    employee_id INT,
    end_date DATE,
    program_name VARCHAR(20),
    start_date DATE,
    `type` ENUM('bmi', 'blood_pressure', 'heart_rate', 'cholesterol'),
    FOREIGN KEY(employee_id) REFERENCES wellness_coordinator(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE participates_in (
    employee_id INT,
    program_id INT,
    enrollment_date DATE,
    PRIMARY KEY (employee_id, program_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (program_id) REFERENCES wellness_program(program_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);




CREATE TABLE health_metrics (
    employee_id INT,
    date_measured DATE,
    cholesterol_levels INT,
    resting_heart_rate INT,
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    bmi FLOAT,
    PRIMARY KEY (employee_id, date_measured),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE coordinated_by (
    employee_id INT,
    program_id INT,
    PRIMARY KEY (employee_id, program_id),
    FOREIGN KEY (employee_id) REFERENCES wellness_coordinator(employee_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,
    FOREIGN KEY (program_id) REFERENCES wellness_program(program_id)
        ON DELETE CASCADE -- We will not allow for a coordinator to be deleted from the database.
        ON UPDATE CASCADE -- It would delete all programs they manage. Updating their ID should be fine
);


COMMIT;

-- SHOW TABLES;