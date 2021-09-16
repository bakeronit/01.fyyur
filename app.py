#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
#from flask_wtf import Form
from flask_wtf import FlaskForm
from sqlalchemy.orm import backref
from forms import *
from flask_migrate import Migrate, migrate
import datetime
from sqlalchemy import desc
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# create a migrate object before running flask db init
migrate = Migrate(app, db)

# connect to a local postgresql database `createdb fyyur`

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    
    genres = db.Column(db.ARRAY(db.String()))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(800))
    website = db.Column(db.String(500))
    shows = db.relationship('Show', backref='Venue',lazy='dynamic')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(800))
    shows = db.relationship('Show',backref='Artist', lazy='dynamic')


class Show(db.Model):
  __tablename__ = 'Show'
  
  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  #print(locations[1])
  data = [{"city":location[0],"state":location[1], \
    "venues":[{"id":v.id,"name":v.name,"num_upcoming_shows": Show.query.filter(Show.venue_id==v.id, Show.start_time > today).count()} \
    for v in Venue.query.filter_by(city=location[0], state=location[1])]} for location in locations[::-1]]

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  
  query = request.form.get("search_term","")  # retrieve POST data
  found_venues = db.session.query(Venue).filter(Venue.name.ilike(f"%{query}%")).all()

  data = [{"id": v.id, "name": v.name, "num_upcoming_shows": \
    Show.query.filter(Show.venue_id==v.id, Show.start_time > today).count()} for v in found_venues]
  count = len(data)
  
  response = {"count" : count,
            "data": data
            }

  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  if (data := Venue.query.get(venue_id)) is not None:
    data.past_shows = [{"artist_id":show.artist_id,"artist_name":Artist.query.get(show.artist_id).name,\
      "artist_image_link":Artist.query.get(show.artist_id).image_link,"start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")} \
      for show in data.shows if show.start_time < today ]
    data.past_shows_count = len(data.past_shows)
    data.upcoming_shows = [{"artist_id":show.artist_id,"artist_name":Artist.query.get(show.artist_id).name,\
      "artist_image_link":Artist.query.get(show.artist_id).image_link,"start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")} \
      for show in data.shows if show.start_time > today ]
    data.upcoming_shows_count = len(data.upcoming_shows)
  else:
    return render_template('errors/404.html'), 404

  #venues_fields = ["id", "name", "genres", "address", "city", "state", "phone", \
  #  "website", "facebook_link", "seeking_talent", "seeking_description", "image_link", \
  #    "past_shows_count", "upcoming_shows_count"]
  
  #venue_info = [venue.id, venue.name, venue.genres, venue.address, venue.city, venue.state, venue.phone, \
  #  venue.website, venue.facebook_link, venue.seeking_talent, venue.seeking_description, venue.image_link, \
  #  Show.query.filter(Show.venue_id==venue.id, Show.start_time < today).count(), \
  #  Show.query.filter(Show.venue_id==venue.id, Show.start_time > today).count()]
  
  #data = { field: info for field,info in zip(venues_fields, venue_info)}
  
  #past_shows = [{"artist_id": show.artist_id, "artist_name": Artist.query.get(show.artist_id).name, \
  #  "artist_image_link": Artist.query.get(show.artist_id).image_link, "start_time": format_datetime(show.start_time)} \
  #    for show in db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time < today).all()]
  #upcoming_shows = [{"artist_id": show.artist_id, "artist_name": Artist.query.get(show.artist_id).name, \
  #  "artist_image_link": Artist.query.get(show.artist_id).image_link, "start_time": format_datetime(show.start_time)} \
  #    for show in db.session.query(Show).filter(Show.venue_id==venue.id, Show.start_time > today).all()]
  
  #data["past_shows"] = past_shows
  #data["upcoming_shows"] = past_shows

  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  venue = Venue()
  for var in request.form:
    if var == 'genres':
      setattr(venue, var, request.form.getlist(var))
    elif var == 'seeking_talent':
      setattr(venue, var, True if request.form.get(var) == 'y' else False)
    else:
      setattr(venue, var, request.form.get(var))
  
  try:
    db.session.add(venue)
    db.session.commit()
    flash(f"Venue {request.form['name']} was successfully listed!")
  
  except:
    db.session.rollback()
    flash(f"An error occurred. Venue {request.form['name']} could not be listed.")
    return render_template('page/home.html')
  
  finally:
    db.session.close()

  return redirect(url_for('venues'))
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
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
  data = [{"id": a.id, "name": a.name, "num_upcoming_shows": \
    Show.query.filter(Show.artist_id==a.id, Show.start_time > today).count()} for a in found_artist]
  
  response={
    "count": len(data),
    "data" : data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id

  if (data := Artist.query.get(artist_id)) is not None:
    data.past_shows = [{"venue_id":show.venue_id,"venue_name":Venue.query.get(show.venue_id).name,\
      "venue_image_link":Venue.query.get(show.venue_id).image_link,"start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")} \
      for show in data.shows if show.start_time < today]
    data.past_shows_count = len(data.past_shows)
    data.upcoming_shows = [{"venue_id":show.venue_id,"venue_name":Venue.query.get(show.venue_id).name,\
      "venue_image_link":Venue.query.get(show.venue_id).image_link,"start_time":show.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")} \
      for show in data.shows if show.start_time > today ]
    data.upcoming_shows_count = len(data.upcoming_shows)
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

  artist = Artist()
  for var in request.form:
    if var == 'genres':
      setattr(artist, var, request.form.getlist(var))
    elif var == 'seeking_venue':
      setattr(artist, var, True if request.form.get(var) == 'y' else False)
    else:
      setattr(artist, var, request.form.get(var))

  try:
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    return render_template('pages/home.html')

  finally:
    db.session.close()

  return redirect(url_for("artists"))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows


  shows = Show.query.all()
  data = [{"venue_id": s.venue_id, "venue_name":Venue.query.get(s.venue_id).name,\
    "artist_id":s.artist_id,"artist_name":Artist.query.get(s.artist_id).name,\
    "artist_image_link":Artist.query.get(s.artist_id).image_link,\
      "start_time":s.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f%z")} for s in shows]

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form

  show = Show()
  for var in request.form:
    setattr(show, var, request.form.get(var))

  try:
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
    return redirect(url_for("shows"))

  except:
    db.session.rollback()    
    flash('An error occurred. Show could not be listed.')
    return render_template('pages/home.html')
  
  finally:
    db.session.close()


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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
