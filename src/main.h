#include <stdlib.h>

typedef struct hbconfig hbconfig;
struct hbconfig {
  volatile unsigned int time;
  volatile unsigned char temp;
};
