import os

selection = 'test_2'
subscripts = os.path.dirname(os.path.realpath(__file__)) + '/'

data = '/home/matteo/Data/HFQPOs/J1550_2/'
data_info = data + 'info/'
database = data_info + 'database_test.csv'

logs = data_info + 'log_scripts/'
terminal_output = True

obsid_lists = '/home/matteo/Data/HFQPOs/Obsids/'
obsid_list = obsid_lists + selection + '.lst'
