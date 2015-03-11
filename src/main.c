#include <stdlib.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <avr/io.h>

#include "serial.c"
#include "sensors.c"
#include "rtc.c"
#include "math.h"

#define MAX(a,b) (a>b ? a : b)

volatile unsigned char update;
volatile unsigned char start;
volatile unsigned char status;

/*
 * ISR RX complete
 * Receive a byte from serial and act on it.
 */
ISR(USART_RX_vect) {
  uint8_t r = UDR0;
  USART_putstring("OK");
  switch (r) {
  case 's':
    start = 1;
    break;
  case 't':
    start = 0;
    break;
  }
}

void run() {
  unsigned int set_time, set_temp, countdown;

  unsigned char cycle, part;
  unsigned char temp1, temp2, last_temp;
  float dt, dg;

  set_temp = 53;
  set_time = 3600*6;
  countdown = set_time;

  part = cycle = 0;
  while (countdown-- > 0) {
    temp1 = phys_temp(0);
    temp2 = phys_temp(1);

    USART_putstring("MSG:12:");
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
    USART_putstring(":EOM:");

    if ((cycle%30)==0) {
      temp1 = MAX(temp1, temp2);
      dt = temp1 - last_temp;
      dg = last_temp - temp1;
      last_temp = temp1;
      if ((dg - dt) > 0) {
        part = part + round((30.0-part)/2.0);
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
    cycle = (cycle + 1)%30;

    temp1 = phys_temp(0);
    temp2 = phys_temp(1);

    _delay_ms(900);

  }

  PORTD &= ~(1<<PD5);
}


int main () {
  
  // Relay controller 1;
  DDRD |= (1<<PD5);
  // Relay controller 2;
  DDRB |= (1<<PB0);
  USART_Init();
  ADC_init();
  USART_putstring("Ready");
  sei();
  while (1) {
    if (start == 1) {
      run();
      USART_putstring("Ready");
    }
  }
}
