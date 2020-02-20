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
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate

import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model): # COMPLETE
  __tablename__ = 'Venue'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500))
  shows = db.relationship('Show', backref='venue')
    
  # "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    
  # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model): # COMPLETE
  __tablename__ = 'Artist'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  website = db.Column(db.String(500))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
  seeking_description = db.Column(db.String(500))
  shows = db.relationship('Show', backref='artist')

  # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model): # COMPLETE
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False)
  start_time = db.Column(db.DateTime, nullable = False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues(): # COMPLETE
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # data=[{
  #   "city": "San Francisco", 
  #   "state": "CA",
  #   "venues": [{
  #     "id": 1,
  #     "name": "The Musical Hop",
  #     "num_upcoming_shows": 0,
  #   }, {
  #     "id": 3,
  #     "name": "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }]

  venue_added = False
  data = []

  venue_list = Venue.query.order_by(Venue.city).all()

  prev_city = ''
  for venue in Venue.query.order_by(Venue.city).all():
    show_query = db.session.query(Show, Artist).filter(Artist.id == Show.artist_id).filter(Show.venue_id == venue.id)
    past_shows_data = show_query.filter(Show.start_time < datetime.today()).all()
    upcoming_shows_data = show_query.filter(Show.start_time > datetime.today()).all()
    
    if venue.city == prev_city:
      data[-1]["venues"].append({
        "id":venue.id,
        "name":venue.name,
        "num_upcoming_shows":len(upcoming_shows_data)
      })
    else:
      data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows":len(upcoming_shows_data)
        }]
      })
      prev_city = venue.city

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues(): # COMPLETE
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  query = Venue.query.filter( Venue.name.ilike('%'+request.form.get('search_term', '')+'%') ).all()
  
  response={
    "count": len(query),
    "data": []
  }

  for venue in query:
    show_query = db.session.query(Show, Artist).filter(Artist.id == Show.artist_id).filter(Show.venue_id == venue.id)
    upcoming_shows_data = show_query.filter(Show.start_time > datetime.today()).all()

    response['data'].append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(upcoming_shows_data)
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id): # COMPLETE
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }

  venue = Venue.query.get(venue_id)

  show_query = db.session.query(Show, Artist).filter(Artist.id == Show.artist_id).filter(Show.venue_id == venue_id)
  past_shows_data = show_query.filter(Show.start_time < datetime.today()).all()
  upcoming_shows_data = show_query.filter(Show.start_time > datetime.today()).all()

  print(past_shows_data)

  past_shows = []
  upcoming_shows = []

  def parse_show(show):
    return {
      "artist_id":show[1].id,
      "artist_name":show[1].name,
      "artist_image_link":show[1].image_link,
      "start_time":show[0].start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
  
  for instance in past_shows_data:
    past_shows.append(parse_show(instance))
  
  for instance in upcoming_shows_data:
    upcoming_shows.append((parse_show(instance)))

  venue_genre = venue.genres.split(",")

  data = venue.__dict__
  data['genres'] = venue_genre
  data['past_shows'] = past_shows
  data['upcoming_shows']= upcoming_shows
  data['past_shows_count']= len(past_shows)
  data['upcoming_shows_count']= len(upcoming_shows)

  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form(): # NOT APPLICABLE
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission(): # COMPLETE
  # TODO: insert form data as a new Venue record in the db, instead
  error = False
  venue = Venue(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    address = request.form['address'],
    phone = request.form['phone'],
    genres = request.form['genres'],
    facebook_link = request.form['facebook_link']
  )
  try:
    db.session.add(venue)
  except:
    error = True
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.commit()
    if error == False:
      flash('Venue ' + Venue.query.get(venue.id).name + ' was successfully listed!')

  #print(Venue.query.get(venue.id) )
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id): # COMPLETE
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

  error = False
  venue = Venue.query.get(venue_id)

  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Venue ' + venue.name + ' could not be Deleted.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error == False:
      flash('Venue ' + venue.name + ' was successfully deleted!')
    db.session.close()
  return redirect(url_for('venues'),code=200)

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists(): # COMPLETE
  # TODO: replace with real data returned from querying the database
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]

  artist_list = Artist.query.order_by(Artist.id).all()
  data = []
  
  for artist in artist_list:
    data.append({
      "id":artist.id,
      "name":artist.name,
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists(): # COMPLETE
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # response={
  #   "count": len(query),
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

  query = Artist.query.filter( Artist.name.ilike('%'+request.form.get('search_term', '')+'%') ).all()
  
  response={
    "count": len(query),
    "data": []
  }

  for artist in query:
    show_query = db.session.query(Show, Venue).filter(Venue.id == Show.venue_id).filter(Show.artist_id == artist.id)
    upcoming_shows_data = show_query.filter(Show.start_time > datetime.today()).all()

    response['data'].append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows_data)
    })
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id): # COMPLETE
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  # data1={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "past_shows": [{
  #     "venue_id": 1,
  #     "venue_name": "The Musical Hop",
  #     "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  
  artist = Artist.query.get(artist_id)
  
  show_query = db.session.query(Show, Venue).filter(Venue.id == Show.venue_id).filter(Show.artist_id == artist_id)
  past_shows_data = show_query.filter(Show.start_time < datetime.today()).all()
  upcoming_shows_data = show_query.filter(Show.start_time > datetime.today()).all()

  past_shows = []
  upcoming_shows = []

  def parse_show(show):
    return {
      "venue_id":show[1].id,
      "venue_name":show[1].name,
      "venue_image_link":show[1].image_link,
      "start_time":show[0].start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }
  
  for instance in past_shows_data:
    past_shows.append(parse_show(instance))
  
  for instance in upcoming_shows_data:
    upcoming_shows.append((parse_show(instance)))

  artist_genre = artist.genres.split(',')

  data = artist.__dict__
  data['genres'] = artist_genre
  data['past_shows'] = past_shows
  data['upcoming_shows']= upcoming_shows

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id): # COMPLETE

  # TODO: populate form with fields from artist with ID <artist_id>
  
  #form.name.data = 'Hello World'
  
  # artist={
  #   "id": 4,
  #   "name": "Guns N Petals",
  #   "genres": ["Rock n Roll"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "326-123-5000",
  #   "website": "https://www.gunsnpetalsband.com",
  #   "facebook_link": "https://www.facebook.com/GunsNPetals",
  #   "seeking_venue": True,
  #   "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
  #   "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  # }
  artist = Artist.query.get(artist_id)
  artist_genres = artist.genres.split(',')
  artist = artist.__dict__
  artist['genres'] = artist_genres

  form = ArtistForm(data = artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id): # COMPLETE
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  artist = Artist.query.get(artist_id)

  data = {
    'name' : request.form['name'],
    'city' : request.form['city'],
    'state' : request.form['state'],
    'phone' : request.form['phone'],
    'genres' : request.form['genres'],
    'facebook_link' : request.form['facebook_link']
  }
  try:
    for key, value in data.items():
      setattr(artist,key,value)
    
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error == False:
      flash('Artist ' + Artist.query.get(artist.id).name + ' was successfully listed!')
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id): # COMPLETE

  # TODO: populate form with values from venue with ID <venue_id>

  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }

  venue = Venue.query.get(venue_id)
  venue_genres = venue.genres.split(',')
  venue = venue.__dict__
  venue['genres'] = venue_genres

  form = VenueForm(data = venue)

  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id): # COMPLETE
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  venue = Venue.query.get(venue_id)

  data = {
    'name' : request.form['name'],
    'genres' : request.form['genres'],
    "address": request.form['address'],
    'city' : request.form['city'],
    'state' : request.form['state'],
    'phone' : request.form['phone'],
    'facebook_link' : request.form['facebook_link']
  }
  try:
    for key, value in data.items():
      setattr(venue,key,value)
    
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error == False:
      flash('Venue ' + Venue.query.get(venue.id).name + ' was successfully listed!')
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form(): # NA
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission(): # COMPLETE
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Artist record in the db, instead
  error = False
  artist = Artist(
    name = request.form['name'],
    city = request.form['city'],
    state = request.form['state'],
    phone = request.form['phone'],
    genres = request.form['genres'],
    facebook_link = request.form['facebook_link']
  )
  try:
    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error == False:
      flash('Artist ' + Artist.query.get(artist.id).name + ' was successfully listed!')
    db.session.close()

  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>/delete', methods=['DELETE'])
def delete_artist(artist_id): # COMPLETE
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Artist on a Artist Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  
  error = False
  artist = Artist.query.get(artist_id)

  try:
    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Artist ' + artist.name + ' could not be Deleted.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error == False:
      flash('Artist ' + artist.name + ' was successfully deleted!')
    db.session.close()
  return redirect(url_for('artists'),code=200)

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows(): # COMPLETE
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]

  show_list = Show.query.order_by(Show.id).all()
  data =[]

  for show in show_list:
    venue_id = show.venue_id
    venue = Venue.query.get(venue_id)
    venue_name = venue.name

    artist_id = show.artist_id
    artist = Artist.query.get(artist_id)
    artist_name = artist.name
    artist_image_link = artist.image_link

    start_time = show.start_time

    instance = {
      "venue_id": venue_id,
      "venue_name": venue_name,
      "artist_id": artist_id,
      "artist_name": artist_name,
      "artist_image_link": artist_image_link,
      "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    }

    data.append(instance)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows(): # DONT TOUCH
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission(): # Complete
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  show = Show(
    artist_id = request.form['artist_id'],
    venue_id = request.form['venue_id'],
    start_time = request.form['start_time']
  )
  try:
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    flash('An error occurred. Show ' + show.name + ' could not be listed.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error == False:
      flash('Show ' + Show.query.get(show.id).name + ' was successfully listed!')
    db.session.close()

  # on successful db insert, flash success
  #flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
