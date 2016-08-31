import datetime
import re

from urlparse import urlparse

from flask import Markup
from flask import current_app as app
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache

from peewee import *
from playhouse.flask_utils import FlaskDB
from playhouse.postgres_ext import *

flask_db = FlaskDB()

# flask_db = FlaskDB()

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())

class Entry(flask_db.Model):
  title = CharField()
  slug = CharField(unique=True)
  content = TextField()
  published = BooleanField(index=True)
  timestamp = DateTimeField(default=datetime.datetime.now, index=True)
  search_content = TSVectorField()

  @property
  def html_content(self):
    """
    Generate HTML representation of the markdown-formatted blog entry,
    and also convert any media URLs into rich media objects such as video
    players or images.
    """
    hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
    extras = ExtraExtension()
    markdown_content = markdown(self.content, extensions=[hilite, extras])
    oembed_content = parse_html(
      markdown_content,
      oembed_providers,
      urlize_all=True,
      maxwidth=app.config['SITE_WIDTH'])
    return Markup(oembed_content)

  def save(self, *args, **kwargs):
    # Generate a URL-friendly representation of the entry's title.
    if not self.slug:
      self.slug = re.sub('[^\w]+', '-', self.title.lower()).strip('-')

    # Store search content.
    self.update_search_index()

    ret = super(Entry, self).save(*args, **kwargs)
    return ret

  def update_search_index(self):
    self.search_content = fn.to_tsvector(self.content)

  @classmethod
  def public(cls):
    return Entry.select().where(Entry.published == True)

  @classmethod
  def drafts(cls):
    return Entry.select().where(Entry.published == False)

  @classmethod
  def search(cls, query):
    words = [word.strip() for word in query.split() if word.strip()]
    if not words:
      # Return an empty query.
      return Entry.select().where(Entry.id == 0)
    else:
      search = ' '.join(words)

    # Query the full-text search index for entries matching the given
    # search query, then join the actual Entry data on the matching
    # search result.
    return Entry.select().where(
        (Entry.published == True) &
        (Entry.search_content.match(search))) # | Match(Entry.title, search)))


