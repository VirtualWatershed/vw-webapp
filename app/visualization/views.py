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

import os, osr, util, numpy


VW_CLIENT = default_vw_client()


@visualization.route('/')
@login_required
def confirmVisFile():
    """
    This function is designed for users to choose
    a file to visualize
    """
    # TODO: upload file part

    # TODO: obtain units from csv file

    # TODO
    # choose a file stored in the server 
    # grab the url of the csv file
    
    

    # this part is just for test
    # for csv only
    item_nameList = []
    # get the current app location
    # app/visualization
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    download_dir = APP_ROOT + '/tempData/'
    filename = 'BRW_HrlySummary_2014.csv'
    # getItemName five variables: folder, file name, item in the csv,
    # first row offset, second row offset,  coloumn offset
    util.getItemName(download_dir,filename,item_nameList ,19,0,0)
   
    return render_template('visualization/index.html', item_nameList = item_nameList)

# this class is used to record the variable parameters
# information, name, dimension count, dimension names
class NetCDFInformation:
    variable_name = ''
    dimension_count = 0
    dimension_name_list = []
    description_information = ''
    def __init__(self, name, count, name_list, description=''):
        self.variable_name = name
        self.dimension_count = count
        self.dimension_name_list = name_list
        self.description_information = description

# this is an evil global variable
netcdf_file_local_path = ''
# this is used by users to confirm which varible to visualize
# and which dimension about that varible by /visualization/linechart/variable_name/dimension_y
# or /visualization/map/variable_name/dimension_x/dimension_y 
@visualization.route('/NetCDF/')
@login_required
def get_NetCDF_information():
    # this part is used flat_input.nc for test
    # later I will connect to the DB and enable users 
    # to choose a file by themselves

    # get the current app location
    # app/visualization
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    download_dir = APP_ROOT + '/tempData/'
    filename = 'flat_input.nc'
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
        if  'description' in netcdf_aim_file.variables[temp_variable_name].ncattrs():
            temp_variable_object = \
            NetCDFInformation(temp_variable_name, \
                          len(netcdf_aim_file.variables[temp_variable_name].dimensions), \
                          list(netcdf_aim_file.variables[temp_variable_name].dimensions), \
                          netcdf_aim_file.variables[temp_variable_name].description)
            variable_class_list.append(temp_variable_object)
        else:
            temp_variable_object = \
            NetCDFInformation(temp_variable_name, \
                          len(netcdf_aim_file.variables[temp_variable_name].dimensions), \
                          list(netcdf_aim_file.variables[temp_variable_name].dimensions))
            variable_class_list.append(temp_variable_object)

    return render_template('visualization/netcdf_information.html', \
                           filename=filename, \
                           variable_name_list=variable_name_list, \
                           variable_class_list=variable_class_list)

    # try netcdf_aim_file.variables['m_pp'].units to get the units of a variable
    # try netcdf_aim_file.variables['m_pp'].dimensions to get the dimensions of a variable
    # len(rootgrp.variables['m_pp'].dimensions) get length
    # access value of a varible netcdf_aim_file.variables['I_lw'][1][2][3] dimensions are (time, northing, easting)

    # get axis information
    # lons = rootgrp.variables['northing'][:]
    # lats = rootgrp.variables['easting'][:]
    # time = rootgrp.variables['time'][:]

# this function is used to create a csv file string from
# two arrays, the first one is for y axis and the second one is for x axis
def create_csv_file_string(y_array=[], y_axis_name='', x_array=[], x_axis_name=''):
    # first row is for label
    csv_string = x_axis_name + "," + y_axis_name + "\\n"
    # y_array and x_array must be the same dimension
    for count in range(len(y_array)):
        csv_string = csv_string + str(x_array[count]) + "," + str(y_array[count]) + "\\n"
    # print csv_string
    return csv_string
    

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
    exec_string = "for count in range(len(netcdf_aim_file.variables[\'"+vis_dimension+"\'])):\n    vis_dimension_data.append(netcdf_aim_file.variables[\'"+variable_name+"\']"
    for item in range(len(dimension_name_list)):
        if item == vis_dimension_index:
            exec_string = exec_string + "[count]"
        else:
            for temp_index in specify_dimension_index:
                if item == temp_index:
                    exec_string = exec_string + "[" + specify_dimension_chosen_index[specify_dimension_index.index(temp_index)] + "]"
    
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
        csv_string = create_csv_file_string(vis_dimension_list, vis_dimension, vis_dimension_data, variable_name)
    else:
        csv_string = create_csv_file_string(vis_dimension_data, variable_name, vis_dimension_list, vis_dimension)
    return csv_string

@visualization.route("/<path:path>")
def relation(path):
    # get the current app location
    # app/visualization
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    # the file extension could only be csv now
    if path.endswith('.csv'):
        # print APP_ROOT + "/tempData/" + path
        return send_from_directory(APP_ROOT + "/tempData/", path)
    elif path.endswith('.nc'):
        # print APP_ROOT + "/tempData/" + path
        return send_from_directory(APP_ROOT + "/tempData/", path)
    elif path.endswith('.js'):
        # this line is used to get the js filename
		filename_js = path.rsplit("/",1)[-1]
		return send_from_directory(APP_ROOT + "/../templates/visualization/js", filename_js)
    elif path.endswith(';'):
        # this line is used to get the js filename
        vis_param = path.rsplit("/",1)[-1]
        csv_string = line_chart_last_step(vis_param)
        return render_template('visualization/netcdf_visualization_results.html', csv_string=csv_string)
        



# this class record the variable dimension information
class VariableDimensionInformation:
    dimension_name = ''
    dimension_size = 0
    dimension_value_list = ''
    def __init__(self, name, size, value_list):
        self.dimension_name = name
        self.dimension_size = size
        self.dimension_value_list = value_list

# this list contains the chosen item dimension names
dimension_name_list = ''
chosen_x = ''
chosen_y = ''
variable_name = ''
# TODO: this version just works when time is number
# Lisa is creating some NetCDF, whose time is string
@visualization.route("/NetCDF/visualization/lineChart/<variablename>/<xaxis>/<yaxis>")
def line_chart_visualization(variablename='', xaxis='', yaxis=''):
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





