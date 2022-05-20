#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from forms import *
from flask import (render_template, 
  Flask,
  request, 
  Response, 
  flash, 
  redirect, 
  url_for
)
import logging
from logging import Formatter, FileHandler
import flask_migrate
#from flask_wtf import Form
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref
import datetime
from sqlalchemy import desc
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from flask_migrate import Migrate, migrate
import itertools

# connect to a local postgresql database `createdb fyyur`

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DatebaseURI')
db = SQLAlchemy(app)

# create a migrate object before running flask db init
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value ## fix format filter in html
  
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
today = datetime.datetime.now()

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  locations = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state)
  data = [{"city":location[0],"state":location[1], \
    "venues":[{"id":v.id,"name":v.name,"num_upcoming_shows": Show.query.filter(Show.venue_id==v.id, Show.start_time > today).count()} \
    for v in Venue.query.filter_by(city=location[0], state=location[1])]} for location in locations[::-1]]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  query = request.form.get("search_term","")  # retrieve POST data
  found_venues = db.session.query(Venue).filter(Venue.name.ilike(f"%{query}%")).all()

  data = [{"id": v.id, "name": v.name, "num_upcoming_shows": \
    Show.query.filter(Show.venue_id==v.id, Show.start_time > today).count()} for v in found_venues]
  count = len(data)
  
  response = {"count" : count,
            "data" : data
            }
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  if (data := Venue.query.get(venue_id)) is not None:
    upcoming_shows = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Show).filter(Show.venue_id==venue_id, Show.start_time > today).all()
    data.upcoming_shows = [dict(itertools.zip_longest(["artist_id","artist_name","artist_image_link","start_time"],show)) for show in upcoming_shows]
    data.upcoming_shows_count = len(data.upcoming_shows)
    past_shows = db.session.query(Artist.id, Artist.name, Artist.image_link, Show.start_time).join(Show).filter(Show.venue_id==venue_id, Show.start_time <= today).all()
    data.past_shows = [dict(itertools.zip_longest(["artist_id","artist_name","artist_image_link","start_time"],show)) for show in past_shows]
    data.past_shows_count = len(data.past_shows)
  else:
    return render_template('errors/404.html'), 404

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  form = VenueForm(request.form)
  
  try:
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash(f"Venue {request.form['name']} was successfully listed!")
  except ValueError as e:
    print(e)
    flash(f"An error occurred. Venue {request.form['name']} could not be listed.")
    db.session.rollback()
  finally:
    db.session.close()
 
  return redirect(url_for('venues'))
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()

  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('venues'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  query = request.form.get("search_term","")
  found_artist = db.session.query(Artist).filter(Artist.name.ilike(f"%{query}%")).all()
  
  data = [{
          "id": a.id, 
          "name": a.name, 
          "num_upcoming_shows": Show.query.filter(Show.artist_id==a.id, Show.start_time > today).count()
          } for a in found_artist
  ]
  
  response={
    "count": len(data),
    "data" : data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  if (data := Artist.query.get(artist_id)) is not None:
    upcoming_shows = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Show).filter(Show.artist_id==artist_id, Show.start_time > today).all()
    data.upcoming_shows = [dict(itertools.zip_longest(["venue_id","venue_name","venue_image_link","start_time"],show)) for show in upcoming_shows]
    data.upcoming_shows_count = len(data.upcoming_shows)
    past_shows = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Show).filter(Show.artist_id==artist_id, Show.start_time <= today).all()
    data.past_shows = [dict(itertools.zip_longest(["venue_id","venue_name","venue_image_link","start_time"],show)) for show in past_shows]
    data.past_shows_count = len(data.past_shows)
  else:
    return render_template('errors/404.html'), 404
 
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.get(artist_id)

  for var in request.form:
    if var == 'genres':
      setattr(artist, var, request.form.getlist(var))
    elif var == 'seeking_venue':
      setattr(artist, var, True if request.form.get(var) == 'y' else False)
    else:
      setattr(artist, var, request.form.get(var))
    
  try:
    db.session.commit()
    flash(f"Artist {request.form['name']} was successfully updated!")

  except:
    db.session.rollback()
    flash(f"An error occurred. Artist {request.form['name']} could not be updated")
    return render_template('page/home.html')
    
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  venue = Venue.query.get(venue_id)

  for var in request.form:
    if var == 'genres':
      setattr(venue, var, request.form.getlist(var))
    elif var == 'seeking_talent':
      setattr(venue, var, True if request.form.get(var) == 'y' else False)
    else:
      setattr(venue, var, request.form.get(var))
    
  try:
    db.session.commit()
    flash(f"Venue {request.form['name']} was successfully updated!")

  except:
    db.session.rollback()
    flash(f"An error occurred. Venue {request.form['name']} could not be updated")
    return render_template('page/home.html')
    
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form

  form = ArtistForm(request.form)
  
  try:
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    flash(f"Artist {request.form['name']} was successfully listed!")
  except ValueError as e:
    print(e)
    flash(f"An error occurred. Artist {request.form['name']} could not be listed.")
    db.session.rollback()
  finally:
    db.session.close()
 
  return redirect(url_for('artists'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows

  shows = db.session.query(Show.venue_id,Venue.name,Show.artist_id,  Artist.name, Artist.image_link, Show.start_time ).join(Artist).join(Venue).all()
  data = [dict(itertools.zip_longest(["venue_id","venue_name","artist_id","artist_name","artist_image_link","start_time"],show)) for show in shows]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  form = ShowForm(request.form)
  
  try:
    show = Show()
    form.populate_obj(show)
    db.session.add(show)
    db.session.commit()
    flash(f"Show {request.form['name']} was successfully listed!")
  except ValueError as e:
    print(e)
    flash(f"An error occurred. Show {request.form['name']} could not be listed.")
    db.session.rollback()
  finally:
    db.session.close()
    return redirect(url_for('shows'))
    
@app.errorhandler(400)
def bad_request_error(error):
    return render_template('errors/400.html'), 400

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
