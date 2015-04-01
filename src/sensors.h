const double phys_params[2][3] = 
  { {0.0009083, 0.0002229, 4.232e-08},
    {0.001109, 0.0001925, 1.471e-07} };
const double log_resistors[2] = {9.890909, 9.893437};
const char mux_mask[2] = {0b0101, 0b0100};

void ADC_init(void);
