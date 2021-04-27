import os
import ltspice
import pandas as pd
from subprocess import Popen
import time


def run_ltspice(commands):
    procs = [Popen(i) for i in commands]
    time.sleep(10)
    for p in procs:
        p.terminate()
    # time.sleep(3) #wait for all processes to be guaranteed closed


if __name__ == '__main__':

    # Run this script right next to Spice Simulation folder
    path = os.path.abspath('Spice Simulation/')
    commands = []
    for dir in os.scandir(path):
        if dir.is_dir():  # ensure directory not file
            print(f'Main Directory: {dir.name}')
            for sub_dir in os.scandir(dir.path):
                if sub_dir.is_dir():  # ensure directory not file
                    print(f'Sub Directory: {dir.name}/{sub_dir.name}')
                    commands = []
                    for file in os.scandir(sub_dir.path):
                        if file.is_file() and file.name.endswith('cir'):
                            print(f'Running LTspiceXVII on {file.name}')
                            commands.append(f"C:\Program Files\LTC\LTspiceXVII\XVIIx64.exe -Run \"{file.path}\"")

                    run_ltspice(commands)
                    print(f'Done with LTspiceXVII data creation for {sub_dir}')

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
                            full_path = os.path.abspath(
                                f"Data Set\\{dir.name.replace('Temp', 'Temperature ')}\\{sub_dir.name}\\{filename}\\")
                            out.to_csv(full_path, sep='\t', float_format='%.5f', index=False)
