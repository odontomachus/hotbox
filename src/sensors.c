#include "sensors.h"

void ADC_init() {
  // Set left adjusted for 8 bit precision
  ADMUX |= (1<<ADLAR);
  // Enable ADC and set prescaler to 16 ~1MHz/16 = 62kHz ~ 0.5ms for
  // first measurement, 0.25ms per subsequent measurement.
  ADCSRA |= (1<<ADEN) | (0b100<<ADPS0);
  // Disable digital buffer on 3 ADC pins.
  DIDR0 |= (1<<ADC4D) | (1<<ADC5D) | (1<<ADC2D);
}

/**
 * Get a reading from sensors.
 *
 * @param mask ADMUX mask.
 */
unsigned int read_ts(char mux) {
  uint8_t tmp;

  // Set source to internal
  ADMUX |= (0b11<<REFS0);
  // Give cap time to discharge
  _delay_ms(100);
  DDRC &= ~((1<<PC5)|(1<<PC4));
  PORTC &= ~((1<<PC5)|(1<<PC4));
  // Set ADC4/5 as input
  ADMUX = (ADMUX & ( ~(0b1111<<MUX0) )) | (mux<<MUX0);
  _delay_ms(1);
  // Start conversion
  ADCSRA |= 1 << ADSC;
  // Wait for conversion to finish
  while (ADCSRA & (1<<ADSC)) {
    _delay_us(50);
  }
  tmp = ADCH;// Discard first measurement after channel switch

  // Start conversion
  ADCSRA |= 1 << ADSC;
  // Wait for conversion to finish
  while (ADCSRA & (1<<ADSC)) {
    _delay_us(50);
  }

  return ((ADCL>>6) | (ADCH<<2));
}

/**
 * Get temperature readings.
 */
unsigned int phys_temp(int i) {
  double d_temp, sensor, log_res;
  // Add 0.1 to make sure it's not 0.
  sensor = (double) read_ts(mux_mask[i])+0.1;

  // Get log of resistance from V measurement.
  log_res = log(sensor) + log_resistors[i] - log(1024-sensor);
  d_temp = 1.0/(phys_params[i][0]+phys_params[i][1]*log_res + phys_params[i][2]*pow(log_res,3)) - 273.15;

  return (int) d_temp;
}
