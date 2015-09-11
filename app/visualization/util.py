# this is used to force division to be floating point
# e.g. 4/5=0.8
from __future__ import division
import numpy as np

#This function is used to get the name of each item
#and remove the offset and write the results into temp file
#The users need to remove the temp file by themselves
def getItemName(downloadDir='', filename='', itemNameList=[], rowOffset=0, rowOffset2=0, columnOffset=0):
    inputFile = open(downloadDir + filename,'r')
    itemList = []
    outputFile = open(downloadDir + 'temp' + filename, 'w+')
    # outputFile = open(downloadDir + 'input.csv', 'w+')

    #skip first rowOffset rows
    for i in range(0, int(rowOffset)):
        itemList = inputFile.readline()

    #obtain item name from the list
    #go back to the start of the file
    itemNameLine = inputFile.readline()
    itemList = itemNameLine.rstrip().split(',')

    #remove the first columnOffset elements
    for i in range(0, int(columnOffset)):
        itemList.pop(0)

    #does not work to do this: itemNameList = itemList
    #should use the following method
    for item in itemList:
        itemNameList.append(str(item))

    #skip second rowOffset rows
    for i in range(0, int(rowOffset2)):
        itemList = inputFile.readline()

    #add the item name list into csv file
    tempList = []
    tempList = itemNameLine.split(',')
    outputFile.write(','.join(tempList))

    #skip first columnOffset columns
    #this is used to get every line of this file
    for line in inputFile:
        tempList = line.split(',')
        for i in range(0, int(columnOffset)):
            tempList.pop(0)        
        outputFile.write(','.join(tempList))
        tempList = []

    #close file
    inputFile.close()
    outputFile.close()

# this function is used for csv interface
# create a file from the input data
# save it into tempData folder
def csv_interface_parse_save(data='', download_dir=''):
    temp_list = data.split('//')
    # get and remove filename from list
    filename = temp_list.pop(0)
    # file content
    # file_content = "/n".join(temp_list)
    # write file content into a file
    # no meta data should be in this input data
    output_file = open(download_dir + filename, 'w+')
    for line in temp_list:
        line = line + '\n'
        output_file.write(line)

    # close file
    output_file.close()

# this function is used to grab all the labels of
# a csv file. The csv file should not have any metadata
def csv_interface_obtain_labels(filename='', download_dir=''):
    input_file = open(download_dir + filename,'r')
    csv_label_list = input_file.readline().replace('\n','').split(',')
    input_file.close()
    return csv_label_list
    


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


# this is from:
# http://stackoverflow.com/questions/3675318/how-to-replace-the-some-characters-from-the-end-of-a-string
# this function is used to replace one part of a string from the 
# end. e.g. replace_last(str, '2', 'x'), this means replace
# the first 2 from the end of str into x for once
def replace_last(source_string, replace_what, replace_with):
    head, sep, tail = source_string.rpartition(replace_what)
    return head + replace_with + tail


# This function is used to check if the upload file type is csv
def allowed_file_csv(filename):
    # define the allowed extension
    allowed_extension_list = ['csv']
    # get extension part
    file_type = filename.rsplit(".",1)[1]
    return file_type in allowed_extension_list

# This function is used to check if the upload file type is NetCDF
def allowed_file_netcdf(filename):
    # define the allowed extension
    allowed_extension_list = ['nc']
    # get extension part
    file_type = filename.rsplit(".",1)[1]
    return file_type in allowed_extension_list

# This function is used to sort a numpy array and 
# return a 1D list with m numbers, each number means 
# the number of array elements in the section from min+x*(max-min)/section_number
# to min+(x+1)(max-min)/section_number, this function also returns the tab name list
def sort_section_number(numpy_input_array=[], section_number=1, section_results_number=[],tab_name_list=[]):
    ordered_array = np.sort(numpy_input_array)
    max_value = ordered_array[numpy_input_array.size-1]
    min_value = ordered_array[0]
    interval_value = (max_value-min_value)/section_number
    # this is used to record elements section numbers
    temp_results_number = [0]*section_number
    for item in ordered_array:
        for count in range(0,section_number):
            # record the number of elements in each section
            if item>=min_value+count*interval_value and item<=min_value+(count+1)*interval_value:
                temp_results_number[count] = temp_results_number[count] + 1
    # create tab name
    for count in range(0,section_number):
        # 2 digits precisions for float
        bound_floor = "%.2f" % (min_value+count*interval_value)
        bound_cell = "%.2f" % (min_value+(count+1)*interval_value)
        tab_name_list.append(str(bound_floor)+' to '+str(bound_cell))
    # push results into section_results_number
    for item in temp_results_number:
        section_results_number.append(item)



