# Project Overview

This application is designed to be a plugin to an existing employee portal. The plugin is used to facilitate the management of "wellness programs", which are meant to improve the physical health of the employees participating in the programs. There are 3 roles, where more priviliged roles are granted more power. For example, "Coordinators" may create programs, whereas "Workers" may only enter their health metrics into the database. 

# Database
The database is a MySQL database, hosted on AWS RDS. The database design has been normalized. There is no ORM abstraction. Raw SQL queries are used to interact with the database. The package PyMySQL protects against SQL injection attacks.


# Flask application