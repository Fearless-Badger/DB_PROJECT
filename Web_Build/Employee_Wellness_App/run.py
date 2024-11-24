"""This file is used to run the Flask application.
It imports the app object from the app.py file and starts the Flask server.
"""

from app import app

# Run this file to start the app
print("Starting Flask...")

if __name__ == '__main__':
    app.run(debug=True)

# Ensure the file ends with a newline
