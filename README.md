# Quick Setup

    pip install -r requirements.txt
    python manage.py migrate
    python manage.py runserver
    
    npm install && node_modules/.bin/grunt
    
Visit http://localhost:8000/


# Release workflow

1. clean your workspace (the output of `git status` should be empty)
2. checkout the master branch and update it
3. run `make release-patch`, `make release-feature` or `make release-breaking`
4. describe your changes in the `git tag` message
5. in case of problems: discard your last commit and stop reading here
6. push your updated master branch (`git push ???`) and push the tags (`git push --tags`)
7. deploy the updated master branch on the target host: `make deploy-git`


# Database setup

The preconfigured database is a local sqlite file.
For production deployment you should use a database server.

## PostgreSQL

The following statement creates a suitable database including proper collation settings:

    CREATE USER stadtgestalten with password 'PUT RANDOM NOISE';
    CREATE DATABASE stadtgestalten WITH ENCODING 'UTF8' LC_COLLATE='de_DE.UTF8' LC_CTYPE='de_DE.UTF8' TEMPLATE=template0 OWNER stadtgestalten;

The above command requires the locale 'de_DE.UTF8' in the system of the database server.
