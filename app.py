import datetime
import functools
import os
import re
import urllib
import sys

import logging

from flask import (Flask, flash, redirect, render_template, request,
                   Response, session, url_for)
from playhouse.flask_utils import FlaskDB, get_object_or_404, object_list
# from playhouse.postgres_ext import *

from models import flask_db, Entry

# Create a Flask WSGI app and configure it using values from the module.
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

# Set a logger
stream_handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(stream_handler)

# FlaskDB is a wrapper for a peewee database that sets up pre/post-request
# hooks for managing database connections.
flask_db.init_app(app)

# The `database` is the actual peewee database, as opposed to flask_db which is
# the wrapper.
database = flask_db.database

def login_required(fn):
  @functools.wraps(fn)
  def inner(*args, **kwargs):
    if session.get('logged_in'):
      return fn(*args, **kwargs)
    return redirect(url_for('login', next=request.path))
  return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
  next_url = request.args.get('next') or request.form.get('next')
  if request.method == 'POST' and request.form.get('password'):
    password = request.form.get('password')
    # TODO: If using a one-way hash, you would also hash the user-submitted
    # password and do the comparison on the hashed versions.
    if password == app.config['ADMIN_PASSWORD']:
      session['logged_in'] = True
      session.permanent = True  # Use cookie to store session.
      flash('You are now logged in.', 'success')
      return redirect(next_url or url_for('index'))
    else:
      flash('Incorrect password.', 'danger')
  return render_template('login.html', next_url=next_url)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
  if request.method == 'POST':
    session.clear()
    return redirect(url_for('login'))
  return render_template('logout.html')

@app.route('/')
def index():
  app.logger.error("test log")
  search_query = request.args.get('q')
  if search_query:
    query = Entry.search(search_query)
  else:
    query = Entry.public().order_by(Entry.timestamp.desc())
  app.logger.error("Entry query done")
  # The `object_list` helper will take a base query and then handle
  # paginating the results if there are more than 20. For more info see
  # the docs:
  # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#object_list
  return object_list(
    'index.html',
    query,
    search=search_query,
    check_bounds=False)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
  if request.method == 'POST':
    if request.form.get('title') and request.form.get('content'):
      entry = Entry.create(
        title=request.form['title'],
        content=request.form['content'],
        published=request.form.get('published') or False)
      flash('Entry created successfully.', 'success')
      if entry.published:
        return redirect(url_for('detail', slug=entry.slug))
      else:
        return redirect(url_for('edit', slug=entry.slug))
    else:
      flash('Title and Content are required.', 'danger')
  return render_template('create.html')

@app.route('/drafts/')
@login_required
def drafts():
  query = Entry.drafts().order_by(Entry.timestamp.desc())
  return object_list('index.html', query, check_bounds=False)

@app.route('/<slug>/')
def detail(slug):
  if session.get('logged_in'):
    query = Entry.select()
  else:
    query = Entry.public()
  entry = get_object_or_404(query, Entry.slug == slug)
  return render_template('detail.html', entry=entry)

@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
  entry = get_object_or_404(Entry, Entry.slug == slug)
  if request.method == 'POST':
    if request.form.get('title') and request.form.get('content'):
      entry.title = request.form['title']
      entry.content = request.form['content']
      entry.published = request.form.get('published') or False
      entry.save()

      flash('Entry saved successfully.', 'success')
      if entry.published:
        return redirect(url_for('detail', slug=entry.slug))
      else:
        return redirect(url_for('edit', slug=entry.slug))
    else:
      flash('Title and Content are required.', 'danger')

  return render_template('edit.html', entry=entry)

@app.template_filter('clean_querystring')
def clean_querystring(request_args, *keys_to_remove, **new_values):
  # We'll use this template filter in the pagination include. This filter
  # will take the current URL and allow us to preserve the arguments in the
  # querystring while replacing any that we need to overwrite. For instance
  # if your URL is /?q=search+query&page=2 and we want to preserve the search
  # term but make a link to page 3, this filter will allow us to do that.
  querystring = dict((key, value) for key, value in request_args.items())
  for key in keys_to_remove:
    querystring.pop(key, None)
  querystring.update(new_values)
  return urllib.urlencode(querystring)

@app.errorhandler(404)
def not_found(exc):
  return Response('<h3>Not found</h3>'), 404

def main():
  # database.create_tables([Entry, FTSEntry], safe=True)
  database.create_tables([Entry], safe=True)
  app.run(debug=True)

if __name__ == '__main__':
  main()
