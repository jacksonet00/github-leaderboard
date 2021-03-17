# Github Leaderboard

## Developer Usage Documentation

[The project is setup with cookiecutter and docker so follow this link.](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally-docker.html)
The following instructions is the bare minimal to get things running. Important configuration instructions is included
in the link.

Important locations are `config` which contains top level information about Django like routing for homepage and
installed apps. `requirements` contain the Python packages that Docker uses. `compose` is for
Docker. `github_leaderboard` contains all the Django files that you would modify.

`db_sql_files` is for Jackson. They contain the SQL schema that he made.

### Setup docker environment from our project dependencies

1. Build the docker containers

   ```bash
   docker-compose -f local.yml build
   ```

2. If in production, we can easily change things by running the production setting files instead.

   ```bash
   docker-compose -f production.yml build
   ```

### Add a new dependency to the project

1. Save the dependency to the requirements file. Note we have two different files `local.txt` and `production.txt` for
   the two environments. Remember to add the right dependency to the right file

   ```bash
   # Local dependency
   echo "<DEPENDENCY_NAME>==<VERSION_NUMBER>" >> requirements/local.txt
   # Production dependency
   echo "<DEPENDENCY_NAME>==<VERSION_NUMBER>" >> requirements/production.txt
   ```

2. Add the dependency to Django by modifying the ```INSTALLED_APPS``` array within the ```config/settings/local.py```
   or `config/settings/production.py` file

### Run server @ localhost:8000

1. Running the local setup. This runs both Django and Postgres.

   ```bash
   docker-compose -f local.yml up
   ```

2. If in production, we can run it easily as well. This runs additional things for running things in production
   environment.

   ```bash
   docker-compose -f production.yml up
   ```

### Manage database from admin panel

1. Ensure server is running
2. Add a superusername with the `manage.py` as detailed below. Since you are running local Postgres instances, you add
   your own superuser identity.
3. Visit ```localhost:8000/admin``` and login with that.

### Modify tables from ```github_leaderboard/app/models.py```

1. Update schema
2. Ensure server is not running
3. Create migrations for new schema

   ```bash
   docker-compose -f local.yml run --rm django python manage.py makemigrations
   ```

4. Migrate database

   ```bash
   docker-compose -f local.yml run --rm django python manage.py migrate
   ```

If typing out the docker command is a pain, just alias
with `alias docker_django="docker-compose -f local.yml run --rm django python manage.py"`

### Create new database administrator account

1. Create a new superuser

   ```bash
   docker-compose -f local.yml run --rm django python manage.py createsuperuser
   ```

2. Log in through the admin panel

### Adding github auth

1. Go to admin page and add a "social application"

2. Add the client id and secret key from the Discord into the social application with provider github.

## Project Design Documentation

### User table explaination:

Django provides a default User table in the database which automatically integrates with authorization and the admin
panel. We will use this User for our app, but extend it to add additional functionality such as GitHub info and roles.
These users are represented by the ```ExtendedUser``` class which has a One-to-One relationship with the default User.
