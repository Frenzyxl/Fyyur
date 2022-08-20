# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from models import Venue, Artist, Show, db_setup
from flask_wtf import FlaskForm
from logging import Formatter, FileHandler
from forms import *

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db = db_setup(app)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    # date = dateutil.parser.parse(value)
    if isinstance(value, str):
        date = dateutil.parser.parse(value)
    else:
        date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#

@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    the_data = []
    city_states = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
    for city_state in city_states:
        state = city_state[1]
        city = city_state[0]
        venue = Venue.query.filter_by(city=city, state=state).all()

        details = {
            "city": city,
            "state": state,
            "venues": venue
        }
        the_data.append(details)
    return render_template('pages/venues.html', areas=the_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # search for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    the_venues = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term', '').strip() + '%')).all()

    the_data = []
    response = {
        "count": len(the_venues),
        "data": the_data
    }
    for venue in the_venues:
        details = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.upcoming_shows_count
        }
        the_data.append(details)
    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
    the_venue = Venue.query.get(venue_id)

    upcoming_shows = []
    past_shows = []
    all_shows = the_venue.shows
    for show in all_shows:
        if str(show.start_time) > current_time:
            upcoming_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
        else:
            past_shows.append({
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time)
            })
    genres = ','.join(the_venue.genres)

    data = {
        "id": the_venue.id,
        "name": the_venue.name,
        "genres": genres.split(','),
        "address": the_venue.address,
        "city": the_venue.city,
        "state": the_venue.state,
        "phone": the_venue.phone,
        "website": the_venue.website,
        "facebook_link": the_venue.facebook_link,
        "seeking_talent": the_venue.seeking_talent,
        "seeking_description": the_venue.seeking_description,
        "image_link": the_venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    form.facebook_link.data = "http://"
    form.website_link.data = "http://"
    form.image_link.data = "http://"
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)

    venue = Venue()
    venue.name = form.name.data
    venue.state = form.state.data
    venue.city = form.city.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.genres = request.form.getlist('genres')
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.website = form.website_link.data
    venue.seeking_description = form.seeking_description.data

    if form.validate_on_submit():
        try:
            db.session.add(venue)
            db.session.commit()
            # on successful db insert, flash success
            flash(f'Venue {form.name.data} was successfully listed!')
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash(f'An error occurred. Venue {form.name.data} could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        finally:
            db.session.close()
        return redirect(url_for('index'))
    else:
        flash(form.errors)
        return redirect(url_for('create_venue_submission'))


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    venue = Venue.query.get(venue_id)
    venue_name = venue.name
    try:
        db.session.delete(venue)
        db.session.commit()
        flash(f'Venue {venue_name} was successfully deleted!')
    except:
        db.session.rollback()
        flash(f'please try again. Venue {venue_name} could not be deleted.')
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button deletes it from the db then redirect the user to the homepage
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    the_artist = Artist.query.order_by(Artist.name).all()

    data = []
    for artist in the_artist:
        details = {
            "id": artist.id,
            "name": artist.name
        }
        data.append(details)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    the_artists = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term', '').strip() + '%')).all()

    the_data = []
    response = {
        "count": len(the_artists),
        "data": the_data
    }
    for artist in the_artists:
        details = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": artist.upcoming_shows_count,
        }
        the_data.append(details)
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(artist_id)

    upcoming_shows = []
    past_shows = []

    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
        Show.start_time > datetime.now()).all()
    past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(
        Show.start_time < datetime.now()).all()

    for the_show in upcoming_shows_query:
        upcoming_shows.append({
            "venue_id": the_show.venue_id,
            "venue_name": the_show.venue.name,
            "venue_image_link": the_show.venue.image_link,
            "start_time": str(the_show.start_time)
        })
    for the_show in past_shows_query:
        past_shows.append({
            "venue_id": the_show.venue_id,
            "venue_name": the_show.venue.name,
            "venue_image_link": the_show.venue.image_link,
            "start_time": str(the_show.start_time)
        })

    genres = ','.join(artist.genres)

    data1 = {
        "id": artist.id,
        "name": artist.name,
        "genres": genres.split(','),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data1)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    the_artist = Artist.query.get(artist_id)
    artist_information = {
        "id": the_artist.id,
        "name": the_artist.name,
        "genres": request.form.getlist('genres'),
        "city": the_artist.city,
        "state": the_artist.state,
        "phone": the_artist.phone,
        "website": the_artist.website,
        "facebook_link": the_artist.facebook_link,
        "seeking_venue": True if 'seeking_venue' in request.form else False,
        "seeking_description": the_artist.seeking_description,
        "image_link": the_artist.image_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    form.name.data = the_artist.name
    form.city.data = the_artist.city
    form.state.data = the_artist.state
    form.phone.data = the_artist.phone
    form.genres.data = the_artist.genres
    form.facebook_link.data = the_artist.facebook_link
    form.image_link.data = the_artist.image_link
    form.website_link.data = the_artist.website
    form.seeking_venue.data = the_artist.seeking_venue
    form.seeking_description.data = the_artist.seeking_description
    return render_template('forms/edit_artist.html', form=form, artist=artist_information)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)

    the_artist = Artist.query.get(artist_id)
    the_artist.name = form.name.data
    the_artist.state = form.state.data
    the_artist.city = form.city.data
    the_artist.phone = form.phone.data
    the_artist.image_link = form.image_link.data
    the_artist.seeking_description = form.seeking_description.data
    the_artist.facebook_link = form.facebook_link.data
    the_artist.seeking_venue = True if 'seeking_venue' in request.form else False
    the_artist.genres = request.form.getlist('genres')
    the_artist.website = form.website_link.data

    if form.validate_on_submit():
        try:
            db.session.commit()
            flash(f"Artist {the_artist.name} updated successfully")
        except:
            db.session.rollback()

            flash(f"Artist {the_artist.name} did not update successfully")
        finally:
            db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        flash(form.errors)
        return redirect(url_for('edit_artist_submission', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    the_venue = Venue.query.get(venue_id)

    venue = {
        "id": the_venue.id,
        "name": the_venue.name,
        "genres": the_venue.genres,
        "address": the_venue.address,
        "city": the_venue.city,
        "state": the_venue.state,
        "phone": the_venue.phone,
        "website": the_venue.website,
        "facebook_link": the_venue.facebook_link,
        "seeking_talent": the_venue.seeking_talent,
        "seeking_description": the_venue.seeking_description,
        "image_link": the_venue.image_link
    }
    # TODO: populate form with values from venue with ID <venue_id>
    form.name.data = the_venue.name
    form.city.data = the_venue.city
    form.state.data = the_venue.state
    form.phone.data = the_venue.phone
    form.genres.data = the_venue.genres
    form.facebook_link.data = the_venue.facebook_link
    form.address.data = the_venue.address
    form.image_link.data = the_venue.image_link
    form.website_link.data = the_venue.website
    form.seeking_talent.data = the_venue.seeking_talent
    form.seeking_description.data = the_venue.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)

    edited_venue = Venue.query.get(venue_id)
    edited_venue.name = form.name.data
    edited_venue.state = form.state.data
    edited_venue.city = form.city.data
    edited_venue.phone = form.phone.data
    edited_venue.image_link = form.image_link.data
    edited_venue.seeking_description = form.seeking_description.data
    edited_venue.address = form.address.data
    edited_venue.facebook_link = form.facebook_link.data
    edited_venue.seeking_talent = True if 'seeking_talent' in request.form else False
    edited_venue.genres = request.form.getlist('genres')
    edited_venue.website = form.website_link.data

    if form.validate_on_submit():
        try:
            db.session.commit()
            flash(f"Venue {edited_venue.name} updated successfully")
        except:
            db.session.rollback()

            flash(f"Venue {edited_venue.name} did not update successfully")
        finally:
            db.session.close()

        return redirect(url_for('show_venue', venue_id=venue_id))
    else:
        flash(form.errors)
        return redirect(url_for('edit_venue_submission', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    form.facebook_link.data = "http://"
    form.website_link.data = "http://"
    form.image_link.data = "http://"

    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)

    artist = Artist()
    artist.name = form.name.data
    artist.state = form.state.data
    artist.city = form.city.data
    artist.image_link = form.image_link.data
    artist.genres = request.form.getlist('genres')
    artist.phone = form.phone.data
    artist.facebook_link = form.facebook_link.data
    artist.website = form.website_link.data
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = form.seeking_description.data

    if form.validate_on_submit():

        try:
            db.session.add(artist)
            db.session.commit()
            # on successful db insert, flash success
            flash(f'Artist {form.name.data} was successfully listed!')
        except:
            db.session.rollback()
            # TODO: on unsuccessful db insert, flash an error instead.
            flash(f'An error occurred. Artist {form.name.data} could not be listed.')
        finally:
            db.session.close()
        return redirect(url_for('index'))
    else:
        flash(form.errors)
        return redirect(url_for('create_artist_submission'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = Show.query.all()
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    show = Show()
    show.artist_id = form.artist_id.data
    show.venue_id = form.venue_id.data
    show.start_time = form.start_time.data

    try:
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    finally:
        db.session.close()
    return redirect(url_for('index'))


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

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
