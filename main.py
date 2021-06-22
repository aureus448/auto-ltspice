import os
import subprocess

import ltspice
import pandas as pd
from subprocess import Popen
import time
import configparser
from queue import Queue
import re
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
    data_name = [key for key in config.keys() if key != 'DEFAULT']

    # Run this script right next to Spice Simulation folder
    path = os.path.abspath('Simulation_Sets/')
    commands = []

    folders_to_check = ['1x10', '2x4', '2x5', '3x3', '4x2', '5x2', '10x1']
    for dataset in os.scandir(path):
        if dataset.is_dir() and dataset.name in data_name:  # ensure directory not file
            print(f'Running Data Analysis on {dataset.name}')
            for dir in os.scandir(dataset.path):
                if dir.is_dir():  # ensure directory not file
                    print(f'Main Directory: {dataset.name}/{dir.name}')
                    for sub_dir in os.scandir(dir.path):
                        if sub_dir.is_dir() and sub_dir.name in folders_to_check:  # ensure directory not file
                            print(f'Sub Directory: {dataset.name}/{dir.name}/{sub_dir.name} [{dataset.name}]')
                            for file in os.scandir(sub_dir.path):
                                if file.is_file() and file.name.endswith('cir'):
                                    print(f'Queueing LTspiceXVII on {file.name} [{dataset.name}]')
                                    commands.append(f"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe -Run \"{file.path}\"")

                        break

                break
        break
    print(f'\n{len(commands)} LTSpiceXVII runs have been queued - Expect a runtime of '
          f'{len(commands)*0.2+8:.2f} seconds ({(len(commands)*0.2+8)//60:.0f} minutes, '
          f'{(len(commands)*0.2+8)%60:.2f} seconds)')
    print('Beginning run in 10 seconds...')
    # time.sleep(10)
    # run_ltspice(commands)

    i = 1 # tracker of how many file(s) are run
    gigantor = pd.DataFrame()
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

                                    # Now that .txt has been generated - lets create biggo csv
                                    biggo = out.copy()

                                    to_rename = {
                                        'vbias':'Voltage (V)',
                                        'I(Vbias)':'Current (A)',
                                        'I(Vbias)*vbias':'Power (W)',
                                    }
                                    biggo.rename(columns=to_rename, inplace=True)
                                    rx = re.compile(r'-?\d+(?:\.\d+)?')
                                    rtemp = re.compile(r'\d+')
                                    contentList = list(map(int, rx.findall(filename)))
                                    temp = list(map(int, rx.findall(dir.name)))[0]
                                    biggo['Full Voltage']=dataset.name.split('-')[0]
                                    biggo['Shade Voltage']=dataset.name.split('-')[1]
                                    biggo['Temperature'] = temp
                                    biggo['File Name'] = filename
                                    biggo['# Of Cells']=contentList[0]*contentList[1]
                                    biggo['Series Cells']=contentList[0]
                                    biggo['Parallel Cells']=contentList[1]
                                    biggo['Shaded Cells']=contentList[2] if len(contentList)>2 else 0
                                    biggo['Shading %']=f'{((contentList[2]/(contentList[0]*contentList[1]))*100 if len(contentList)>2 else 0):.2f}'
                                    biggo['Solar Panel']=i
                                    biggo['IsShade']='1' if len(contentList)>2 and contentList[2] > 0 else 0
                                    gigantor = gigantor.append(biggo, ignore_index=True)
                                    i+= 1 # increment number of solar panels run on

    gigantor.to_csv('MEGASET.csv', index=False)