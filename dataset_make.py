import os
import configparser

# Makes datasets based on the data_sets.ini file
# Needed params: Full Voltage, Shade Voltage as well as Dataset name. (Just append to given list)

if __name__ == '__main__':

    # Run this script right next to Spice Simulation folder
    path = os.path.abspath('Spice Simulation/')
    commands = []

    # Read in datasets to make
    config = configparser.ConfigParser()
    config.read('data_sets.ini')

    data_sets = [[key, config[key]['temps']] for key in config.keys() if key != 'DEFAULT']
    print(data_sets)

    for set, temps in data_sets:
        if not temps:
            temp_sets = [27, 30, 35, 40, 45, 50]
            print(set, temp_sets)
        else:
            var_sets = temps.split(', ')
            temp_sets = []
            for val in var_sets:
                if '-' in val:
                    lower, upper = val.split('-')
                    results = [x for x in range(int(lower), int(upper)+1)]
                else: results = [int(val)]
                temp_sets += results
            print(set, temp_sets)

    for dir in os.scandir(path):
        if dir.is_dir() and dir.name not in data_name:  # ensure directory not file
            print(f'Main Directory: {dir.name}')
            for sub_dir in os.scandir(dir.path):
                if sub_dir.is_dir():  # ensure directory not file
                    print(f'Sub Directory: {dir.name}/{sub_dir.name}')
                    for Full_Voltage, Shade_Voltage, name in list(zip(full, shade, data_name)):
                        # Creates the dataset path
                        full_path = os.path.abspath(
                            f"Simulation_Sets\\{name}\\{dir.name}\\{sub_dir.name}\\")
                        os.makedirs(full_path, exist_ok=True)

                        # Iterate through files and add them to dataset
                        for file in os.scandir(sub_dir.path):
                            if file.is_file() and file.name.endswith('cir'):
                                print(f'Creating Datasets from {file.name}')
                                with open(file.path, 'r') as f:
                                    ltspice_file = f.readlines()

                                    for line in range(len(ltspice_file)):
                                        # Regex for search: (?<=[0-9]{4}  0 dc )\d+
                                        ltspice_file[line] = ltspice_file[line].replace('900', Shade_Voltage)
                                        ltspice_file[line] = ltspice_file[line].replace('1000', Full_Voltage)

                                    with open(full_path + '\\' + file.name, 'w') as f:
                                        f.write(''.join(ltspice_file))
                                    pass
