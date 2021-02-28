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
nSamples = int(config['DEFAULT']['nSamples'])

# Delay between samples
delay = int(config['DEFAULT']['delay'])

# Frequency Interval
fi = int(config['DEFAULT']['frequencyInterval'])

# Spectrum Resolution 
sr = int(config['DEFAULT']['spectrumResolution'])

# BandWidth
bw = fi/sr

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
    fzhat = np.abs(np.fft.fft(az,n))*(2/n)
    # PSD
    zPSD = ((fzhat*np.conj(fzhat))/bw)*0.5

    freq = bw*np.arange(n)

    fftPath = dataDir+"/fft.csv"
    fftFile = os.path.join(_dir, fftPath)

    if i>1 :
        with open(fftFile) as csvFile:
            csvReader = csv.reader(csvFile, delimiter=',')
            lineCount = 0
            for row in csvReader:
                if lineCount>0:
                    zfft = float(row[1])
                    fzhat[lineCount-1] = (fzhat[lineCount-1] + zfft)/2
                lineCount+=1

    with open(fftFile, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["frequency","fft"])
        for j in range(sr+1):
            writer.writerow([freq[j], fzhat[j]])


    fig = tpl.figure()
    os.system(f'clear')
    fig.plot(freq[0:sr], fzhat[0:sr], width=60, height=15)
    fig.show()

    if i == nSamples:
        index = np.argmax(fzhat[0:sr])
        print(freq[index], fzhat[index])

    i+=1

config['SYSTEM']['fileCount'] = str(fileCount+1);

with open ('config.ini', 'w') as configfile:
    config.write(configfile)
