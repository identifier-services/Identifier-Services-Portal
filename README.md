# Identifier Services Portal


## First time setup

1. Clone the repo

   ```
   $ git clone https://github.com/identifier-services/Identifier-Services-Portal 
   $ cd Identifier-Services-Portal 
   ```

2. Configure environment variables

   Make a copy of [ids.env.sample](ids.env.sample) and rename it to
   `ids.env`. Configure variables as necessary.

   Required environment variables:

   - AGAVE_CLIENT_KEY  
   - AGAVE_CLIENT_SECRET  
   - AGAVE_SUPER_TOKEN

   Optional:

   - AGAVE_TENANT_BASEURL  (default: https://agave.iplantc.org/)
   - DJANGO_DEBUG (default: False)

3. Installing

    Install requirements:
    (Would suggest doing this in a virtual environment)

    ```
    $ pip install -r requirements.txt
    ```

4. Migrating

    Run migrations:
    ```
    $ python manage.py migrate
    ```

## Running

1. From project directory (same directory as manage.py):

    ```
    $ source ids.env
    $ python manage.py runserver
    ```

2. Open in browser

   Navigate to [http://localhost:8000](http://localhost:8000) in your browser.
