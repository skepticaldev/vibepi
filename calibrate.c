#include <stdio.h>
#include <pigpio.h>
#include <time.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>

#define POWER_CTL 	0x2D
#define BW_RATE 	0x2C
#define DATA_FORMAT	0x31
#define DATAX0		0x32

#define READ_BIT	0x80
#define MULTI_BIT	0x40


const int spiSpeed = 2000000;
const int coldStartBuffer = 10;
const double coldDelay = 0.1;

int readBytes(int handle, char *data, int count) {
	data[0] |= READ_BIT;
	if(count > 1) data[0] |= MULTI_BIT;
	return spiXfer(handle, data, data, count);
}

int writeBytes(int handle, char *data, int count) {
	if(count > 1) data[0] |= MULTI_BIT;
	return spiWrite(handle, data, count);
}

void avgData(int h, int bufferSize, double* avgX, double* avgY, double* avgZ, double xOS, double yOS, double zOS) {

	int16_t x, y, z;
	int bytes, i;
	char data[7];
	double delay = 0.1;

	double buffAx = 0.0, buffAy = 0.0 , buffAz = 0.0;

	for(i=0; i<coldStartBuffer;i++) {
		data[0] = DATAX0;
		bytes = readBytes(h, data, 7);
		if(bytes != 7) {
			printf("Read error!\n");
			return;
		}
		time_sleep(coldDelay);
	}

	for(i=0; i<bufferSize; i++) {
		data[0] = DATAX0;
		bytes = readBytes(h, data, 7);
		if(bytes==7) {
			x = (data[2]<<8) | (data[1]);
			y = (data[4]<<8) | (data[3]);
			z = (data[6]<<8) | (data[5]);

			//printf("%d, %d, %d\n", x, y, z);

			buffAx = buffAx + xOS + (double)x;
			buffAy = buffAy + yOS + (double)y;
			buffAz = buffAz + zOS + (double)z;
		}
		time_sleep(delay);
	}

	*avgX = buffAx/(double)bufferSize;
	*avgY = buffAy/(double)bufferSize;
	*avgZ = buffAz/(double)bufferSize;
}

int main(int argc, char *argv[]) {

	double freq = 100;
	double error = 1.0;
	int samples = 10;
	int h;
	char data[7];

	if(gpioInitialise() < 0) {
		printf("GPIO Failed!\n");
		return 1;
	}

	h = spiOpen(0, spiSpeed, 3);

	data[0] = BW_RATE;
	data[1] = 0x0F; // 3200Hz Mode
	writeBytes(h, data, 2);

	data[0] = DATA_FORMAT;
	data[1] = 0x02; // 8g
	writeBytes(h, data, 2);

	data[0] = POWER_CTL;
	data[1] = 0x08;
	writeBytes(h, data, 2);

	double avg_x, avg_y, avg_z;
	double x_os = 0.0, y_os = 0.0, z_os = 0.0;

	printf("Calibrating...\n");

	avgData(h, samples, &avg_x, &avg_y, &avg_z, 0.0, 0.0, 0.0);

	x_os = -avg_x/(double)4;
	y_os = -avg_y/(double)4;
	z_os = -avg_z/(double)4;

	while(1) {
		int ready = 0;

		avgData(h, samples, &avg_x, &avg_y, &avg_z, x_os, y_os, z_os);

		printf("%.5f, %.5f, %.5f\n", x_os, y_os, z_os);
		//printf("%.5f, %.5f, %.5f\n", avg_x, avg_y, avg_z);

		if(fabs(avg_x)<=error) {
			ready+=1;
		} else {
			x_os = x_os - avg_x/(double)4;
		}

		if(fabs(avg_y)<=error) {
			ready+=1;
		} else {
			y_os = y_os - avg_y/(double)4;
		}

		if(fabs(avg_z)<=error) {
			ready+=1;
		} else {
			z_os = z_os - avg_z/(double)4;
		}

		if(ready==3) {
			break;
		}
	}

	printf("Offsets: %.5f, %.5f, %.5f\n", x_os, y_os, z_os);
}
