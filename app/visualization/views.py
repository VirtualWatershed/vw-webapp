from flask import render_template, flash, redirect, url_for, request, send_from_directory
from flask_login import login_required, current_user
from flask import current_app as app
from werkzeug import secure_filename
from . import visualization
from .. import db
from ..models import Resource
from wcwave_adaptors import default_vw_client
from wcwave_adaptors import make_fgdc_metadata, metadata_from_file
from netCDF4 import Dataset

from .classes import NetCDFInformation, VariableDimensionInformation

import os, osr, util, numpy


VW_CLIENT = default_vw_client()

@visualization.route('/')
@login_required
def index():
    return render_template('visualization/index.html')

# this part is for upload csv files
# the idea is from http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
@visualization.route('/CSV/')
@login_required
def csv_access_files():
    return render_template('visualization/csv_file_access.html')

@visualization.route('/CSV/upload_page')
@login_required
def csv_upload_files():
    return render_template('visualization/csv_upload.html')

# Route that will process the file upload
@visualization.route('/CSV/upload/', methods=['POST'])
def csv_upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and util.allowed_file_csv(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # app/visualization
        # get the current app location
        app_root = os.path.dirname(os.path.abspath(__file__))
        download_dir = app_root + '/tempData/'
        file.save(os.path.join(download_dir, filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return render_template('visualization/csv_metadata_confirm.html',\
                               filename=filename)
    else:
        return render_template('visualization/csv_error_upload.html')

# upload section ends here


@visualization.route('/CSV/visualization_results/upload/<filename>', methods=['POST'])
@login_required
def csv_upload_visualization(filename=''):
    """
    This function is designed for users to upload
    a file to visualize
    """

    # TODO
    # choose a file stored in the server 
    # grab the url of the csv file
    
    # obtain row_offset and column_offset
    csv_row_offset = request.form['row_offset']
    csv_column_offset = request.form['column_offset']

    item_name_list = []
    # get the current app location
    # app/visualization
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/tempData/'
    # getItemName five variables: folder, file name, item in the csv,
    # first row offset, second row offset,  coloumn offset
    util.getItemName(download_dir, filename, item_name_list, \
                     csv_row_offset, 0, csv_column_offset)
    input_filename = 'temp' + filename
    return render_template('visualization/csv_visualization_results.html', \
                           item_name_list=item_name_list, \
                           input_filename=input_filename)

# this part is for upload NetCDF files
# the idea is from http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
@visualization.route('/NetCDF/')
@login_required
def netcdf_access_files():
    return render_template('visualization/netcdf_file_access.html')

@visualization.route('/NetCDF/upload_page')
@login_required
def netcdf_upload_files():
    return render_template('visualization/netcdf_upload.html')

# Route that will process the file upload
@visualization.route('/NetCDF/upload/', methods=['POST'])
def netcdf_upload():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file and util.allowed_file_netcdf(file.filename):
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        # Move the file form the temporal folder to
        # app/visualization
        # get the current app location
        app_root = os.path.dirname(os.path.abspath(__file__))
        download_dir = app_root + '/tempData/'
        file.save(os.path.join(download_dir, filename))
        # Redirect the user to the uploaded_file route, which
        # will basicaly show on the browser the uploaded file
        return redirect('/visualization/NetCDF/'+filename)
    else:
        return render_template('visualization/netcdf_error_upload.html')

# upload section ends here


# this is an evil global variable
netcdf_file_local_path = ''
# this is used by users to confirm which varible to visualize
# and which dimension about that varible by 
# /visualization/linechart/variable_name/dimension_y
# or /visualization/map/variable_name/dimension_x/dimension_y 
@visualization.route('/NetCDF/<filename>')
@login_required
def get_NetCDF_information(filename=''):
    # this part is used flat_input.nc for test
    # later I will connect to the DB and enable users 
    # to choose a file by themselves

    # get the current app location
    # app/visualization
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/tempData/'
    filename_path = download_dir + filename
    global netcdf_file_local_path
    netcdf_file_local_path = filename_path
    dimension_name_list = []
    variable_name_list = []
    variable_class_list = []

    # open netcdf file
    netcdf_aim_file = Dataset(filename_path, "r")
    
    # get the dimension name list
    for dimobj in netcdf_aim_file.dimensions.values():
        dimension_name_list.append(dimobj.name)

    # get the variable name list
    # varobj will contain dimension names
    # I remove them by using if not in
    # because I think nobody want to visualize these
    # dimension variables
    for varobj in netcdf_aim_file.variables.values():
        if varobj.name not in dimension_name_list:
            variable_name_list.append(varobj.name)

    # get all variables information and store them into varable class lists
    for temp_variable_name in variable_name_list:
        # use netcdf_aim_file.variables[temp_variable_name].ncattrs()
        # to list all the attributes of a varible
        # netcdf_aim_file.variables[temp_variable_name].dimensions
        # this will return tuple, not list
        temp_dim_handle = netcdf_aim_file.variables[temp_variable_name] 
        temp_dims = list(temp_dim_handle.dimensions)
        temp_dim_len = len(temp_dims)
        if  'description' in temp_dim_handle.ncattrs():
            temp_variable_object = \
            NetCDFInformation(temp_variable_name, \
                              temp_dim_len, \
                              temp_dims, \
                              temp_dim_handle.description)
            variable_class_list.append(temp_variable_object)
        else:
            temp_variable_object = \
            NetCDFInformation(temp_variable_name, \
                              temp_dim_len, \
                              temp_dims)
            variable_class_list.append(temp_variable_object)

    return render_template('visualization/netcdf_information.html', \
                           filename=filename, \
                           variable_name_list=variable_name_list, \
                           variable_class_list=variable_class_list)
    

# this function is used to handle the last step of line chart visualizion
# parse input and obtain data from netcdf
def line_chart_last_step(vis_param=''):
    # TODO remove these evil global variables
    global netcdf_file_local_path
    global dimension_name_list
    global chosen_x
    global chosen_y
    global variable_name
    # open netcdf file
    netcdf_aim_file = Dataset(netcdf_file_local_path, "r")
    # vis_param structure is dimensionName:index;
    # pop becausethe last element will be ''
    dimension_information_list = vis_param.split(';')
    dimension_information_list.pop()
    # parse information list
    # specify_dimension_name = []
    specify_dimension_index = []
    specify_dimension_chosen_index = []
    for item in dimension_information_list:
        item_information = item.split(':')
        # item_information[0] is the dimension index 
        # specify_dimension_name.append(item_information[0])
        specify_dimension_index.append(dimension_name_list.index(item_information[0]))
        # item_information[1] is the dimension index chosen by users
        # this value need to be -1, coz it starts from 1
        specify_dimension_chosen_index.append(str(int(item_information[1])-1))
    # collect visualization dimension information
    # and make clear variable is in x or y axis
    vis_dimension = ''
    bool_variable_x = False
    if chosen_x == variable_name:
        bool_variable_x = True
        vis_dimension = chosen_y
    else:
        bool_variable_x = False
        vis_dimension = chosen_x
    vis_dimension_index = dimension_name_list.index(vis_dimension)

    # create executable string to obtain data
    # this list is used to record obtained data
    vis_dimension_data = []
    # the string last character should be ) 
    # this exec_string does not consider masked value
    # therefore, if users choose to visualize m_pp there will be some bugs
    exec_string = "for count in range(len(netcdf_aim_file.variables[\'"+ \
                  vis_dimension+ \
                  "\'])):\n    vis_dimension_data.append(netcdf_aim_file.variables[\'" \
                  +variable_name+"\']"
    for item in range(len(dimension_name_list)):
        if item == vis_dimension_index:
            exec_string = exec_string + "[count]"
        else:
            for temp_index in specify_dimension_index:
                if item == temp_index:
                    exec_string = exec_string + "[" + \
                    specify_dimension_chosen_index[specify_dimension_index.index(temp_index)] \
                    + "]"
    
    exec_string = exec_string + ")"
    # print exec_string
    exec exec_string
    # print vis_dimension_data

    # create csv string
    # create vis_dimension_list
    vis_dimension_list = []
    for item in netcdf_aim_file.variables[vis_dimension]:
        vis_dimension_list.append(item)
    if bool_variable_x:
        csv_string = util.create_csv_file_string(vis_dimension_list, \
                                                 vis_dimension, \
                                                 vis_dimension_data, \
                                                 variable_name)
    else:
        csv_string = util.create_csv_file_string(vis_dimension_data, \
                                                 variable_name, \
                                                 vis_dimension_list, \
                                                 vis_dimension)
    return csv_string

@visualization.route("/<path:path>")
def relation(path):
    # get the current app location
    # app/visualization
    app_root = os.path.dirname(os.path.abspath(__file__))
    # the file extension could only be csv now
    if path.endswith('.csv'):
        # print app_root + "/tempData/" + path
        filename_csv = path.rsplit("/",1)[1]
        return send_from_directory(app_root + "/tempData/", filename_csv)
    elif path.endswith('.nc'):
        # print app_root + "/tempData/" + path
        filename_nc = path.rsplit("/",1)[1]
        return send_from_directory(app_root + "/tempData/", filename_nc)
    elif path.endswith('.js'):
        # this line is used to get the js filename
		filename_js = path.rsplit("/",1)[1]
		return send_from_directory(app_root + "/../templates/visualization/js", \
                                   filename_js)
    elif path.endswith('.png'):
        # this line is used to get the png filename
		filename_img = path.rsplit("/",1)[1]
		return send_from_directory(app_root + "/../templates/visualization/img", \
                                   filename_img)
    # this used to obtain parameters for NetCDF visualization
    elif path.endswith('NetCDFParameters'):
        # this line is used to get the js filename
        vis_param = path.rsplit("/",1)[1]
        vis_param = util.replace_last(vis_param,'NetCDFParameters','')
        csv_string = line_chart_last_step(vis_param)
        return render_template('visualization/netcdf_visualization_results.html', \
                               csv_string=csv_string)
        


# this list contains the chosen item dimension names
dimension_name_list = ''
chosen_x = ''
chosen_y = ''
variable_name = ''
# TODO: this version just works when time is number
# Lisa is creating some NetCDF, whose time is string
@visualization.route("/NetCDF/lineChart/<variablename>/<xaxis>/<yaxis>")
def netcdf_line_chart_visualization(variablename='', xaxis='', yaxis=''):
    global netcdf_file_local_path
    global dimension_name_list
    global chosen_x
    global chosen_y
    global variable_name
    
    chosen_x = xaxis
    chosen_y = yaxis    
    variable_name = variablename

    # open netcdf file
    netcdf_aim_file = Dataset(netcdf_file_local_path, "r")
    dimension_name_list = list(netcdf_aim_file.variables[variablename].dimensions)
    # this list is used to list all the dimensions need 
    # to be specified by users, this list will never include
    # variable itself
    specify_dimension_list = []
    for item in dimension_name_list:
        if (item!=xaxis) and (item!=yaxis):
            specify_dimension_list.append(item)

    # collect all the dimension information
    # this list is used to record dimension values
    temp_value_list = []
    # this list is used to record all the 
    # variable dimension information objects
    dimension_information_list = []
    for item in specify_dimension_list:
        for temp_value in netcdf_aim_file.variables[item]:
            temp_value_list.append(temp_value)
        # following codes are based on an idea about netcdf:
        # if a thing is in dimension list
        # then it must be a variable too
        temp_dimension_information_object = \
            VariableDimensionInformation(item,\
                                         len(netcdf_aim_file.variables[item]),\
                                         temp_value_list)
        dimension_information_list.append(temp_dimension_information_object)
        temp_value_list = []
        
    return render_template('visualization/netcdf_linechart.html', \
           variablename=variablename, xaxis=xaxis, yaxis=yaxis, \
           dimension_information_list=dimension_information_list, \
           specify_dimension_list=specify_dimension_list);




