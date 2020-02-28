# Common Workflows

## Normal Development Workflow

Normal development is driven by what is in github, so most engineers
would only need access to that, which helps separate duties and reduce the
attack surface for compromised accounts.  It also provides a good audit trail
for all changes, and with protected branches and good tests, makes sure that changes
have oversight and will work.

  * You develop locally, pushing changes up to your own feature/fix branch in github
    and building/running tests locally.  If you are developing code to address
    compliance needs, be sure to update the compliance documentation.
  * Once you have something that is tested and worthy of going out, you can Pull Request
    (PR) it into the dev branch, where it will be automatically deployed to the dev
    version of the app in cloud.gov and have it's tests run against it.
  * When you have your changes in a releasable form, your changes should be PR'ed
    into the staging branch, where they will be approved by another person, and then
    they will automatically be rolled out into the staging version of the app in cloud.gov.
  * After staging has been validated through UAT or other automated testing, your 
    changes should be PR'ed into the master branch and approved by somebody else,
    where they will be automatically rolled out into production.
  * **NOTE:**  The prototype app will run db migrations before doing the promotion to 
    production, so make sure that your old version of the app is forward-compatible
    one release, or you might cause problems with the old version of the app
    accessing/adding data using the old code/schema/etc.  This is something that
    you could change in the circleci pipelines or your app code.

## Logging/Debugging

Logs can be watched either by using the [cloud.gov log viewer](https://logs.fr.cloud.gov/),
or by using the [commandline tools](https://cloud.gov/docs/deployment/logs/).

Debugging can be done through an ssh connection to the app, again using the
[cloud.gov commandline tools](https://cloud.gov/docs/management/using-ssh/).

## Connecting to Databases

Most of the time, you will want to make changes to the database through your
app's ORM schema update or migration system, so that it is repeatable and documented.
However, sometimes you need to debug why queries are slow or look at data that is
causing problem with your app.  When that happens, you will need to connect directly
to the db.

First, you will need to install the [cf connect-to-service plugin](https://github.com/18F/cf-service-connect).

After this is installed, you can get into the database in cloud.gov by doing
`cf connect-to-service tanf tanf-db`.
This will give you a postgres psql prompt, and you can do whatever queries you want.
The `upload_*` tables are what contain all the data.

If you would like to connect a GUI client to the database, then you can run
`cf connect-to-service --no-client tanf tanf-db`, and it will supply you with the host/port,
username/password, and database name for you to configure your client to use. 

Note:
the credentials will only work and the database will only be accessible while
you have your authenticated `connect-to-service` session going.

## Secrets Rotation Workflow

The main secrets in the system are the login.gov OIDC key, as well
as the deploy credentials.

### Update login.gov OIDC key

To update the login.gov OIDC key, you will need to:
- Schedule some downtime with your users, or do it in the off hours at least.
- Check the code out and cd into the repo.
- Be sure your cf tools are pointing at the proper org/space with
  `cf target -o YOURORG -s YOURSPACE`.
- Run `CGHOSTNAME=tanf-prototype-HOSTNAME ./deploy-cloudgov.sh regenjwt`.
  Make sure that HOSTNAME is set to the proper hostname for the environment you
  are in.
- Copy the contents of the `cert.pem` file (also emitted during the regenjwt operation)
  into the login.gov dashboard n the app for the proper environment.

This will regenerate the OIDC key/cert and plug it into the cloud.gov
application.  It will restart the app and until you plug that cert into
login.gov, authentication will not work.  This is why it's good to
schedule downtime.


### Update deploy credentials

To update the deployment credentials, you will need to:
- Be sure your cf tools are pointing at the proper org/space with
  `cf target -o YOURORG -s YOURSPACE`.
- Delete the existing deploy keys: `cf delete-service-key tanf-keys deployer; cf delete-service tanf-keys`
- Run `CGHOSTNAME=tanf-prototype-HOSTNAME ./deploy-cloudgov.sh setup` to create a new deploy key.
  Make sure that HOSTNAME is set to the proper hostname for the environment you
  are in.
- Get the deploy keys from `cf service-key tanf-keys deployer` and edit the
  Environment Variables in the CircleCI project to change the `CF_PASSWORD_XXX`
  and `CF_USERNAME_XXX` variables to add them in.  XXX should be `DEV` or
  `PROD` or whatever your environment is.

