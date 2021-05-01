#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
from enum import Enum

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app,db)



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


#  Show Home page
#  ----------------------------------------------------------------
@app.route('/')
def index():
  return render_template('pages/home.html')


#  Show All Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  area_list = Venue.query.with_entities(func.count(Venue.id),Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for area in area_list:
    venue_list = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []

    for venue in venue_list:
      venue_data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
      })
    data.append({"city": area.city, "state": area.state, "venues": venue_data })

  return render_template('pages/venues.html', areas=data)

#  Search Venue
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '')
  search_result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  item_list = []

  for venue in search_result:
     item_list.append({
       "id": venue.id,
       "name": venue.name,
       "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.now()).all()),
     })

  search_results={
     "count": len(search_result),
     "data": item_list
  }

  return render_template('pages/search_venues.html', results=search_results, search_term=request.form.get('search_term', ''))


#  Show Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  item = Venue.query.get(venue_id)

  old_show_list = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
  old_show_count = len(old_show_list)
  old_show_data = []

  for show in old_show_list:
    timestamp_str = show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    old_show_data.append({
       "venue_id":          show.venue_id,
       "venue_name":        show.venue.name,
       "artist_image_link": show.venue.image_link,
       "start_time":        timestamp_str
    })

  new_show_list =  db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  new_show_count = len(new_show_list)
  new_show_data = []
  for show in new_show_list:
    timestamp_str = show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    new_show_data.append({
       "venue_id":          show.venue_id,
       "venue_name":        show.venue.name,
       "artist_image_link": show.venue.image_link,
       "start_time":        timestamp_str
    })

  data={
    "id": item.id,
    "name": item.name,
    "genres": item.genres,
    "address": item.address,
    "city": item.city,
    "state": item.state,
    "phone": item.phone,
    "website": item.website,
    "facebook_link": item.facebook_link,
    "seeking_talent": item.seeking_talent,
    "image_link": item.image_link,
    "past_shows": old_show_data,
    "upcoming_shows": new_show_data,
    "past_shows_count": old_show_count,
    "upcoming_shows_count": new_show_count,
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)
  new_venue_id = 0

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  new_venue_id = None
  error = False
  form = VenueForm(request.form, meta={'csrf': False})
  new_venue = Venue()

  if form.validate():
    try:
       form.populate_obj(new_venue)
       db.session.add(new_venue)
       db.session.commit()
       new_venue_id = new_venue.id
    except:
       error = True
       print('*** Error saving new Venue...rolling back ***')
       print(sys.exc_info())
       db.session.rollback()
    finally:
       db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/new_venue.html', form=form, venue=new_venue)
  
  return redirect(url_for('show_venue', venue_id=new_venue_id)) 


#  Delete Venue
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>/delete', methods=['GET','POST'])
def delete_venue(venue_id):

   try:
     error = False
     item = Venue.query.get(venue_id)
     db.session.delete(item)
     db.session.commit()
   except:
     error = True
     print('*** Error deleting venue...rolling back ***')
     print(sys.exc_info())
     db.session.rollback()
   finally:
     db.session.close()

   if error:
     flash(f'An error occurred. Venue {venue_id} could not be deleted.')
   if not error:
     flash(f'Venue {venue_id} was successfully deleted.')
   return render_template('pages/home.html')




#  Show Artist list
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  try:
     error = False
     item_list = db.session.query(Artist).all()
  except:
     error = True
     print('*** Error querying Artist list...rolling back ***')
     print(sys.exc_info())
     db.session.rollback()
  finally:
     db.session.close()

  if error:
     flash('An error occurred listing Artists')

  return render_template('pages/artists.html', artists=item_list)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term', '')
  search_result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  item_list = []

  for result in search_result:
     item_list.append({
       "id": result.id,
       "name": result.name,
       "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == result.id).filter(Show.start_time > datetime.now()).all()),
     })

  search_results={
     "count": len(search_result),
     "data": item_list
  }


  return render_template('pages/search_artists.html', results=search_results, search_term=request.form.get('search_term', ''))

#  Show Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

   artist_query = db.session.query(Artist).get(artist_id)
   past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()
   past_shows = []

   for show in past_shows_query:
     timestamp_str = show.start_time.strftime('%Y-%m-%d %H:%M:%S')
     past_shows.append({
       "venue_id":          show.venue_id,
       "venue_name":        show.venue.name,
       "venue_image_link": show.venue.image_link,
       "start_time":        timestamp_str
     })

   upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.    now()).all()
   upcoming_shows = []

   for show in upcoming_shows_query:
     timestamp_str = show.start_time.strftime('%Y-%m-%d %H:%M:%S')
     upcoming_shows.append({
       "venue_id":          show.venue_id,
       "venue_name":        show.venue.name,
       "venue_image_link": show.venue.image_link,
       "start_time":        timestamp_str
     })

   artist_data = {
     "id":                   artist_query.id,
     "name":                 artist_query.name,
     "genres":               artist_query.genres,
     "city":                 artist_query.city,
     "state":                artist_query.state,
     "phone":                artist_query.phone,
     "website":              artist_query.website,
     "facebook_link":        artist_query.facebook_link,
     "seeking_venue":        artist_query.seeking_venue,
     "seeking_description":  artist_query.seeking_description,
     "image_link":           artist_query.image_link,
     "past_shows":           past_shows,
     "upcoming_shows":       upcoming_shows,
     "past_shows_count":     len(past_shows),
     "upcoming_shows_count": len(upcoming_shows),
   }

   return render_template('pages/show_artist.html', artist=artist_data)

#  Delete Artist
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>/delete', methods=['GET', 'POST'])
def delete_artist(artist_id):

   try:
     error = False
     item = Artist.query.get(artist_id)
     db.session.delete(item)
     db.session.commit()
   except:
     error = True
     print('*** Error deleting Artist...rolling back ***')
     print(sys.exc_info())
     db.session.rollback()
   finally:
     db.session.close()

   if error:
     flash(f'An error occurred. Artist {artist_id} could not be deleted.')
   if not error:
     flash(f'Artist {artist_id} was successfully deleted.')


   return render_template('pages/home.html')


#  Edit Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.first_or_404(artist_id)
  form = ArtistForm(obj=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False
  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form, meta={'csrf': False})

  if form.validate():
    try:
       form.populate_obj(artist)
       db.session.add(artist)
       db.session.commit()
    except:
       error = True
       print('*** Error saving artist updates...rolling back ***')
       print(sys.exc_info())
       db.session.rollback()
    finally:
       db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/edit_artist.html', form=form, artist=artist)

  return redirect(url_for('show_artist', artist_id=artist_id))


#  Edit Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.first_or_404(venue_id)
  form = VenueForm(obj=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  # query venue from database
  error = False
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form, meta={'csrf': False})
  
  if form.validate():
    try:
       form.populate_obj(venue)
       db.session.add(venue)
       db.session.commit()
    except:
       error = True
       print('*** Error saving venue updates...rolling back ***')
       print(sys.exc_info())
       db.session.rollback()
    finally:
       db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/edit_venue.html', form=form, venue=venue)

  return redirect(url_for('show_venue', venue_id=venue_id)) 



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  new_artist_id = None
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  new_artist_id = None
  form = ArtistForm(request.form, meta={'csrf': False})
  new_artist = Artist()

  if form.validate():
    try:
      form.populate_obj(new_artist)
      db.session.add(new_artist)
      db.session.commit()
      new_artist_id = new_artist.id
    except:
      error = True
      print('*** Error saving new Artist...rolling back ***')
      print(sys.exc_info())
      db.session.rollback()
    finally:
      db.session.close()
  else:
    message = []
    for field, err in form.errors.items():
        message.append(field + ' ' + '|'.join(err))
    flash('Errors ' + str(message))
    return render_template('forms/new_artist.html', form=form, artist=new_artist)

  return redirect(url_for('show_artist', artist_id=new_artist_id))


#  Shows
#  ----------------------------------------------------------------
@app.route('/shows')
def shows():

  item_list = db.session.query(Show).join(Artist).join(Venue).all()
  data = []
  for show in item_list:
     timestamp_str = show.start_time.strftime('%Y-%m-%d %H:%M:%S')

     data.append({
       "venue_id":          show.venue_id,
       "venue_name":        show.venue.name,
       "artist_id":         show.artist_id,
       "artist_name":       show.artist.name,
       "artist_image_link": show.artist.image_link,
       "start_time":        timestamp_str
  })

  return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  new_show = Show()

  try:
     form.populate_obj(new_show)
     db.session.add(new_show)
     db.session.commit()
  except:
     error = True
     print('*** Error saving new Show...rolling back ***')
     print(sys.exc_info())
     db.session.rollback()
  finally:
     db.session.close()

  if error:
     flash('An error occurred. Show could not be listed.')
  if not error:
     flash('Show was successfully listed!')

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

