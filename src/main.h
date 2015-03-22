#include <stdlib.h>

#define HB_STOP 0
#define HB_START 1
#define HB_ACTIVE 2
#define HB_CYCLE 30

typedef struct hbconfig hbconfig;
struct hbconfig {
  volatile unsigned int time;
  volatile unsigned char temp;
};
