--  coordinated_by(employee_id, program_id;
--  participates_in(program_id, employee_id, end_date, program_name, start_date);
--  health_metrics( employee_id, date_measured, cholesterol_levels, resting_heart_rate, blood_pressure_systolic, blood_pressure_diastolic, bmi);
--  wellness_coordinator(employee_id, area_of_expertise, coordinator_credentials);
--  wellness_program( program_id, employee_id, end_date, program_name, start_date, type);
--  employee(employee_id, fname, middle_initial, lname, role, phone_number, department_id, work_email);
    
SELECT * FROM coordinated_by;

SELECT * FROM participates_in;

SELECT * FROM health_metrics;

SELECT * FROM wellness_coordinator;

SELECT * FROM wellness_program;

SELECT * FROM employee;

-- queries

-- query 1(done)

SELECT department_id, count(*)
FROM employee, participates_in, wellness_program
WHERE   participates_in.program_id = wellness_program.program_id 
	AND wellness_program.program_id = 203 
	AND participates_in.employee_id = employee.employee_id
GROUP BY department_id;


-- query 2(done)

SELECT wellness_program.program_id, count(*)
FROM wellness_program, participates_in, employee
WHERE 
	wellness_program.program_id = participates_in.program_id
AND participates_in.employee_id = employee.employee_id
GROUP BY program_id;

-- query 3(broken)

SELECT fname, lname, work_email, phone_number
FROM(
    SELECT *
    FROM employee, health_metrics -- , wellness_program
    WHERE date_measured = ((SELECT MAX(date_measured) FROM health_metrics, employee WHERE health_metrics.employee_id = employee.employee_id) AS SUB)
) AS SUP
LIMIT %s OFFSET %s;

SELECT MAX(date_measured) FROM health_metrics, employee WHERE health_metrics.employee_id = employee.employee_id;


-- query 4 (done)

SELECT fname, lname, work_email, phone_number, coordinated_by.program_id
FROM(
	SELECT *
    FROM employee
    WHERE `role` = 'coordinator'
	) AS contacts, 
wellness_program, coordinated_by
WHERE 
	wellness_program.program_id = coordinated_by.program_id
AND coordinated_by.employee_id  = contacts.employee_id
;










