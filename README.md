# HR Wellness Program Portal

## Project Overview

This application serves as a plugin for an existing employee portal, designed to support the management of workplace **wellness programs** aimed at improving employees' physical health.

It supports three user roles with hierarchical permissions:

- **Workers** – Can enter their own health metrics.
- **Secretaries** – Can manage user data and view reports.
- **Coordinators** – Have full administrative access, including the ability to create and manage programs.

---

## Database

The backend uses a **MySQL** database hosted on **AWS RDS**.

- The schema is **normalized** to ensure efficient data storage and consistency.
- No ORM abstraction is used; all database interaction is done through **raw SQL queries**.
- **PyMySQL** is used to connect to the database securely and helps protect against SQL injection attacks.

---

## Flask Application

The web application is built with **Flask** and supports multiple pages based on user roles.

#### User Authentication and Authorization

- Upon login, users are redirected to a personalized landing page.
- A dynamic **navbar** is rendered based on the user’s permission level.

#### Role-Based Access Control

- Each route is protected with a **decorator** that checks the user’s role before allowing access.
- For example, the `/delete_employee` page is accessible only to Coordinators.

#### UI Structure

- A common **base template** is used across all pages with a shared navbar.
- Individual pages extend this base layout using Jinja templates.

---

#### Technologies Used

- Flask
- MySQL (AWS RDS)
- PyMySQL
- HTML/CSS (Jinja Templates)