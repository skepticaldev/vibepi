import os
import numpy as np
import configparser
import time
import csv
import termplotlib as tpl

config = configparser.ConfigParser()
offsets = configparser.ConfigParser()
config.read('config.ini')
offsets.read('offsets.ini')

# Load Offsets
xOff = offsets['VALUES']['x']
yOff = offsets['VALUES']['y']
zOff = offsets['VALUES']['z']

# Current file name
fileCount = int(config['SYSTEM']['fileCount'])

# Number of samples to average
nSamples = int(config['SAMPLING']['nSamples'])

# Delay between samples
delay = int(config['SAMPLING']['delay'])

# Frequency Interval
fi = int(config['SAMPLING']['frequencyInterval'])

# Spectrum Resolution 
sr = int(config['SAMPLING']['spectrumResolution'])

# Frequency Filter
ff = int(config['SAMPLING']['frequencyfilter'])

# BandWidth
bw = fi/sr

# Filter lines
# Value to iterate through FFT array to filter low frequencies
fl = int(ff/bw)

# Acquisition Time
aTime = 1/bw

# Acquisition Frequency
aFreq = 2.56 * fi

print(aTime)
print(aFreq)

dataDir = 'data/'+str(fileCount)
os.system(f'sudo mkdir -p {dataDir}')

_dir = os.path.dirname(os.path.realpath('__file__'))
        
i=1
while(i <= nSamples):
    print('Collecting samples:', i)
    timePath = dataDir+"/time_series_"+str(i)+".csv"
    os.system(f'sudo ./sample -f {aFreq} -t {aTime} -p {timePath} -xo {xOff} -yo {yOff} -zo {zOff}')
    
    time.sleep(1)

    # Processing Variables
    dt = 0.0
    n = 0
    t = []
    ax = []
    ay = []
    az = []

    _file = os.path.join(_dir, timePath)
    with open(_file) as csvFile:
        csvReader = csv.reader(csvFile, delimiter=',')
        lineCount = 0
        for row in csvReader:
            if lineCount==1:
                n = int(row[1])
            elif lineCount==2:
                dt = float(row[1])
            elif lineCount>=4:
                t.append(float(row[0]))
                ax.append(float(row[1]))
                ay.append(float(row[2]))
                az.append(float(row[3]))
            lineCount+=1
    
    # Processing
    # FFT
    fxhat = np.abs(np.fft.fft(ax,n))*(2/n)
    fyhat = np.abs(np.fft.fft(ay,n))*(2/n)
    fzhat = np.abs(np.fft.fft(az,n))*(2/n)   

    # PSD
    xPSD = ((fxhat*np.conj(fxhat))/bw)*0.5
    yPSD = ((fyhat*np.conj(fyhat))/bw)*0.5
    zPSD = ((fzhat*np.conj(fzhat))/bw)*0.5

    freq = bw*np.arange(n)

    for j in range(fl):
        fxhat[j] = 0
        fyhat[j] = 0
        fzhat[j] = 0

    fftPath = dataDir+"/fft.csv"

    fftFile = os.path.join(_dir, fftPath)

    if i>1 :
        with open(fftFile) as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',')
            lineCount = 0
            for row in csvReader:
                if lineCount>0:
                    xfft = float(row[1])
                    yfft = float(row[2])
                    zfft = float(row[3])
                    fxhat[lineCount-1] = (fxhat[lineCount-1] + xfft)/2
                    fyhat[lineCount-1] = (fyhat[lineCount-1] + yfft)/2
                    fzhat[lineCount-1] = (fzhat[lineCount-1] + zfft)/2
                lineCount+=1

    with open(fftFile, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["frequency","fft"])
        for j in range(sr+1):
            writer.writerow([freq[j], fxhat[j], fyhat[j], fzhat[j]])


    fig = tpl.figure()
    os.system(f'clear')
    fig.plot(freq[0:sr], fzhat[0:sr], width=60, height=15)
    fig.show()

    ix = np.argmax(fxhat[0:sr])
    iy = np.argmax(fyhat[0:sr])
    iz = np.argmax(fzhat[0:sr])

    print(freq[iz], fzhat[iz])

    fx = round(freq[ix], 1)
    fy = round(freq[iy], 1)
    fz = round(freq[iz], 1)

    ax = round(fxhat[ix], 2)
    ay = round(fyhat[iy], 2)
    az = round(fzhat[iz], 2)
    s = int(fz*60)

    os.system(f'python3 screen.py --ax {ax} --ay {ay} --az {az} --fx {fx} --fy {fy} --fz {fz} --spd {s}')
    i+=1

config['SYSTEM']['fileCount'] = str(fileCount+1);

with open ('config.ini', 'w') as configfile:
    config.write(configfile)
