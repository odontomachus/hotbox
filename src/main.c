#include <stdlib.h>
#include <avr/interrupt.h>
#include <util/delay.h>

#include "serial.c"
#include "sensors.c"
#include "rtc.c"
#include "math.h"
#include "main.h"

#define MAX(a,b) ( a > b ? a : b)

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
    switch (r) {
    // Start run
    case 's':
      if (status == HB_STOP) {
        status = HB_START;
      }
      break;
    // stop run
    case 't':
      status = HB_STOP;
      break;
    // query config
    case 'q':
      send_config();
      break;
    // query status
    case 'r':
      send_status();
      break;
    case 'c':
      recv = 3;
      break;
    }
  }
}

/**
 * Interrupt once per second during heating.
 */
ISR(TIMER2_COMPA_vect) {
  if (status == HB_ACTIVE) {
    update = 1;
  }
}

void send_config() {
    USART_putstring("\0\0\0");
    USART_transmit(MSG_CONFIG);
    USART_transmit((unsigned char) (config.time >> 8));
    USART_transmit((unsigned char) config.time);
    USART_transmit(config.temp);
}

void send_status() {
    USART_putstring("\0\0\0");
    USART_transmit(MSG_STATUS);
    USART_transmit(status);
}  

void run() {
  unsigned int set_time, set_temp, countdown;

  unsigned char cycle, part;
  unsigned char temp1, temp2, last_temp;
  int dt, dg;

  USART_putstring("Starting");

  status = HB_ACTIVE;

  // Set timer
  OCR2A = TCNT2;
  // Enable compare interrupt
  TIMSK2 |= (1<<OCIE2A);

  set_temp = config.temp;
  set_time = config.time;
  countdown = set_time;

  part = cycle = dg = dt = 0;
  while ((countdown-- > 0) && (status == HB_ACTIVE)) {
    temp1 = phys_temp(0);
    temp2 = phys_temp(1);

    // Disable interrupts during message transmission
    cli();
    USART_putstring("\0\0\0");
    USART_transmit(MSG_RUN_STATUS);
    USART_transmit('T');
    USART_transmit(temp1);
    USART_transmit(temp2);
    USART_transmit('C');
    USART_transmit(countdown>>8);
    USART_transmit(countdown);
    USART_transmit('P');
    USART_transmit(part);
    USART_transmit('Y');
    USART_transmit(cycle);
    USART_transmit('S');
    USART_transmit(PIND & (1<<PD5));
    USART_transmit('G');
    USART_transmit(dg);
    USART_transmit('D');
    USART_transmit(dt);
    sei();

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
 
    // wait until interrupt
    while ((update != 1) && (status == HB_ACTIVE));
    update = 0;
    //_delay_ms(900);
  }

  PORTD &= ~(1<<PD5);
  status = HB_STOP;
  // Disable compare interrupt
  TIMSK2 &= ~(1<<OCIE2A);
}


int main () {
  RTC_init();
  // Relay controller 1;
  DDRD |= (1<<PD5);
  // Relay controller 2;
  DDRB |= (1<<PB0);
  USART_init();
  USART_putstring("Booting");  

  ADC_init();


  config.time = 3600*6;
  config.temp = 52;

  USART_putstring("Ready");
  sei();
  while (1) {
    if (status == HB_START) {
      run();
      USART_putstring("Ready");
    }
  }
}
