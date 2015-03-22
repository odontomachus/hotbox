/** 
 * Start Timer/Counter2 in asynchronous operation using a 32.768kHz crystal for RTC.
 */
void RTC_init(void)
{
  // Let oscillator stabilize
  _delay_ms(100);
  // Disable the Timer/Counter2 interrupts
  TIMSK2 &= ~((1<<OCIE2A)|(1<<OCIE2B)|(1<<TOIE2));
  // Select clock source by setting AS2 as appropriate.
  ASSR = (1<<AS2);
  // Set prescaler to 128: 32.768 kHz / 128 = 1 sec between each overflow
  TCCR2B |= (1<<CS22) | (1<<CS20);            
  // Reset TCNT2
  TCNT2 = 0;
	
  // Wait for clock edge
  while(ASSR & 0x1F);

  // Clear timer interrupt flag registers
  TIFR2 |= ((1<<OCF2A)|(1<<OCF2B)|(1<<TOV2));
  // Enable timer overflow interrupt
  //TIMSK2 |= (1<<TOIE2);
}
