# Github Leaderboard

## Developer Usage Documentation

### Setup virtual environment from our project dependencies<br>
   1. Start a virtual environment
      ```
      python3 -m venv venv
      ```
   2. Activate the virual environment in your shell (.vscode/settings.json will automatically set this as your python interpreter for vs code)
      ```
      source venv/bin/activate
      ```
   3. Ensure your environment is up to date with current dependencies
      ```
      pip3 install -r requirements.txt
      ```

### Add a new dependency to the project

   1. Ensure the virtual environment is activaetd in your shell and the dependencies are up to date
      ```
      source venv/bin/activate
      pip3 install -r requirements.txt
      ```
   2. Install the dependency within the virtual environment
      ```
      pip3 install <dependency_name>
      ```
   3. Save the dependency to the requirements file
      ```
      pip freeze > requirements.txt
      ```
   4. Add the dependency to Django by modifying the ```INSTALLED_APPS``` array within the ```github_leaderboard/settings.py``` file

### Run server @ localhost:8000
   ```
   python3 manage.py runserver
   ```
### Manage database from admin panel
   1. Ensure server is running
   2. Visit ```localhost:8000/admin```
   3. Login using the provided credentials pinned in ```#backend```

### Modify tables from ```app/models.py```
   1. Update schema
   2. Ensure server is not running
   3. Create migrations for new schema
      ```
      python3 manage.py makemigrations
      ```
   4. Migrate database
      ```
      python3 manage.py migrate
      ```
### Create new database administrator account
   1. Create a new superuser
      ```
      python3 manage.py createsuperuser
      ```
   2. Log in through the admin panel

## Project Design Documentation

### User table explaination:
   Django provides a default User table in the database which automatically integrates with authorization and the admin panel. We will use this User for our app, but extend it to add additional functionality such as GitHub info and roles. These users are represented by the ```ExtendedUser``` class which has a One-to-One relationship with the default User.