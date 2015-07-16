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
