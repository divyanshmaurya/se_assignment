# Django Polls on AWS Elastic Beanstalk

The polls application from the official Django tutorial
([parts 1–4](https://docs.djangoproject.com/en/6.1/intro/tutorial01/)),
configured for deployment to AWS Elastic Beanstalk.

- Django 6.1 (requires Python 3.12+)
- Project: `mysite`, app: `polls`
- Pages: `/polls/` (index), `/polls/<id>/` (vote), `/polls/<id>/results/`, `/admin/`
- The bare domain `/` redirects to `/polls/`

## Project layout

```
.ebextensions/django.config    Elastic Beanstalk settings + deploy commands
mysite/                        Django project (settings, urls, wsgi)
polls/                         Polls app (models, views, urls, templates)
polls/fixtures/sample_polls.json  Sample questions loaded on every deploy
requirements.txt               Python dependencies (EB installs these)
manage.py
```

## Run locally

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata sample_polls   # optional sample questions
python manage.py createsuperuser         # optional, for /admin/
python manage.py runserver
```

Open http://127.0.0.1:8000/polls/. Run the tests with `python manage.py test polls`.

## Deploy to Elastic Beanstalk

Prerequisites:

1. An AWS account, and an IAM user with access keys. Configure them on your own
   machine with `aws configure` (or let `eb init` prompt you). **Never commit
   keys to this repository.**
2. The EB CLI: `pip install awsebcli`
   ([install guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html)).

From the repository root:

```bash
# 1. Initialize the EB application (Django 6.1 needs a Python 3.12+ platform).
eb init -p python-3.13 swe1-app --region us-east-1
eb init                 # optional: re-run to set up SSH access to the instance

# 2. Create a single-instance environment (free-tier friendly, no load balancer).
eb create swe1-app-env --single --instance_type t3.micro

# 3. Give Django a real secret key (generate one, then set it on EB).
python -c "import secrets; print(secrets.token_urlsafe(50))"
eb setenv DJANGO_SECRET_KEY=<paste-the-generated-value>

# 4. Open the app, then add /polls/ to the URL.
eb open
```

The app is then live at `http://swe1-app-env.<id>.us-east-1.elasticbeanstalk.com/polls/`
(`eb status` shows the exact CNAME).

To ship later changes: commit them, then run `eb deploy` (the EB CLI deploys the
latest git commit).

### Elastic Beanstalk configuration

`.ebextensions/django.config`:

- Points EB at `mysite.wsgi:application` and sets `DJANGO_SETTINGS_MODULE`.
- Sets `DJANGO_DEBUG=False` so production runs with `DEBUG` off.
- Serves `/static` (admin CSS/JS) directly from nginx.

`.platform/scripts/setup_db.sh` runs `migrate`, loads the sample polls, runs
`collectstatic`, and gives the `webapp` user write access to the SQLite file.
It is called from both `.platform/hooks/predeploy` (`eb deploy`) and
`.platform/confighooks/predeploy` (configuration changes such as `eb setenv`),
because both can replace the app directory with a fresh copy that has no
database.

`ALLOWED_HOSTS` already includes `.elasticbeanstalk.com`, so any EB environment
domain works. For a custom domain, set `eb setenv DJANGO_ALLOWED_HOSTS=example.com`.

### Notes

- The database is SQLite on the instance. It is rebuilt (and re-seeded with the
  sample polls) on each `eb deploy` and `eb setenv`, so votes and admin users do not survive a
  redeploy. To use `/admin/` on EB: `eb ssh`, then
  `cd /var/app/current && sudo /var/app/venv/*/bin/python3 manage.py createsuperuser`.
- If the environment is "Degraded" because there is no default VPC, create one
  in the AWS VPC console (Actions → Create default VPC) and run `eb create` again.
- Useful commands: `eb status`, `eb health`, `eb logs` (500 errors are logged
  with their traceback in `web.stdout.log`).
- Set a billing alarm
  ([CloudWatch guide](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/monitor_estimated_charges_with_cloudwatch.html)),
  and run `eb terminate swe1-app-env` once the assignment has been graded.
