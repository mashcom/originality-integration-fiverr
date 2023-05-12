# How install the application

<p>Here are the step-by-step instructions on how to install a Django application from GitHub using Markdown language:</p>

**1. Clone the GitHub repository to your local machine using the following command:**

`git clone https://github.com/username/repository.git
`
Replace "username/repository" with the name of the repository you want to clone.

**2. Create a virtual environment for your Django application.**

 You can use the following command to create a new virtual environment using Python 3:

`python3 -m venv myenv`


Replace "**myenv**" with the name you want to give your virtual environment.

**3. Activate the virtual environment by running the following command:**

`source myenv/bin/activate
`

**4. Install the required packages for the Django application.**

You can find the required packages in the _requirements.txt_ file in the root directory of the repository. Use the following command to install them:

`pip install -r requirements.txt`


**5. Set up the database by running the following commands:**

Please ensure that you have MySQL version 8 is running and add the required mysql settings on the **originality_project.settings.py** file

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'database_name',
                'USER': 'database_username',
                'PASSWORD': 'database_password',
                'PORT': 'database_3306',
            }
        }


`python manage.py makemigrations`

`python manage.py migrate`

**6. Create a superuser for the Django application by running the following command:**


`python manage.py createsuperuser`

Follow the prompts to set a username and password for the superuser.

**7. Run the Django application by running the following command:**

`python manage.py runserver
`
Open a web browser and navigate to **http://127.0.0.1:8000/admin/** to access the Django admin panel. Log in using the username and password you set for the superuser in step 6.