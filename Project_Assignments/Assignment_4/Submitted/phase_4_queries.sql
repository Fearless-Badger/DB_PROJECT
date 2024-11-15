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

-- query 1

SELECT distinct department_id, count(*)
FROM employee, participates_in, wellness_program
WHERE   participates_in.program_id = wellness_program.program_id 
	AND wellness_program.program_id = 203 
	AND participates_in.employee_id = employee.employee_id
GROUP BY department_id;


-- query 2

SELECT distinct wellness_program.program_id, count(*)
FROM wellness_program, participates_in, employee
WHERE 
	wellness_program.program_id = participates_in.program_id
AND participates_in.employee_id = employee.employee_id
GROUP BY program_id;

-- query 3

SELECT e.department_id, 
	   ROUND(AVG(h.blood_pressure_systolic), 2) AS avg_systolic,
	   ROUND(AVG(h.blood_pressure_diastolic), 2) AS avg_diastolic
FROM employee e
JOIN health_metrics h 
ON e.employee_id = h.employee_id
GROUP BY e.department_id;

-- query 4 

SELECT distinct fname, lname, work_email, phone_number, coordinated_by.program_id
FROM(
	SELECT *
    FROM employee
    WHERE `role` = 'coordinator'
	) AS contacts, 
wellness_program, coordinated_by
WHERE 
	wellness_program.program_id = coordinated_by.program_id
AND coordinated_by.employee_id  = contacts.employee_id;


-- query 5 (done)

SELECT fname as 'First Name', 
	   lname as 'Last Name', 
	   resting_heart_rate as 'Resting BPM', 
	   cholesterol_levels as 'Cholesterol', 
       blood_pressure_systolic as 'Sys', 
       blood_pressure_diastolic as 'DBP', 
       bmi as 'BMI'
FROM employee
LEFT JOIN health_metrics
ON employee.employee_id = health_metrics.employee_id
WHERE date_measured = (
	(SELECT MAX(date_measured) 
     FROM health_metrics, employee 
     WHERE health_metrics.employee_id = employee.employee_id)
     );

-- query 6 (done) finds employees who are not participating in any wellness programs

SELECT fname, lname, work_email
FROM employee
WHERE employee_id 
NOT IN (
SELECT employee_id
FROM participates_in
);

-- query 7 (done) Identifies employees who have shown imporvement in health metrics between the two most recent measurements

SELECT h1.employee_id, e.fname, e.lname,
       h1.bmi AS Latest_BMI, h2.bmi AS Previous_BMI,
       h1.resting_heart_rate AS Latest_Heart_Rate, h2.resting_heart_rate AS Previous_Heart_Rate
FROM health_metrics h1
JOIN health_metrics h2 ON h1.employee_id = h2.employee_id
JOIN employee e ON h1.employee_id = e.employee_id
WHERE h1.date_measured > h2.date_measured
AND h1.date_measured = (SELECT MAX(date_measured) FROM health_metrics WHERE employee_id = h1.employee_id)
AND h2.date_measured = (SELECT MAX(date_measured) FROM health_metrics WHERE employee_id = h2.employee_id AND date_measured < h1.date_measured)
AND (h1.bmi < h2.bmi OR h1.resting_heart_rate < h2.resting_heart_rate);

-- query 8 Identifies employees whose BMI, cholesterol levels, or blood pressure are outside of the normal range(unhealthy)

SELECT distinct e.fname, e.lname, h.bmi, h.cholesterol_levels, h.blood_pressure_systolic, h.blood_pressure_diastolic, h.date_measured
FROM employee e
JOIN health_metrics h ON e.employee_id = h.employee_id
WHERE (h.bmi < 18.5 OR h.bmi > 24.9)
   OR (h.cholesterol_levels > 200)
   OR (h.blood_pressure_systolic > 130 OR h.blood_pressure_diastolic > 90);








