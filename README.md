# Project: Item Catalog

This web app manages a database of categorized items. Any user may view the catalog. Authorized users may create new items as well as edit and delete items they have created. OAuth2 authentication is provided by Facebook and Google.

### Requirements
* Python >= 2.7
    * sqlalchemy
    * flask
    * oauth2client
    * httplib2
    * requests
* Google Cloud Platform
* Facebook for Developers

### Included Files
* app.py - *The view for the web app*
* db.py - *The model for the web app*
* dry.py - *A helper script containing frequently used custom methods*
* create_db_categories.py - *A helper script which generates a database with the given categories*
* create_test_db.py - *A helper script which generates a database complete with items, categories, and a user for testing*
* fb_client_secrets.json - *Empty JSON for storing Facebook credentials*
* STATUS.md - *Indicates the current status of the project*
* README.md
* templates
    * catalog.html - *HTML template for rendering the main/full catalog page*
    * category.html - *HTML template for rendering a category page*
    * documentation.html - *HTML template for rendering the API documentation*
    * error.html - *HTML template for alerting the user of an error*
    * header.html - *HTML header/navbar snippet for inclusion in other templates*
    * item_create.html - *HTML template for creating an item*
    * item_delete.html - *HTML template for deleting an item*
    * item_update.html - *HTML template for updating an item*
    * item.html - *HTML template for rendering an item page*
    * login.html - *HTML template for rendering the login page*
* static
    * css
        * styles.css - *Contains style for HTML templates*
    * images
        * icons
            * catalog.png - *Icon for "Full Catalog" link*
            * create.png - *Icon for "Create Item" link*
    * scripts
        * image_check.js - *jQuery for rendering image preview and validating image url*

### How To Use
* Download/install all requirements
    * Install python
    * Install python modules
        * sqlalchemy
        * psycopg2
        * flask
        * oauth2client
        * httplib2
        * requests
    * Install postgresql
* Setup Postgresql
    * Create role and database with the following commands:
        * sudo -u postgres createuser -d catalog
        * sudo -u postgres psql
            * \password catalog
                * udacity4life
            * create database "catalog" owner "catalog";
            * \q
* Setup Google Authentication
    * Sign up or login to Google Cloud Platform
    * Create a new project
    * Create credentials
        * Fill out the "OAuth Consent" for your project
        * Go to the "Credentials" page for your project
        * Click the dropdown menu labeled "Create credentials"
        * Choose the "OAuth Client ID" option
        * On the next screen select "Web application"
        * In the "Authorized JavaScript origins" enter the domain you will be running the application from. If you are running it on your local machine enter "http://localhost:8000"
        * In the "Authorized redirect URIs" enter the domain you will be running the application from with the paths "/oauth2callback" and "/gconnect". If you are running it on your local machine enter "http://localhost:8000/oauth2callback" and "http://localhost:8000/gconnect"
        * Click "Create"
        * Download your client secrets JSON file from the "Credentials" page
        * Rename the file "client_secrets.json" and move it into the directory containing app.py
* Setup Facebook Authentication
    * Sign up or login to Facebook for Developers
    * Create new app
    * Create a test app from your new app
    * Setup Facebook Login
        * From the dashboard click "Setup" for Facebook Login
        * On the next page select "Web" as the platform
        * On the next page enter the domain you will be running the app from in "Site URL". If you are running the app from your local machine enter "http://localhost:8000"
        * Click "Save"
        * Copy your "App ID" into fb_client_secrets.json
        * Copy your "App Secret" into fb_client_secrets.json (You can find your App Secret in Basic Settings)
* Setup the database
    * Edit the 'categories' list in create_db_categories.py with the categories you would like
    * Run create_db_categories.py to populate the database
* Run app.py

### Use Options
If you would like to test the app with a full database run create_test_db.py instead of create_db_categories.py

### Database Structure
* User
    * id (integer) - *Primary Key*
    * name (string) - *The user's name as provided by authentication*
    * email (string) - *The user's email address as provided by authentication*
* Category
    * id (integer) - *Primary Key*
    * name (string) - *The name of the category*
* Item
    * id (integer) - *Primary Key*
    * name (string) - *The name of the item*
    * description (string) - *A description of the item*
    * image_url (string, nullable) - *The url for an image relating to the item*
    * category_id (integer) - *The id of category containing this item*
    * category (relationship) - *The category containing this item*
    * user_id (interger) - *The id of the user that created this item*
    * user (relationship) - *The user that created this item*

### Contributions:
* Lorenzo Brown
