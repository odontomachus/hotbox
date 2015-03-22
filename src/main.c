#include <stdlib.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include "serial.c"
#include "sensors.c"
#include "rtc.c"
#include "math.h"
#include "main.h"

#define MAX(a,b) (a>b ? a : b)

volatile unsigned char update;
volatile unsigned char status;
volatile unsigned char recv;
hbconfig config;

void rcv(unsigned char byte) {
  switch(recv) {
  case 2:
    config.time = byte << 8;
    break;
  case 1:
    config.time += byte;
    break;
  case 0:
    config.temp = byte;
    break;
  }
}


/*
 * ISR RX complete
 * Receive a byte from serial and act on it.
 */
ISR(USART_RX_vect) {
  uint8_t r = UDR0;

  if (recv > 0) {
    recv--;
    rcv(r);
  }
  else {
    USART_putstring("OK");
    switch (r) {
    case 's':
      if (status == HB_STOP) {
        status = HB_START;
      }
      break;
    case 't':
      status = HB_STOP;
      break;
    case 'c':
      recv = 3;
      break;
    }
  }
}

void run() {
  unsigned int set_time, set_temp, countdown;

  unsigned char cycle, part;
  unsigned char temp1, temp2, last_temp;
  int dt, dg;

  status = HB_ACTIVE;

  set_temp = 53;
  set_time = 90;
  countdown = set_time;

  part = cycle = dg = dt = 0;
  while (countdown-- > 0) {
    temp1 = phys_temp(0);
    temp2 = phys_temp(1);

    USART_putstring("MSG:");
    USART_Transmit('T');
    USART_Transmit(temp1);
    USART_Transmit(temp2);
    USART_Transmit('C');
    USART_Transmit(countdown>>8);
    USART_Transmit(countdown);
    USART_Transmit('P');
    USART_Transmit(part);
    USART_Transmit('Y');
    USART_Transmit(cycle);
    USART_Transmit('S');
    USART_Transmit(PORTD & (1<<PD5));
    USART_Transmit('G');
    USART_Transmit(dg);
    USART_Transmit('D');
    USART_Transmit(dt);
    USART_putstring(":EOM");

    if ((cycle%HB_CYCLE)==0) {
      temp1 = MAX(temp1, temp2);
      dt = temp1 - last_temp;
      dg = set_temp - temp1;
      last_temp = temp1;
      if ((dg - dt) > 0) {
        part = part + round(((float) HB_CYCLE-part)/2.0);
      }
      else if ((dg - dt) < 0) {
        if (part > 0) {
          part = part / 2;
        }
      }
    }

    if (cycle == part) {
      PORTD &= ~(1<<PD5);
    }
    if (cycle == 0) {
      if (part > 0) {
        PORTD |= (1<<PD5);
      }
    }
    cycle = (cycle + 1)%HB_CYCLE;

    temp1 = phys_temp(0);
    temp2 = phys_temp(1);

    _delay_ms(900);

  }

  PORTD &= ~(1<<PD5);
  status = HB_STOP;
}


int main () {
  // Relay controller 1;
  DDRD |= (1<<PD5);
  // Relay controller 2;
  DDRB |= (1<<PB0);
  USART_Init();
  USART_Transmit('c');
  USART_putstring("Booting");  

  ADC_init();
  USART_putstring("Ready");

  config.time = 3600*6;
  config.temp = 52;
  
  sei();
  while (1) {
    if (status == HB_START) {
      run();
      USART_putstring("Ready");
    }
  }
}
