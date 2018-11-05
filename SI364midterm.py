###############################
####### SETUP (OVERALL) #######
###############################

## Import statements
import os
import requests
import json
import spotipy
import sys
from flask import Flask, render_template, session, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, Form, SubmitField, validators, ValidationError # Note that you may need to import more here! Check out examples that do what you want to figure out what.
from wtforms.validators import DataRequired # Here, too
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Shell
from spotipy.oauth2 import SpotifyClientCredentials


## App setup code
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.debug = True
app.use_reloader = True

## All app.config values
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecurebutitsok'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://localhost/spot1"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

## Statements for db setup (and manager setup if using Manager)
db = SQLAlchemy(app)
manager = Manager(app)

## API setup
sp = spotipy.Spotify()

client_credentials_manager = SpotifyClientCredentials(client_id='4ea4d177cd0b446eb007833b538fe482', client_secret='e254dd99e9e741f298fef461fb7c6d9f')
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

######################################
######## HELPER FXNS (If any) ########
######################################

##################
##### MODELS #####
##################

#artists searched model
class Artists(db.Model):
    __tablename__ = "artist_searched"
    id = db.Column(db.Integer,primary_key=True)
    artist = db.Column(db.String(64))
    results = db.relationship('ArtistResults',backref='Artists')

    def __repr__(self):
        return "{} (ID: {})".format(self.artist, self.id)

#artist search results model
class ArtistResults(db.Model):
    __tablename__ = "artist_results"
    id = db.Column(db.Integer,primary_key=True)
    results = db.Column(db.String)
    artist_id = db.Column(db.Integer,db.ForeignKey("artist_searched.id"))

    def __repr__(self):
        return "{} (ID: {})".format(self.results, self.id)

###################
###### FORMS ######
###################


#artist list form
class artistlistform(FlaskForm):
    artist = StringField('Add an artist to the list:', validators=[DataRequired()])
    submit = SubmitField()
    def validate_artist(self, field):
        if len(field.data) > 20:
            raise ValidationError("Artist to add to list must be less than 20 characters")

#artist search form    
class artistsearchform(FlaskForm):
    artist = StringField('Search for an artist on Spotify:', validators=[DataRequired()])
    submit = SubmitField()
    def validate_artist(self, field):
        if len(field.data) > 20:
            raise ValidationError("Artist search term must be less than 20 characters")
   
#######################
###### VIEW FXNS ######
#######################

#home
@app.route('/')
def home():
   return render_template('base.html')

#add artist to list
@app.route('/artistadd', methods = ['GET','POST'])
def artist_form():
  form = artistlistform()
  if form.validate_on_submit():
      artist_searched = form.artist.data
      artist = Artists(artist = artist_searched)
      db.session.add(artist)
      db.session.commit()
      return redirect(url_for('all_artists'))
  return render_template('artistlistform.html', form=form)

#all artists searched
@app.route('/names')
def all_artists():
    artists = Artists.query.all()
    return render_template('artistssearched.html',artists=artists)

# search artist
@app.route("/searchartist", methods = ['GET','POST'])
def artist_search():
    form = artistsearchform()
    if form.validate_on_submit():
        artist_searched = (request.form['artist'])
        results = spotify.search(q='artist:' + artist_searched, type='artist')
        items = results['artists']['items']
        artistlist = []
        for item in items:
            name = item['name']
            artistlist.append(name)
        useableartists = str(artistlist)
        newartistlist = ArtistResults(results = useableartists)
        db.session.add(newartistlist)
        db.session.commit()
        return render_template('artistsearchform.html', form=form) + useableartists
    return render_template('artistsearchform.html', form=form)

#all search results
@app.route('/results')
def all_results():
    results = ArtistResults.query.all()
    return render_template('artistresults.html',results=results)

#error handler
@app.errorhandler(404) 
def page_not_found(e): 
    return render_template('404.html')

## Code to run the application...

# Put the code to do so here!
# NOTE: Make sure you include the code you need to initialize the database structure when you run the application!

if __name__ == '__main__':
  db.create_all()
  app.run(debug=True)
  manager.run()




        #director = Director.query.filter_by(full_name=movie_dir).first() # None if no such one -- make sure to use the .first() so it's not just a BaseQuery object!!
    #   db.session.add(artist_searched)
    #   db.session.commit()