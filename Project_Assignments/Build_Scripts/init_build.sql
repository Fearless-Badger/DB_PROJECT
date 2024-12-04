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
DROP TABLE IF EXISTS departments;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Create departments table first
CREATE TABLE departments (
    department_id VARCHAR(50) PRIMARY KEY,
    department_name VARCHAR(100)
);

-- Create employee table
CREATE TABLE employee (
    employee_id INT PRIMARY KEY, 
    department_id VARCHAR(50),
    fname VARCHAR(20),
    middle_initial CHAR(1),
    lname VARCHAR(50),
    `role` ENUM('worker', 'secretary', 'coordinator'),
    phone_number VARCHAR(20),
    work_email VARCHAR(30),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- Create wellness_coordinator table
CREATE TABLE wellness_coordinator (
    employee_id INT PRIMARY KEY,
    area_of_expertise VARCHAR(20),
    coordinator_credentials VARCHAR(10),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create wellness_program table
CREATE TABLE wellness_program (
    program_id INT PRIMARY KEY,
    employee_id INT,
    end_date DATE,
    program_name VARCHAR(20),
    start_date DATE,
    `type` ENUM('bmi', 'blood_pressure', 'heart_rate', 'cholesterol'),
    FOREIGN KEY (employee_id) REFERENCES wellness_coordinator(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create participates_in table
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

-- Create health_metrics table
CREATE TABLE health_metrics (
    health_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    date_measured DATE,
    cholesterol_levels INT,
    resting_heart_rate INT,
    blood_pressure_systolic INT,
    blood_pressure_diastolic INT,
    bmi FLOAT,
    UNIQUE KEY (employee_id, date_measured), -- Use UNIQUE instead of PRIMARY
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Create coordinated_by table
CREATE TABLE coordinated_by (
    employee_id INT,
    program_id INT,
    PRIMARY KEY (employee_id, program_id),
    FOREIGN KEY (employee_id) REFERENCES wellness_coordinator(employee_id)
        ON DELETE NO ACTION
        ON UPDATE CASCADE,
    FOREIGN KEY (program_id) REFERENCES wellness_program(program_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

COMMIT;

SHOW TABLES;
