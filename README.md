# How install the application

**Prerequisites**

Ensure that Python 3 and pip are installed on your system. You can check their installation by running the following commands in your terminal or command prompt:

`python --version`


`pip --version`


Make sure you have Git installed. Run the following command to verify:

`git --version`

## **# Steps to install**


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


# **Configure Social Configuration**

To add a social app on the Django admin interface using, follow these steps:


**1. Create a Social App:** 

Open your Django project's admin interface by accessing the URL **http://127.0.0.1:8000/admin/**. Log in with your superuser credentials.

**2. Navigate to Social Applications:** 

In the admin interface, find the section labeled **"SOCIAL ACCOUNT"** and click on "Social Applications". This section allows you to manage the social apps configured for your Django project.

**3. Add a Social Application:** 

Click on the **"ADD SOCIAL APPLICATION"** button to create a new social app.

**4. Fill in the required details:** 

In the **"Add Social Application"** form, you need to provide the following information:

**Provider:** Select the **Google**  from the drop-down menu

**Name:** Enter a descriptive name for the social app.

**Client ID:** Enter the client ID or API key provided by the social provider.

**Secret Key:** Enter the secret key or API secret provided by the social provider.

**Sites:** Select the site(s) for which this social app should be active.


**5. Save the social app:** 

Once you have filled in the required details, click on the **"SAVE"** button to create the social app.

**6. Test the social app:** 

You can now test the social app integration by navigating to the login page of your Django project and clicking on the social provider's login button (e.g., "Login with Facebook"). It should redirect you to the social provider's authentication page.

**7. Manage additional settings (optional)**

Django-allauth provides various additional settings for social apps, such as specifying the desired scopes, setting up callback URLs, and customizing the behavior of social authentication. You can refer to the Django-allauth documentation for more details on these settings.

# **Configure Google Classroom**

To generate Google Classroom API credentials file, you need to create a new project in the Google Cloud Console, enable the Google Classroom API, and then create credentials for your project. Here's a step-by-step guide on how to do it:

1. Go to the Google Cloud Console (console.cloud.google.com) and sign in with your Google account.

2. Click on the project drop-down and select "New Project" to create a new project. Enter a name for your project and click "Create."

3. Once your project is created, make sure it's selected in the project drop-down.

4. In the Cloud Console, click on the menu icon (☰) in the upper-left corner, then navigate to "APIs & Services" → "Library."

5. In the library, search for "Google Classroom API" and click on it when it appears.

6. On the Google Classroom API page, click the "Enable" button to enable the API for your project.

7. After enabling the API, go back to the menu and navigate to "APIs & Services" → "Credentials."

8. On the Credentials page, click on the "Create credentials" button and select "OAuth client ID."

9. Choose "Web application" as the application type.

10. Enter a name for your OAuth 2.0 client ID (e.g., "Google Classroom API Credentials").

11. Under "Authorized JavaScript origins," enter the URL where your application will be hosted. If you're developing locally, you can enter "http://127.0.0.1:8000".

12. Under "Authorized redirect URIs," enter the redirect URL where users will be sent after granting access. This will typically be the URL of your application's authentication page. For example, you can use "http://127.0.0.1:8000/auth/google/callback".

13. Click the "Create" button to create the OAuth client ID.

14. On the credentials page, you will see your newly created client ID listed. Click on the download icon on the right-hand side of the client ID row to download the JSON file. This file contains your credentials and will be named "credentials.json" by default.

15. Add the credentials details on the Google Classroom configuration page **http://127.0.0.1/config/google_classroom** 

_**_`Important ** Ensure that you enable the Google Drive API so that the Google Classroom will be able to attach files to Google Drive `_**_

# **API documentation:**

#### **API Endpoint**

**POST** /api/v1/report

Use this endpoint to create a new report.

#### **Request Headers**

**Content-Type :**	The content type of the request body. (e.g., application/json)
**Authorization :**	The authorization token for accessing the API.


#### **Request Body**

The request body should contain the necessary data to create the resource. The structure and fields required may vary depending on the specific API endpoint. Provide a detailed description of the expected request body, including any required or optional fields, their data types, and any validation rules.

**Example Request Body:**

The request should provide json content

    `{
      "OriginalityFileId": "Unique Identifier of Similarity Report",
      "Grade": "Number",
      "file": "Base64 encoded file",
    }`

**Response:**

Response Codes
<table>
<tr>
    <td>200</td>
    <td>OK</td>
    <td>The request was successful, and the resource was created.</td>
</tr>
<tr>
    <td>400</td>
    <td>Bad</td>
    <td>Request	The request body was invalid or missing required fields.</td>
</tr>
<tr>
    <td>401</td>
    <td>Unauthorized</td>
    <td>The request lacks valid authentication credentials.</td>
</tr>
<tr>
    <td>500</td>
    <td>Internal Server Error</td>
    <td>An unexpected error occurred on the server.</td>
</tr>

</table>


**Response Body**

The response body will contain a message if applicable. Make sure you pay attention to the **Response Code** to determine if a request was successful or not 

**Example Response Body (Success):**

    `{
        "Id": originality report id, 
        "Message": "Report transfer successful"
    }`
    
**Example Response Body (Failure):**

    `{
        "Message": "Report transfer successful"
    }`