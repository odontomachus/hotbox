#include <stdlib.h>

#define HB_START 1
#define HB_ACTIVE 2
#define HB_READY 3
#define HB_BOOT 4
#define HB_INIT 5


#define HB_CYCLE 30
#define MSG_RUN_STATUS 1
#define MSG_CONFIG 2
#define MSG_STATUS 3

typedef struct hbconfig hbconfig;
struct hbconfig {
  volatile unsigned long time;
  volatile unsigned char temp;
};

volatile unsigned char update;
volatile unsigned char status;
volatile unsigned char recv;

hbconfig config;

// Receive configuration over serial
void rcv(unsigned char);

// Send the config over serial
void send_config(void);

// Send the status over serial
void send_status(void);

// Busy loop during cooking session
void run(void);

