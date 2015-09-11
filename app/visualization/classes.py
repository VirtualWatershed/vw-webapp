import numpy as np

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


# this class record the variable dimension information
class VariableDimensionInformation:
    dimension_name = ''
    dimension_size = 0
    dimension_value_list = ''
    def __init__(self, name, size, value_list):
        self.dimension_name = name
        self.dimension_size = size
        self.dimension_value_list = value_list

# this class is used for histograms of frequence distribution visualization
class FrequenceDistributionInformation:
    data = np.array([])
    # bar chart y values
    section_results_number = []
    # bar chart x tabs
    tab_name_list = []
    title = ''
    units =''
    standard_name = ''
    def __init__(self, data_input, section_results_number_input, tab_name_list_input, units_input, standard_name_input):
        self.data = data_input
        self.section_results_number = section_results_number_input
        self.tab_name_list = tab_name_list_input
        self.units = units_input
        self.standard_name = standard_name_input
        

