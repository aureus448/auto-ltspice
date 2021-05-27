import os
import subprocess

import ltspice
import pandas as pd
from subprocess import Popen
import time
import configparser
from queue import Queue

def run_ltspice(commands):
    procs = Queue()
    s = subprocess.STARTUPINFO(dwFlags=subprocess.STARTF_USESHOWWINDOW, wShowWindow=subprocess.SW_HIDE)
    sleep = 0.2
    for i in range(len(commands)):
        procs.put((Popen(commands[i], startupinfo=s), time.time()))
        time.sleep(sleep)
        # Begins checking after at least X seconds has passed
        if not procs.empty() and sleep*i > 8:
            process = procs.get()
            if time.time() - process[1] > 8:
                process[0].terminate()
            else:
                procs.put(process) # not ready-put back in queue (at end) and continue looping
                continue

    while not procs.empty():
        process = procs.get()
        if time.time() - process[1] > 8:
            process[0].terminate()
        else:
            procs.put(process) # not ready-put back in queue (at end)

#TODO
# Regex replace 1000-> 800
# 900 -> 700

if __name__ == '__main__':

    # Read in datasets to make
    config = configparser.ConfigParser()
    config.read('data_sets.ini')
    full = config['Full Voltage']['voltages'].split(', ')
    shade = config['Shade Voltage']['voltages'].split(', ')
    data_name = config['Names']['name'].split(', ')

    # Run this script right next to Spice Simulation folder
    path = os.path.abspath('Spice Simulation/')
    commands = []

    print('WARNING: Computer WIll be useless for 20-30 minutes. Program begins in 5 seconds.')
    time.sleep(5)

    for dataset in os.scandir(path):
        if dataset.is_dir() and dataset.name in data_name:  # ensure directory not file
            print(f'Running Data Analysis on {dataset.name}')
            for dir in os.scandir(dataset.path):
                if dir.is_dir():  # ensure directory not file
                    print(f'Main Directory: {dataset.name}/{dir.name}')
                    for sub_dir in os.scandir(dir.path):
                        if sub_dir.is_dir():  # ensure directory not file
                            print(f'Sub Directory: {dataset.name}/{dir.name}/{sub_dir.name} [{dataset.name}]')
                            for file in os.scandir(sub_dir.path):
                                if file.is_file() and file.name.endswith('cir'):
                                    print(f'Queueing LTspiceXVII on {file.name} [{dataset.name}]')
                                    commands.append(f"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe -Run \"{file.path}\"")

    run_ltspice(commands)

    for dataset in os.scandir(path):
        if dataset.is_dir() and dataset.name in data_name:  # ensure directory not file
            print(f'Running Data Analysis on {dataset.name}')
            for dir in os.scandir(dataset.path):
                if dir.is_dir():  # ensure directory not file
                    print(f'Main Directory: {dataset.name}/{dir.name}')
                    for sub_dir in os.scandir(dir.path):
                        if sub_dir.is_dir():  # ensure directory not file
                            print(f'Sub Directory: {dataset.name}/{dir.name}/{sub_dir.name} [{dataset.name}]')
                            for file in os.scandir(sub_dir.path):  # rescan directory after modifying and creating .raw files
                                if file.is_file() and file.name.endswith('raw'):
                                    print(f'Creating Datasheet Output from {file.name}')
                                    l = ltspice.Ltspice(file.path)
                                    l.parse()
                                    vbias = l.get_data('vbias')
                                    I_Vbias = l.get_data('I(vbias)')
                                    P_Vbias = vbias * I_Vbias

                                    out = pd.DataFrame()
                                    out['vbias'] = vbias
                                    out['I(Vbias)'] = I_Vbias
                                    out['I(Vbias)*vbias'] = P_Vbias

                                    # These three lines get the filename from the file (sans .raw), name it .txt, find full
                                    # path to corresponding dataset, and then output at that location
                                    filename = file.name.split('.')[0] + '.txt'
                                    dir_path = os.path.abspath(
                                        f"Data Set\\{dataset.name}\\{dir.name.replace('Temp', 'Temperature ')}\\{sub_dir.name}\\")
                                    os.makedirs(dir_path, exist_ok=True)
                                    full_path = os.path.abspath(f"{dir_path}\\{filename}\\")
                                    out.to_csv(full_path, sep='\t', float_format='%.5f', index=False)
