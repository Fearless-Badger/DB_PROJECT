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
    role ENUM('worker', 'secretary', 'coordinator'),
    phone_number VARCHAR(20),
    department_id INT, 
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
    type ENUM('bmi', 'blood_pressure', 'heart_rate', 'cholesterol'),
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
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (program_id) REFERENCES wellness_program(program_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Insert data

-- Insert 20 employees
INSERT INTO employee (employee_id, fname, middle_initial, lname, role, phone_number, department_id, work_email)
VALUES
(101, 'John', 'A', 'Smith', 'worker', '555-0101', 101, 'john.smith@example.com'),
(102, 'Emma', 'B', 'Johnson', 'worker', '555-0102', 102, 'emma.johnson@example.com'),
(103, 'Michael', 'C', 'Williams', 'coordinator', '555-0103', 103, 'michael.williams@example.com'),
(104, 'Olivia', 'D', 'Brown', 'worker', '555-0104', 104, 'olivia.brown@example.com'),
(105, 'William', 'E', 'Jones', 'coordinator', '555-0105', 105, 'william.jones@example.com'),
(106, 'Sophia', 'F', 'Garcia', 'worker', '555-0106', 106, 'sophia.garcia@example.com'),
(107, 'James', 'G', 'Miller', 'coordinator', '555-0107', 107, 'james.miller@example.com'),
(108, 'Isabella', 'H', 'Davis', 'worker', '555-0108', 108, 'isabella.davis@example.com'),
(109, 'Benjamin', 'I', 'Rodriguez', 'worker', '555-0109', 109, 'benjamin.rodriguez@example.com'),
(110, 'Mia', 'J', 'Martinez', 'worker', '555-0110', 110, 'mia.martinez@example.com'),
(111, 'Jacob', 'K', 'Hernandez', 'worker', '555-0111', 111, 'jacob.hernandez@example.com'),
(112, 'Charlotte', 'L', 'Lopez', 'worker', '555-0112', 112, 'charlotte.lopez@example.com'),
(113, 'Ethan', 'M', 'Gonzalez', 'worker', '555-0113', 113, 'ethan.gonzalez@example.com'),
(114, 'Amelia', 'N', 'Wilson', 'worker', '555-0114', 114, 'amelia.wilson@example.com'),
(115, 'Alexander', 'O', 'Anderson', 'worker', '555-0115', 115, 'alexander.anderson@example.com'),
(116, 'Harper', 'P', 'Thomas', 'worker', '555-0116', 116, 'harper.thomas@example.com'),
(117, 'Daniel', 'Q', 'Taylor', 'worker', '555-0117', 117, 'daniel.taylor@example.com'),
(118, 'Evelyn', 'R', 'Moore', 'worker', '555-0118', 118, 'evelyn.moore@example.com'),
(119, 'Matthew', 'S', 'Jackson', 'worker', '555-0119', 119, 'matthew.jackson@example.com'),
(120, 'Abigail', 'T', 'Martin', 'worker', '555-0120', 120, 'abigail.martin@example.com');

-- Insert coordinators
INSERT INTO wellness_coordinator (employee_id, area_of_expertise, coordinator_credentials)
VALUES
(103, 'Fitness', 'CERTFIT'),
(105, 'Mindfulness', 'CERTMIN'),
(107, 'Nutrition', 'CERTNUT'),
(113, 'Wellness', 'CERTGEN');

-- Insert wellness programs
INSERT INTO wellness_program (program_id, employee_id, end_date, program_name, start_date, type)
VALUES
(201, 103, '2023-12-31', 'Fitness Challenge', '2023-09-01', 'bmi'),
(202, 105, '2023-12-31', 'Mindfulness Workshop', '2023-09-15', 'heart_rate'),
(203, 107, '2023-12-31', 'Nutrition Plan', '2023-09-30', 'cholesterol');

-- Insert participations in programs
INSERT INTO participates_in (employee_id, program_id, enrollment_date)
VALUES
(101, 201, '2023-09-05'),
(102, 201, '2023-09-06'),
(103, 201, '2023-09-07'),
(104, 201, '2023-09-08'),
(105, 202, '2023-09-16'),
(106, 202, '2023-09-17'),
(107, 202, '2023-09-18'),
(108, 202, '2023-09-19'),
(109, 203, '2023-10-01'),
(110, 203, '2023-10-02'),
(111, 203, '2023-10-03'),
(112, 203, '2023-10-04');

-- Assign coordinators to programs
INSERT INTO coordinated_by (employee_id, program_id)
VALUES
(103, 201),
(105, 202),
(107, 203),
(113, 201);

-- Insert health metrics with trends
INSERT INTO health_metrics (employee_id, date_measured, cholesterol_levels, resting_heart_rate, blood_pressure_systolic, blood_pressure_diastolic, bmi)
VALUES
(101, '2023-09-01', 180, 72, 120, 80, 24.5),
(101, '2023-10-01', 178, 71, 119, 79, 24.3),
(101, '2023-11-01', 176, 70, 118, 78, 24.1),

(102, '2023-09-01', 190, 75, 122, 82, 23.0),
(102, '2023-10-01', 189, 74, 121, 81, 22.9),
(102, '2023-11-01', 188, 73, 120, 80, 22.8),

-- Add the rest of the employee metrics
(103, '2023-09-01', 170, 70, 118, 78, 26.1),
(103, '2023-10-01', 169, 69, 117, 77, 26.0),
(103, '2023-11-01', 168, 68, 116, 76, 25.9),

(104, '2023-09-01', 160, 68, 115, 75, 22.5),
(104, '2023-10-01', 160, 68, 115, 75, 22.5),
(104, '2023-11-01', 160, 68, 115, 75, 22.5),

(105, '2023-09-01', 200, 78, 125, 85, 28.0),
(105, '2023-10-01', 198, 76, 123, 83, 27.8),
(105, '2023-11-01', 196, 74, 121, 81, 27.6);

-- Continue inserting data for other employees similarly, with most showing slight improvement
-- Some employees will show constant metrics without improvement

COMMIT;

-- SHOW TABLES;