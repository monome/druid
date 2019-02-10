#include <termios.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/types.h>

#include <pthread.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <ctype.h>

#define BAUDRATE B38400
#define DEV "/dev/ttyACM0"

int fd;
static pthread_t p;

void serial_tx(char *line);
void *serial_rx(void *);

void serial_init() {
  if (pthread_create(&p, NULL, serial_rx, 0) ) {
    fprintf(stderr, "error creating thread\n");
  }
}

void serial_deinit() {
  pthread_cancel(p);
}



int main(int argc, char **argv) {
	struct termios oldtio, newtio;

  char dev[255];

  if(argc==1) {
    printf("default\n");
    strcpy(dev,DEV);
  }
  else
    strcpy(dev,argv[1]);

  
  printf("druid --- 'q' to quit\n");

	//fd = open(DEV, O_RDWR | O_NOCTTY | O_NONBLOCK);
	fd = open(dev, O_RDWR | O_NOCTTY); //| O_NONBLOCK);
	if (fd <0) {perror(dev); exit(-1); }

  printf("connected to %s\n",dev);

  serial_init();

	tcgetattr(fd,&oldtio);
	newtio.c_cflag = BAUDRATE | CRTSCTS | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR | ICRNL;
	newtio.c_oflag = 0;
	newtio.c_lflag = ICANON;
	newtio.c_cc[VMIN]=1;
	newtio.c_cc[VTIME]=0;
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);

  int i = 0;
  int wlen;
  int c = 0;
  char a = 0;
  char line[255];
  int quit = 0;

  while(quit != 1) {
    line[a] = getchar();
    a++;
    line[a] = 0;

    if(line[a-1] == 10) {
      if(a==2 && line[0] == 'q') {
        quit = 1;
      } else {
        printf("\n");
        serial_tx(line);
        a = 0;
      }
    }
    else printf("%c",line[a-1]);
  }
  printf("\nfare well\n");
  serial_deinit();
	tcsetattr(fd,TCSANOW,&oldtio);
}

void serial_tx(char *line) {
  uint8_t i = 0;
  uint8_t wlen;
  while(i !=strlen(line)) {
    wlen = write(fd, line+i, 1);
    if(wlen==1) i++;
  }
}

void *serial_rx(void *x) {
  (void)x;
  uint8_t len;
  char buf[255];

  while(1) {
    len = read(fd, buf, 255);
    if(len > 0) {
      buf[len] = 0;
      //printf("%d\t > %s", len, buf);
      if(len>1) printf("\n> %s\n", buf);
      len = 0;
    }
    usleep(100);
  }
}

