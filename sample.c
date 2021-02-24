#include <stdio.h>
#include <pigpio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>

#define POWER_CTL	0x2D
#define BW_RATE		0x2C
#define DATA_FORMAT	0x31
#define DATAX0		0x32

#define READ_BIT	0x80
#define MULTI_BIT	0x40

const int maxFreq = 3200;
const int spiSpeed = 2000000;
const int spiFreqRef = 60000;
const int checkFreqSamples = 100;
const double defaultFreq = 512;
const double defaultTime = 4;

int readBytes(int handle, char *data, int count) {
	data[0] |= READ_BIT;
	if(count > 1) data[0] |= MULTI_BIT;
	return spiXfer(handle, data, data, count);
}

int writeBytes(int handle, char *data, int count) {
	if(count > 1) data[0] |= MULTI_BIT;
	return spiWrite(handle, data, count);
}

int main(int argc, char *argv[]) {

	int i;
	double aFreq = defaultFreq;
	double aTime = defaultTime;
	double xOff = 0.0, yOff = 0.0, zOff = 0.0;

	for(i=1; i < argc; i++) {
		if(strcmp(argv[i], "-f") == 0) {
			if(i+1 <= argc-1) {
				i++;
				aFreq = atof(argv[i]);
				if((aFreq < 1) || (aFreq > maxFreq)) {
					printf("Sampling rate not allowed!\n");
					return 1;
				}
			} else {
				printf("%s missing arguments!\n", argv[i]);
				return 1;
			}
		} else if(strcmp(argv[i], "-t") == 0) {
			if(i+1 <= argc-1) {
				i++;
				aTime = atof(argv[i]);
			} else {
				printf("%s missing arguments!\n", argv[i]);
				return 1;
			}
		} else if(strcmp(argv[i], "-xo") == 0) {
			if(i+1 <= argc-1) {
				i++;
				xOff = atof(argv[i]);
			} else {
				printf("%s missing arguments!\n", argv[i]);
				return 1;
			}
		} else if(strcmp(argv[i], "-yo") == 0) {
			if(i+1 <= argc-1) {
				i++;
				yOff = atof(argv[i]);
			} else {
				printf("%s missing arguments!\n", argv[i]);
				return 1;
			}
		} else if(strcmp(argv[i], "-zo") == 0) {
			if(i+1 <= argc-1) {
				i++;
				zOff = atof(argv[i]);
			} else {
				printf("%s missing arguments!\n", argv[i]);
				return 1;
			}
		}
	}

	// End command-line arguments

	int bufferSize = aFreq * aTime;
	int spiBufferSize = spiFreqRef * aTime;
	int h, bytes;
	char data[7];
	int16_t x, y, z;
	double dt = 1.0/aFreq;
	double sTime;

	if(gpioInitialise() < 0) {
		printf("GPIO failed!");
		return 1;
	}

	h = spiOpen(0, spiSpeed, 3);

	data[0] = POWER_CTL;
	data[1] = 0x08;
	writeBytes(h, data, 2);

	data[0] = BW_RATE;
	data[1] = 0x0F;
	writeBytes(h, data, 2);

	data[0] = DATA_FORMAT;
	data[1] = 0x02;
	writeBytes(h, data, 2);

	double *st, *sx, *sy, *sz;
	st = malloc(bufferSize * sizeof(double));
	sx = malloc(bufferSize * sizeof(double));
	sy = malloc(bufferSize * sizeof(double));
	sz = malloc(bufferSize * sizeof(double));

	double *rt, *rx, *ry, *rz;
	rt = malloc(spiBufferSize * sizeof(double));
	rx = malloc(spiBufferSize * sizeof(double));
	ry = malloc(spiBufferSize * sizeof(double));
	rz = malloc(spiBufferSize * sizeof(double));

	for(i=0; i < spiBufferSize; i++) {
		data[0] = DATAX0;
		bytes = readBytes(h, data, 7);
		if(bytes == 7) {
			x = (data[2]<<8) | (data[1]);
			y = (data[4]<<8) | (data[3]);
			z = (data[6]<<8) | (data[5]);

			rt[i] = time_time();
			rx[i] = (double) x;
			ry[i] = (double) y;
			rz[i] = (double) z;
		}
	}

	gpioTerminate();

	// Normalize time, i dont think doing this during sampling is a good pratice
	sTime = rt[0];
	for(i=0;i < spiBufferSize; i++) {
		rt[i] = rt[i]-sTime;
	}

	double cTime, nTime, tError;
	int j, nJ;

	cTime = 0.0;
	nJ = 0;
	nTime = rt[nJ];

	sx[0] = (double) rx[nJ];
	sy[0] = (double) ry[nJ];
	sz[0] = (double) rz[nJ];
	st[0] = cTime;

	for(i=1; i < bufferSize; i++) {
		cTime = (float)i * dt;
		tError = fabs(nTime - cTime);
		for(j = nJ; j < spiBufferSize; j++) {
			if(fabs(rt[j]-cTime) <= tError) {
				nJ = j;
				nTime = rt[nJ];
				tError = fabs(nTime - cTime);
			} else {
				break;
			}
		}
		st[i] = cTime;
		sx[i] = (double)rx[nJ];
		sy[i] = (double)ry[nJ];
		sz[i] = (double)rz[nJ];
	}

	for(i=0;i<100;i++) {
		printf("%.8f time, %.3f\n", st[i], sx[i]);
	}
}
