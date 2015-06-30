from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from flask import current_app as app
from werkzeug import secure_filename
from . import visualization
from .. import db
from ..models import Resource
from wcwave_adaptors import default_vw_client
from wcwave_adaptors import make_fgdc_metadata, metadata_from_file

import os, osr, util, numpy


VW_CLIENT = default_vw_client()


@visualization.route('/')
@login_required
def confirmVisFile():
    """
    This function is designed for users to choose
    a file to visualize
    """
    #TODO: upload file part

    #TODO: obtain units from csv file

    #TODO
    #choose a file stored in the server 
    #grab the url of the csv file
    
    

    #this part is just for test
    #for csv only
    item_nameList = []
    #get the current app location
    #app/visualization
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    download_dir = APP_ROOT + '/tempData/'
    filename = 'BRW_HrlySummary_2014.csv'
    #getItemName five variables: folder, file name, item in the csv,
    #first row offset, second row offset,  coloumn offset
    util.getItemName(download_dir,filename,item_nameList ,19,0,0)
   
    return render_template('visualization/index.html', item_nameList = item_nameList)

@visualization.route("/<path:path>")
def relation(path):
    #get the current app location
    #app/visualization
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    #the file extension could only be csv now
    if path.endswith('.csv'):
        #print APP_ROOT + "/tempData/" + path
        return send_from_directory(APP_ROOT + "/tempData/", path)
    else:
		#print APP_ROOT + "/../templates/visualization/" + path
		return send_from_directory(APP_ROOT + "/../templates/visualization/", path)
		

