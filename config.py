import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Blog configuration values.


class Config(object):
  DEBUG = False
  TESTING = False
  CSRF_ENABLED = True

  # The secret key is used internally by Flask to encrypt session data stored
  # in cookies. Make this unique for your app.
  SECRET_KEY = 'shhh, secret!'

  # This is used by micawber, which will attempt to generate rich media
  # embedded objects with maxwidth=800.
  SITE_WIDTH = 800

  # You may consider using a one-way hash to generate the password, and then
  # use the hash again in the login view to perform the comparison. This is just
  # for simplicity.
  ADMIN_PASSWORD = 'secret'
  APP_DIR = os.path.dirname(os.path.realpath(__file__))

  # The playhouse.flask_utils.FlaskDB object accepts database URL configuration.
  DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')


class ProductionConfig(Config):
  DEBUG = False

  DATABASE = 'postgresext://zrzwfdfydlrfwk:EuQ8L8atZROsm76p2c2BteaZY8@ec2-54-225-112-215.compute-1.amazonaws.com:5432/d2l7j9pr4it50u'


class StagingConfig(Config):
  DEVELOPMENT = True
  DEBUG = True


class DevelopmentConfig(Config):
  DEVELOPMENT = True
  DEBUG = True


class TestingConfig(Config):
  TESTING = True

  # This should not equal the Production DB, but for now I don't have separate postgres server for testing...
  DATABASE = 'postgres://zrzwfdfydlrfwk:EuQ8L8atZROsm76p2c2BteaZY8@ec2-54-225-112-215.compute-1.amazonaws.com:5432/d2l7j9pr4it50u'
