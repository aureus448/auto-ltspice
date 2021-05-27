"""
With a given data_sets.ini configuration listing the name of a dataset by HighVoltage-LowVoltage,
creates the expected dataset to be run upon by main.py
"""
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

    # TODO unfinalized logic that seperates each project into 'Name' and Temps to run
    to_run_sets = []
    for set, temps in data_sets:

        # Step 1: Collect Temperatures to Run
        if not temps:
            temp_sets = [27, 30, 35, 40, 45, 50]
            print(set, temp_sets)
        else:
            var_sets = temps.split(', ')
            temp_sets = []
            for val in var_sets:
                if '-' in val:
                    lower, upper = val.split('-')
                    results = [x for x in range(int(lower), int(upper) + 1)]
                else:
                    results = [int(val)]
                temp_sets += results
            print(set, temp_sets)
        to_run_sets.append((set, temp_sets))

    # Only check these folders for data
    folders_to_check = ['1x10', '2x4', '2x5', '3x3', '4x2', '5x2', '10x1']

    for dir in os.scandir(path):
        if dir.is_dir() and dir.name in folders_to_check:
            print(f'Main Directory: {dir.name}')

            # Highly inefficient but lazy method
            for file in os.scandir(dir.path):
                if file.is_file() and file.name.endswith('cir'):
                    print(f'Creating Dataset from {file.name}')

                    for set, temps in to_run_sets:
                        for temperatures in temps:
                            full_path = os.path.abspath(
                                f"Simulation_Sets\\{set}\\Temp{temperatures}\\{dir.name}\\")
                            os.makedirs(full_path, exist_ok=True)

                            high, low = set.split('-')  # Get high and low voltages expected
                            with open(file.path, 'r') as f:
                                ltspice_file = f.read()

                                # Update the necessary data (Temperature, High voltage, Low Voltage)
                                ltspice_file = ltspice_file.replace('temp=30', f'temp={temperatures}')
                                ltspice_file = ltspice_file.replace('900', low)
                                ltspice_file = ltspice_file.replace('1000', high)

                                with open(full_path + '\\' + file.name, 'w') as f:
                                    f.write(ltspice_file)  # write out the file to correct pathing
