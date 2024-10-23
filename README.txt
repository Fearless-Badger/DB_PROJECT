1. REQUIREMENTS & SETUP:

python 3.12, from python.org. Not MSYS or some linux fashioned python install.

MySQL installed in full, with a DB host, username, and password ready to be configured


2. Initialize VENV: 


 
If you have some other version of python, you can edit venv_setup.bat to match your python version. 
Make sure your python install is geared towards windows (like python.org install)

I recommend setting up a virtual environment, but its not necessary if you know for a fact that you also have python 3.12.2

If you have other versions of python installed, take them off your environment variable 'PATH'

    If you use VSCODE like me, the following applies to you

        SHIFT + CTRL + P -->  "Python: Select Intrepreter" --> 
	"Python 3.12.2 ('venv':venv) .\venv\Scripts\python.exe      Recommended" 
	----- (Recommended or Workspace works) -----

        Now when you hover over 'pwsh' in the top left of the terminal, you will see "Show Environment Contributions"

        The contents should include 

        """## Extension: ms-python.python

           Activated environment for `.\.venv\Scripts\python.exe`"""

Let me know if there are problems with the .bat file, if you decide to use it.

3. Create local config file

    Create a 'config.py' file within the "Employee_Wellness_App" folder. It should look like:

-------------------------------------------------------------------
    class Config:
        SECRET_KEY = ''                   # Use Secure key
        DB_HOST = ''                      # DB host name
        DB_USER = ''                      # Your username
        DB_PASSWORD = ''                  # Your password
        DB_NAME = 'employee_wellness'     # DB Name
-------------------------------------------------------------------




