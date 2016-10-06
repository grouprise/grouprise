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
