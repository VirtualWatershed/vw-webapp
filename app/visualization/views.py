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
from .classes import NetCDFInformation, VariableDimensionInformation, FrequenceDistributionInformation
import os, osr, util, numpy, json, time



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


@visualization.route("/CSV/3DVisualizationApplication", methods=['POST'])
def csv_visualization_interface_post():
    data = request.data
    # get the label row
    item_name_list = data.split('//')[1].split(',')
    # get filename
    filename = data.split('//')[0]
    # parse data and save it in tempData folder
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/tempData/'
    util.csv_interface_parse_save(data, download_dir)
    # print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    return 'Works!'


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
netcdf_filename=''
# this is used by users to confirm which varible to visualize
# and which dimension about that varible by 
# /visualization/linechart/variable_name/dimension_y
# or /visualization/map/variable_name/dimension_x/dimension_y 
@visualization.route('/NetCDF/<filename>')
@login_required
def get_NetCDF_information(filename=''):
    # get the current app location
    # app/visualization
    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/tempData/'
    filename_path = download_dir + filename
    global netcdf_file_local_path
    global netcdf_filename
    netcdf_filename = filename
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
    # print csv_string
    return csv_string

# this function is used to handle the last step of bar chart visualizion
# parse input and obtain data from netcdf
# x_axis contains data for x axis
# name_list[0] is the label for x axis
# name_list[1] is the label for y axis
def bar_chart_last_step(vis_param='', x_axis=[], y_axis=[], name_list=[]):
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
    
    # create vis_dimension_list
    vis_dimension_list = []
    for item in netcdf_aim_file.variables[vis_dimension]:
        vis_dimension_list.append(item)

    if bool_variable_x:
        for item in vis_dimension_list:
            y_axis.append(item)
        for item in vis_dimension_data:
            x_axis.append(item)
        # print 'bbbbbbbbb'
        # print x_axis
        name_list.append(variable_name)
        name_list.append(vis_dimension)
    else:
        for item in vis_dimension_data:
            y_axis.append(item)
        for item in vis_dimension_list:
            x_axis.append(item)
        # print 'xxxxxxxxxx'
        # print x_axis
        name_list.append(vis_dimension)
        name_list.append(variable_name)
        
    

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
    # this used to obtain parameters for NetCDF line chart visualization
    elif path.endswith('LineChartNetCDFParameters'):
        # this line is used to get the nc parameters
        vis_param = path.rsplit("/",1)[1]
        vis_param = util.replace_last(vis_param,'LineChartNetCDFParameters','')
        csv_string = line_chart_last_step(vis_param)
        return render_template('visualization/netcdf_visualization_line_chart_results.html', \
                               csv_string=csv_string)
    # this used to obtain parameters for NetCDF bar chart visualization
    elif path.endswith('BarChartNetCDFParameters'):
        # this line is used to get the nc parameters
        vis_param = path.rsplit("/",1)[1]
        vis_param = util.replace_last(vis_param,'BarChartNetCDFParameters','')
        x_axis = []
        x_name = ''
        y_axis = []
        y_name = ''
        name_list = []
        bar_chart_last_step(vis_param, x_axis, y_axis, name_list)
        x_name = name_list[0]
        y_name = name_list[1]
        # print 'aaaaaaaaaaaaa'
        # print x_axis
        return render_template('visualization/netcdf_visualization_bar_chart_results.html', \
                               x_axis=x_axis, x_name=x_name, \
                               y_axis=y_axis, y_name=y_name)
    elif path.endswith('3DApplicationResults/'):
        filename = path.rsplit('/')[-3]
        app_root = os.path.dirname(os.path.abspath(__file__))
        download_dir = app_root + '/tempData/'
        # item_name_list = util.csv_interface_obtain_labels(filename,download_dir)
        item_name_list = util.csv_interface_obtain_labels(filename, download_dir)
        input_filename = filename
        # print item_name_list
        # print input_filename
        return render_template('visualization/csv_visualization_results.html', \
                               item_name_list=item_name_list, \
                               input_filename=input_filename)

    elif path.endswith('3DApplicationResultsHistogram/'):
        # grab data from file
        filename = path.rsplit('/')[-3]
        app_root = os.path.dirname(os.path.abspath(__file__))
        download_dir = app_root + '/tempData/'
        input_file = open(download_dir + filename,'r')
        # the file just have one line
        data = input_file.readline()
        # print 'aaaaaaaaaaaaaaaaaa'
        # print data

        # -2 is because we need to remove section number and variable name
        element_num = len(data.split('//'))-2
        section_num = int(data.split('//')[1])
        class_information_list = []
        variablename = data.split('//')[0]

        # print 'aaaaaaaaaaaaaaaaaa'
        # print variablename

    
        # set up for loop to create a list of class
        for count in range(0,element_num):
            # initialize these array and lists
            section_results_number = []
            tab_name_list = []
            # get array
            aim_array = data.split('//')[count+2].split(',')
            # convert all the elements in the array into float
            aim_array = [float(i) for i in aim_array]
            # convert list into numpy array
            aim_array = numpy.asarray(aim_array)
            units = ''
            # for this part only we used variable name as standard name
            standard_name = variablename
            util.sort_section_number(aim_array, section_num, section_results_number, tab_name_list)
            # create the class object
            temp_object = FrequenceDistributionInformation(aim_array, section_results_number, tab_name_list, units, standard_name)
            class_information_list.append(temp_object)
        # this is used to compromise with my own part updates
        load_number = element_num
        return render_template('visualization/netcdf_visualization_histogram_results.html', \
               variablename=variablename, class_information_list=class_information_list, load_number=load_number)

    # all the data about certain variable in a NetCDF file will be
    # transfered as json type data
    elif path.endswith('NetCDFMapData'):
        # /filename:variablename:3:x_dimension:y_dimension:NetCDFMapData or
        # /filename:variablename:4:x_dimension:y_dimension:NetCDFMapData
        
        app_root = os.path.dirname(os.path.abspath(__file__))
        download_dir = app_root + '/tempData/'

        filename = path.split(':')[0]
        variable_name = path.split(':')[1]
        # open netcdf file
        netcdf_file_local_path = download_dir + filename
        netcdf_aim_file = Dataset(netcdf_file_local_path, "r")
        # grab dimension name list
        dimension_name_list = list(netcdf_aim_file.variables[variable_name].dimensions)
        dimension_num = path.split(':')[2]
        lat = path.split(':')[3]
        lon = path.split(':')[4]
        lon_length = len(netcdf_aim_file.dimensions[lon])
        lat_length = len(netcdf_aim_file.dimensions[lat])
        # create json to store the variable data
        # and because we will visualize data on a map
        # the visualization data will be 3D (use 2D as x and y and display the
        # last dimension the data on a map)
        # or will be 4D (use 2D data as x and y, when users click on a element,
        # then display the the left 2D in a line chart)
        # for 4D we can also use slider. e.g. temperature is a 4D variable
        # with (lat, lon, time, temperture)
        json_projects = []

        # use different for loop if it is 4D, now only it works for 3D
        # now the two loops are the same
        if int(dimension_num) == 3:
            # need to figure out which dimension is at first
            if dimension_name_list.index(lat) == 0:
                for count_lon in range(0,lon_length):
                    temp_array = ''
                    for count_lat in range(0,lat_length):
                        # python dictionary does not like array in it, so have to use string
                        temp_array = temp_array + str(netcdf_aim_file.variables[variable_name][count_lat][count_lon]) +","
                    # remove the last ,
                    # don't know why temp_array.rstrip(',') does not work
                    temp_change_str_into_list = temp_array.split(',')
                    temp_change_str_into_list.pop()
                    temp_array = ','.join(temp_change_str_into_list)
                    json_projects.append({"data" : temp_array})
            else:
                for count_lon in range(0,lon_length):
                    temp_array = ''
                    for count_lat in range(0,lat_length):
                        # python dictionary does not like array in it, so have to use string
                        temp_array = temp_array + str(netcdf_aim_file.variables[variable_name][count_lon][count_lat]) +","
                    # remove the last ,
                    # don't know why temp_array.rstrip(',') does not work
                    temp_change_str_into_list = temp_array.split(',')
                    temp_change_str_into_list.pop()
                    temp_array = ','.join(temp_change_str_into_list)
                    json_projects.append({"data" : temp_array})

            json_projects = json.dumps(json_projects)
        elif int(dimension_num) == 4:
            # create executable string for 4D to find out the order of each dimension
            # two of the dimensions are variable itself and "another one"
            # for the "another one" we can use 0 to specify its value for now
            exec_string='temp_array = temp_array + str(netcdf_aim_file.variables[variable_name]'
            lat_dimension_index = dimension_name_list.index(lat)
            lon_dimension_index = dimension_name_list.index(lon)
            for count in range(3):
                if count == lon_dimension_index:
                    exec_string  = exec_string + '[count_lon]'
                elif count == lat_dimension_index:
                    exec_string  = exec_string + '[count_lat]'
                else:
                    exec_string = exec_string + '[0]'

            exec_string = exec_string + ')+' +"','"
            # print exec_string

            for count_lon in range(0,lon_length):
                temp_array = ''
                for count_lat in range(0,lat_length):
                    # python dictionary does not like array in it, so have to use string
                    # exec_string should be something like this
                    # temp_array = temp_array + str(netcdf_aim_file.variables[variable_name][0][count_lon][count_lat]) +","
                    exec exec_string
                # remove the last ,
                # don't know why temp_array.rstrip(',') does not work
                temp_change_str_into_list = temp_array.split(',')
                temp_change_str_into_list.pop()
                temp_array = ','.join(temp_change_str_into_list)
                json_projects.append({"data" : temp_array})

            json_projects = json.dumps(json_projects)
        return json_projects
    # all the data about certain variable in a NetCDF file will be
    # transfered as json type data, lat and lon as variables
    # and they are decided by the same dimensions
    elif path.endswith('NetCDFMapDataOther'):
        # /filename:variablename:3:x_dimension:y_dimension:NetCDFMapDataOther or
        # /filename:variablename:4:x_dimension:y_dimension:NetCDFMapDataOther
        
        app_root = os.path.dirname(os.path.abspath(__file__))
        download_dir = app_root + '/tempData/'

        filename = path.split(':')[0]
        variable_name = path.split(':')[1]
        # print filename
        # open netcdf file
        netcdf_file_local_path = download_dir + filename
        netcdf_aim_file = Dataset(netcdf_file_local_path, "r")
        # grab dimension name list
        dimension_name_list = list(netcdf_aim_file.variables[variable_name].dimensions)
        dimension_num = path.split(':')[2]
        lat = path.split(':')[3]
        lon = path.split(':')[4]
        lon_length = len(netcdf_aim_file.variables[lon])
        lat_length = len(netcdf_aim_file.variables[lat])
        lon_dimension_list = list(netcdf_aim_file.variables[lon].dimensions)
        lat_dimension_list = list(netcdf_aim_file.variables[lat].dimensions)
        # create json to store the variable data
        # and because we will visualize data on a map
        # the visualization data will be 3D (use 2D as x and y and display the
        # last dimension the data on a map)
        # or will be 4D (use 2D data as x and y, when users click on a element,
        # then display the the left 2D in a line chart)
        # for 4D we can also use slider. e.g. temperature is a 4D variable
        # with (lat, lon, time, temperture)
        # for 3D we won't use json_projects_final
        # for 4D we will use json_projects_final for the final json outputs


        # use different for loop if it is 4D, now only it works for 3D
        # now the two loops are almost the same
        if int(dimension_num) == 3:
            json_projects = []
            first_dimension_length =  len(netcdf_aim_file.dimensions[dimension_name_list[0]])
            second_dimension_length =  len(netcdf_aim_file.dimensions[dimension_name_list[1]])

            for count_y in range(0,first_dimension_length):
                temp_array = ''
                for count_x in range(0,second_dimension_length):
                    # python dictionary does not like array in it, so have to use string
                    temp_array = temp_array + str(netcdf_aim_file.variables[variable_name][count_y][count_x]) +","
                # remove the last ,
                # don't know why temp_array.rstrip(',') does not work
                temp_change_str_into_list = temp_array.split(',')
                temp_change_str_into_list.pop()
                temp_array = ','.join(temp_change_str_into_list)
                json_projects.append({"data" : temp_array})

            json_projects = json.dumps(json_projects)

            return json_projects

        elif int(dimension_num) == 4:
            '''
            4D json file will be like this:
            {
                "min_value":xxx,
                "max_value":xxx,
                "x_num":xxx,
                "y_num":xxx,
                "max_lat":xxx,
                "max_lon":xxx,
                "min_lat":xxx,
                "min_lon":xxx,
                "time":['2014-1-1',...,],
                "location":[{"lat":123,
                            "lon":234,
                            "x_location":xxx,
                            "y_location":xxx,
                            "data":[1,2,3,4]},
                             {...}
                           ]
            }
            x_num means how many elements we have alone x-axis
            y_num means how many elements we have alone y-axis
            (x_location,y_location) is the coordinate in the 2D map
            min_value is the minimum value of all location "data"
            time should have as many elements as data
            which means we can find data timestamp from time array
            !!!!
            max_lat,max_lon,min_lat,min_lon are used to locate the 2D map
            in google map. I know this is not right if the data is not rectangular
            !!!!
            '''
            # NOTICE!!!!!
            # for this version the lat and lon should be decided by the same two dimensions
            # and lat_lon_first_dimension_length is for 2D map y-axis
            # and lat_lon_second_dimension_length is for 2D map x-axis
            lat_lon_first_dimension_length = len(netcdf_aim_file.dimensions[lon_dimension_list[0]])
            lat_lon_second_dimension_length = len(netcdf_aim_file.dimensions[lon_dimension_list[1]])
            # other_dimension_name is for the dimension that is not decided lat and lon
            other_dimension_name = ''
            for item in dimension_name_list:
                if item not in lon_dimension_list:
                    other_dimension_name = item
            
            other_dimension_length =  len(netcdf_aim_file.dimensions[other_dimension_name])

            # create executable string for 4D to find out the order of each dimension
            # two of the dimensions are variable itself and "another one"
            # for the "another one" we can use 0 to specify its value for now
            exec_string='temp_array = temp_total_array['
            lat_lon_first_dimension_index = dimension_name_list.index(lon_dimension_list[0])
            lat_lon_second_dimension_index = dimension_name_list.index(lon_dimension_list[1])
            # dynamically create execuation string
            # exec_string should be something like:
            # temp_array = temp_total_array[:,count_lat_lon_first,count_lat_lon_second].tolist()
            for count in range(3):
                if count == lat_lon_first_dimension_index:
                    exec_string  = exec_string + 'count_lat_lon_first,'
                elif count == lat_lon_second_dimension_index:
                    exec_string  = exec_string + 'count_lat_lon_second,'
                else:
                    exec_string = exec_string + ':,'
            # .item() is used to convert numpy.float into float
            exec_string = exec_string + '].tolist()'

            # print exec_string
            json_projects = {}
            json_projects_location = []
            json_projects_final = {}
            
            # get all the data into an numpy array
            temp_total_array = netcdf_aim_file.variables[variable_name][:][:][:]
            # get the min and max lat and lon
            min_lat = netcdf_aim_file.variables[lat][:][:].min().item()
            max_lat = netcdf_aim_file.variables[lat][:][:].max().item()
            min_lon = netcdf_aim_file.variables[lon][:][:].min().item()
            max_lon = netcdf_aim_file.variables[lon][:][:].max().item()
            # get the max and min value of the chosen variable
            min_value = netcdf_aim_file.variables[variable_name][:][:][:].min().item()
            max_value = netcdf_aim_file.variables[variable_name][:][:][:].max().item()
            # record time
            start_time = time.time()
            
            # create json file
            temp_lat_array = netcdf_aim_file.variables[lat][:][:]
            temp_lon_array = netcdf_aim_file.variables[lon][:][:]
            for count_lat_lon_first in range(0,lat_lon_first_dimension_length):
                for count_lat_lon_second in range(0,lat_lon_second_dimension_length):
                    # numpy_array[:,1,1] means obtain all data from numpy_array[all][1][1]
                    # temp_array = temp_total_array[:,count_lat_lon_first,count_lat_lon_second].tolist()
                    exec exec_string
                    json_projects = {}
                    json_projects['data'] = temp_array
                    # lat and lon should be decided by two dimensions in this version application
                    # .item() is used to convert numpy.float into float
                    json_projects['lat'] = temp_lat_array[count_lat_lon_first][count_lat_lon_second].item()
                    json_projects['lon'] = temp_lon_array[count_lat_lon_first][count_lat_lon_second].item()
                    json_projects['x_location'] = count_lat_lon_second
                    json_projects['y_location'] = count_lat_lon_first
                    json_projects_location.append(json_projects)

            print('--- %s second for extration and creating json---' % (time.time() - start_time))
            start_time = time.time()
            
            # this is used to store other dimension information
            temp_array = []
            for count_other in range(0,other_dimension_length):
                temp_array.append(netcdf_aim_file.variables[other_dimension_name][count_other].item())
            
            # add location
            json_projects_final['location'] = json_projects_location
            
            json_projects_final['y_num'] = lat_lon_first_dimension_length
            json_projects_final['x_num'] = lat_lon_second_dimension_length
            json_projects_final['min_value'] = min_value
            json_projects_final['max_value'] = max_value
            # record the min and max of lat and lon
            json_projects_final['min_lon'] = min_lon
            json_projects_final['min_lat'] = min_lat
            json_projects_final['max_lon'] = max_lon
            json_projects_final['max_lat'] = max_lat
            
            # add another dimension
            json_projects_final[other_dimension_name] = temp_array
            json_projects_final = json.dumps(json_projects_final)
            
            # print the total time
            print('--- %s second for final json---' % (time.time() - start_time))

            return json_projects_final
            
            
            
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
        
    return render_template('visualization/netcdf_line_chart.html', \
           variablename=variablename, xaxis=xaxis, yaxis=yaxis, \
           dimension_information_list=dimension_information_list, \
           specify_dimension_list=specify_dimension_list)

# this part is used to handle histogram
# start means the start frame of the variable
# end means the end frame of the variable
@visualization.route("/NetCDF/histogram/<variablename>/<xaxis>/<sectionNumber>/<start>/<end>/histogramVisualization")
def netcdf_histogram_visualization(variablename='', xaxis='', start='0', end='0', sectionNumber='1'):
    global netcdf_file_local_path
    # open netcdf file
    netcdf_aim_file = Dataset(netcdf_file_local_path, "r")
    
    element_num = len(netcdf_aim_file.dimensions[xaxis])
    section_num = int(sectionNumber)
    class_information_list = []
    temp_dim_handle = netcdf_aim_file.variables[variablename]
    start_frame = int(start)
    end_frame = int(end)
    # load_num means how many frames to visualize each time
    load_number = 5
    # if start==end==0 means this is the first step
    if start_frame==0 and end_frame==0:
        if element_num <= load_number:
            # element_num-1 because the index starts from 0
            end_frame = element_num - 1
        else:
            end_frame = load_number
        # set up for loop to create a list of class
        # for count in range(0,element_num):
        for count in range(start_frame,end_frame):
            # record time
            # start_time = time.time()
            # initialize these array and lists
            section_results_number = []
            tab_name_list = []
            # TODO need to dynamically obtain data, not just first dimension
            aim_array = temp_dim_handle[count].flatten()
            units = ''
            standard_name = ''
            util.sort_section_number(aim_array, section_num, section_results_number, tab_name_list)
            # .ncattrs() is used to list all the attributes of the chosen variable
            if  'units' in temp_dim_handle.ncattrs():
                units = temp_dim_handle.units
            if  'standard_name' in temp_dim_handle.ncattrs():
                standard_name = temp_dim_handle.standard_name
            temp_object = FrequenceDistributionInformation(aim_array, section_results_number, tab_name_list, units, standard_name)
            class_information_list.append(temp_object)
            # print('--- %s second ---' % (time.time() - start_time))
    
        return render_template('visualization/netcdf_visualization_histogram_results.html', \
               variablename=variablename, class_information_list=class_information_list, \
               load_number=load_number, element_num=element_num)
    # if not the first step, we need return a json file contains all the information to visualize
    '''
    json file is like this:
    {
        "timestamp":[
             {
                 "standard_name": "XXX",
                 "units": "YYY",
                 "section_results_number":[1,2,3],
                 "tab_name_list": ['aatobb','bbtocc']
             },
             {}
        ]
    }
    information is based on time, this means json[y] is the information for timestamp y
    '''    
    # for this part, start and end should be all less than element_num
    # and this is controlled in netcdf_histogram_visualization_results.js
    # I don't know why elif does not work
    # elif start_frame<element_num and end_frame<=element_num:
    if start_frame<element_num and end_frame<=element_num:
        json_final = {}
        json_timestamp = []
        # !!!!!!!!!!!!!!!!!!!!
        # set up for loop to create a json file
        for count in range(start_frame,end_frame):
            # record time
            # start_time = time.time()
            # initialize these array and lists
            section_results_number = []
            tab_name_list = []
            json_projects = {}
            # TODO need to dynamically obtain data, not just first dimension
            aim_array = temp_dim_handle[count].flatten()
            units = ''
            standard_name = ''
            util.sort_section_number(aim_array, section_num, section_results_number, tab_name_list)
            # .ncattrs() is used to list all the attributes of the chosen variable
            if  'units' in temp_dim_handle.ncattrs():
                units = temp_dim_handle.units
            if  'standard_name' in temp_dim_handle.ncattrs():
                standard_name = temp_dim_handle.standard_name

            json_projects['units'] = units
            json_projects['standard_name'] = standard_name
            json_projects['section_results_number'] = section_results_number
            json_projects['tab_name_list'] = tab_name_list
            json_timestamp.append(json_projects)

        json_final['timestamp'] = json_timestamp
        json_final = json.dumps(json_final)
        return json_final
    else:
        # we should return an error page is start and end is bigger than element_num
        return 'error'

# I am really confused why return render_template does not work in the post request
@visualization.route("/Histogram/3DVisualizationApplication", methods=['POST'])
def histogram_visualization_interface_post():
    # data should be 'section_number//arrayT0//arrayT1//...'
    # arrayTM is for timestamp TM, and it is an array like
    # 'float0,float1,float2...'
    data = request.data

    # get the variable name
    filename = data.split('//')[0]

    app_root = os.path.dirname(os.path.abspath(__file__))
    download_dir = app_root + '/tempData/'

    output_file = open(download_dir + filename, 'w+')
    output_file.write(data)
    output_file.close()

    return 'works!'




# TODO: this version just works when time is number
# Lisa is creating some NetCDF, whose time is string
@visualization.route("/NetCDF/barChart/<variablename>/<xaxis>/<yaxis>")
def netcdf_bar_chart_visualization(variablename='', xaxis='', yaxis=''):
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
        
    return render_template('visualization/netcdf_bar_chart.html', \
           variablename=variablename, xaxis=xaxis, yaxis=yaxis, \
           dimension_information_list=dimension_information_list, \
           specify_dimension_list=specify_dimension_list)

# this part is for netcdf map visualization
# with lat and lon as dimensions
@visualization.route('/NetCDF/<map_information>/2DMapVisualizationLatLon')
@login_required
def netcdf_map_visualization_lat_lon(map_information=''):
    # TODO I need to remove the global variable filename
    global netcdf_filename
    # map_information formats should be:
    # /filename:variablename:3:x_dimension:y_dimension:NetCDFMapDataLatLon or
    # /filename:variablename:4:x_dimension:y_dimension:NetCDFMapDataLatLon
    # However the format are
    # /variablename:3:x_dimension:y_dimension:NetCDFMapDataLatLon or
    # /variablename:4:x_dimension:y_dimension:NetCDFMapDataLatLon
    map_information_list = map_information.split(':')
    return render_template('visualization/netcdf_map_lat_lon.html', variablename=map_information_list[0],\
                           dimensionNum=map_information_list[1],lat=map_information_list[2],\
                           lon=map_information_list[3], filename=netcdf_filename)
'''
    return render_template('visualization/netcdf_map.html', filename=map_information_list[0], variablename=map_information_list[1],\
                           dimensionNum=map_information_list[2],lat=map_information_list[3],\
                           lon=map_information_list[4])
'''

# this part is for netcdf map visualization
# without lat and lon as dimensions
@visualization.route('/NetCDF/<map_information>/2DMapVisualizationOther')
@login_required
def netcdf_map_visualization_other(map_information=''):
    # TODO I need to remove the global variable filename
    global netcdf_filename
    # map_information formats should be:
    # /filename:variablename:3:x_dimension:y_dimension:NetCDFMapDataOther or
    # /filename:variablename:4:x_dimension:y_dimension:NetCDFMapDataOther
    # However the format are
    # /variablename:3:x_dimension:y_dimension:NetCDFMapDataOther or
    # /variablename:4:x_dimension:y_dimension:NetCDFMapDataOther
    map_information_list = map_information.split(':')
    return render_template('visualization/netcdf_map_other.html', variablename=map_information_list[0],\
                           dimensionNum=map_information_list[1],lat=map_information_list[2],\
                           lon=map_information_list[3], filename=netcdf_filename)
'''
    return render_template('visualization/netcdf_map.html', filename=map_information_list[0], variablename=map_information_list[1],\
                           dimensionNum=map_information_list[2],lat=map_information_list[3],\
                           lon=map_information_list[4])
'''


