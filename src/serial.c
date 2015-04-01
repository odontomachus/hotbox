#include <stdlib.h>
#include <serial.h>

#define BAUDRATE 9600UL
#define BAUD_PRESCALLER (((F_CPU / (BAUDRATE * 8UL))) - 1)

void USART_init()
{
    /* Set baud rate (using u2x=1 doubles effective baud rate) */
  UBRR0H = (uint8_t)(BAUD_PRESCALLER>>8);
  UBRR0L = (uint8_t)(BAUD_PRESCALLER);
  UCSR0A |= (1<<U2X0);
  /* Enable receiver, transmitter and rx complete interrupt */
  UCSR0B = (1<<RXEN0)|(1<<TXEN0)|(1<<RXCIE0);
  /* Set frame format: 
   * 8 bit data (UCSZ2:0 = 0b011) 
   * 1 stop bit (USBS = 0) 
   * Async. op (UMSEL = 0) 
   * No parity (UPM1:0 = 0b00)*/ 
  UCSR0C = (3<<UCSZ00);
}

/**
 * Send a byte.
 */
void USART_transmit( unsigned char data )
{
  /* Wait for empty transmit buffer */
  while ( !( UCSR0A & (1<<UDRE0)) )
    ;
  /* Put data into buffer, sends the data */
  UDR0 = data;
}

void USART_flush( void )
{
  unsigned char dummy;
  while ( UCSR0A & (1<<RXC0) ) dummy = UDR0;
}

void USART_putstring(char* StringPtr){
  while(*StringPtr != '\0') {
    USART_transmit(*StringPtr);
    StringPtr++;
  }
}
