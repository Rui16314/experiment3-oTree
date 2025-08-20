# ECON3310 oTree Project

This is a full oTree project ready for GitHub + Heroku.

## Run locally
```
pip install -r requirements.txt
otree devserver
```
Visit http://localhost:8000

## Deploy to Heroku
```
heroku create econ3310-risk
heroku buildpacks:set heroku/python -a econ3310-risk
heroku addons:create heroku-postgresql:hobby-dev -a econ3310-risk
heroku config:set OTREE_ADMIN_PASSWORD=YourStrongPassword OTREE_AUTH_LEVEL=STUDY OTREE_PRODUCTION=1 -a econ3310-risk
git push https://git.heroku.com/econ3310-risk.git main
heroku run otree migrate -a econ3310-risk
heroku open -a econ3310-risk
```
