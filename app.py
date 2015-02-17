#!/usr/local/bin/python

"""
file: adaptors/human/app.py

So far only search is exposed. Done via static/search.js.
"""
from flask import Flask, request, redirect, render_template, session, url_for
from flask.ext.wtf import Form
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy

from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Required
from wcwave_adaptors.watershed import default_vw_client

from collections import defaultdict
import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

key = os.getenv('VWPLATFORM_KEY')
app.secret_key = os.getenv('VWPLATFORM_KEY')

app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(BASEDIR, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

manager = Manager(app)

vw_client = default_vw_client()



#### INDEX ####
@app.route('/')
def index():
    "Splash page"
    if 'user_name' not in session:
        session['user_name'] = None

    # search URL is like https://129.24.196.28
    watershed_ip = vw_client.searchUrl.split('/')[2]

    return render_template("index.html", ip=watershed_ip,
                           user_name=session['user_name'])



#### ABOUT ####
@app.route('/about')
def about():
    "About page"
    return render_template("about.html", user_name=session['user_name'])


@app.route('/search', methods=['GET', 'POST'])
def search():
    """
    Create model run panels, rectangles on the search/home page that display
    summary information about the data that the VW has for a particular model
    run.

    Returns: (str) HTML string of the model run panel
    """
    # build the search form
    form = SearchForm()

    model_run_name = ''
    panels = []

    # if there was a submission, read the arguments and search
    # res = vw_client.search(**(request.args.to_dict()))
    search_args = defaultdict(str)
    model_run_name = form.model_run_name.data

    if model_run_name:
        search_args['model_run_name'] = model_run_name

    search_results = vw_client.search(**search_args)

    # make a panel of each metadata record
    panels = [_make_panel(rec) for rec in search_results.records]

    # this enforces unique model_run_uuids TODO integrate new search/modelruns
    panels = {p['model_run_uuid']: p for p in panels}.values()

    # pass the list of parsed records to the template to generate results page
    return render_template('search.html', form=form, panels=panels,
                           user_name=session['user_name'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    print form.validate_on_submit()

    if form.user_name.data and form.password.data:
        session['user_name'] = form.user_name.data
        return redirect(url_for('index'))

    return render_template('login.html', form=form)


def _make_panel(search_record):
    """
    Extract fields we currently support from a single JSON metadata file and
    prepare them in dict form to render search.html.

    Returns: (dict) that will be an element of the list of panel_data to be
        displayed as search results
    """
    lonmin, latmin, lonmax, latmax = \
        (el for el in search_record['spatial']['bbox'])

    centerlat = latmin + 0.5*(latmax - latmin)
    centerlon = lonmin + 0.5*(lonmax - lonmin)

    assert latmin < latmax, "Error, min lat is less than max lat"
    assert latmin < latmax, "Error, min lon is less than max lon"

    cats = search_record['categories'][0]
    state = cats['state']
    modelname = cats['modelname']
    watershed = cats['location']

    model_run_name = search_record['model_run_name']
    model_run_uuid = search_record['model_run_uuid'].replace('-', '')

    panel = {"latmin": latmin, "latmax": latmax,
             "lonmin": lonmin, "lonmax": lonmax,
             "centerlat": centerlat, "centerlon": centerlon, "state": state,
             "watershed": watershed,
             "model_run_name": model_run_name,
             "model_run_uuid": model_run_uuid,
             "model": modelname}

    return panel


###############
#### Forms ####
###############
class LoginForm(Form):
    """
    Login form for /login route
    """
    user_name = StringField('Enter your User Name', validators=[Required()])
    password = PasswordField('Enter your Password', validators=[Required()])
    submit = SubmitField('Go!')


class SearchForm(Form):
    """
    Flask-WTF form for the search page
    """
    model_run_name = StringField('Model Run Name')
    # start_datetime = DateTimeField('Start Date/time')
    # end_datetime = DateTimeField('End Date/time')
    submit = SubmitField('Submit')


###########################
#### Model Definitions ####
###########################
class User(db.Model):
    """
    Our User model. Users have biographical information, a user id, user name,
    and password.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True)
    affiliation = db.Column(db.String(64), index=True)
    state = db.Column(db.String(2), index=True)
    city = db.Column(db.String(20))
    email = db.Column(db.String(20))
    user_name = db.Column(db.String(20), unique=True)
    # passwd = db.Column(db.String(20), primary_key=True)

    def __repr__(self):
        return '<User %r>' % self.user_name


if __name__ == "__main__":
    # manager.run()
    app.run(debug=True)
