HOW TO SETUP AND VIEW WEBPAGE:

    1. REQUIREMENTS & SETUP:

    python 3.12.2, from python.org. Not MSYS or some linux fashioned python install.

    MySQL installed in full, with a DB host, username, and password ready to be configured


    2. Initialize VENV: 

    This step is kinda optional, but I like to be safe. I dont want to deal with package, dependency, or OS problems
    Make sure your python install is geared towards windows (like python.org install)
    I recommend setting up a virtual environment, but its not necessary if you know for a fact that you also have python 3.12.2

    If you have other versions of python installed, take them off your environment variable 'PATH'  

        If you use VSCODE like me, then its easy

        a)     SHIFT + CTRL + P -->  
               "Python: Select Intrepreter" --> 
	           "Python 3.12.2 ('venv':venv) .\venv\Scripts\python.exe      Recommended" 

	            ----- (Recommended or Workspace works) -----

        b)   Now when you hover over 'pwsh' in the top right of the terminal, you will see "Show Environment Contributions"

            The contents should include 

            """## Extension: ms-python.python

                  Activated environment for `.\.venv\Scripts\python.exe`"""


    I decided to include the batch file so you can look at its contents and see the commands that I used.


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

    4. Run the 'run.py' file in the 'Employee_Wellness_App' folder
       Next follow the link provided in the cmd propmt

    5. Test contributions on staging branch, or your own branch.