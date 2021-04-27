# auto-ltspice
Automatic Run of LTspiceXVII on .cir files with auto output generation*

Provided as-is, this was designed for use in my Research Project to automate the generation of LTspiceXVII simulation data of several .cir files and automatically parse and produce desired outputs via the ltspice library from PyPi.

While the code in its current state is very specific to my needs, this can be used as a template for future projects if it were designed to recursively search and perform analysis on all .cir files. The code is itself very easy to read, and consists of autorunning of several LTspice instances (as many as in a subdirectory, though this could be customized to run X amount at a time if desired) to generate runtime .raw files that can be used for data analysis or further development of research models. 

What the code currently does:
For help in designing future systems, here is an explanation of my code.
1. Given a 'Spice Simulation' directory, iterates through its subdirectories as 'main directories'
    > Inside each main directory a 'sub-directory' contains all .cir files to run
2. Iterating through each sub-directory, pulls the .cir files and appends them to a temporary list of files to run
3. Runs all LTspice instances simultaneously through python's subprocess Popen function for concurrent function access.
    > While dirty, my method just terminates all instances after a period of 10 seconds. For my models, the average runtime was 0.5s, meaning this was well after each program had successfully ran.
4. Through each .raw file generated within the sub-directory, use the ltspice library to collect the data (Knowing the expected variable names is not necessary other than knowing what data you need, the ltspice library can show all 'keys' if necessary and you are just experimenting)
5. Output the data in a .csv format (.txt file in my instance) with the column headers being the data collected, and the rows being the data for each collected data point (Example: Vbias, I(Vbias))
