# Correlator_final
Repository to hold final versions of working codes, bof files, and models
Who knows how long it will take before it will get outdated, but contact me should you have questions at:
	eddietoral16@gmail.com
	
adc_stats is to be used to check the digital outputs, 1 antenna at a time using option '-a', of the SNAP board
	Not included in the larger models to preserve space for BRAMs
	2^16 data points collected per cnt_rst
	script provides plot of the ADC digital output data and histogram of the digital levels recorded into 256 bins (-128 to 127)
	
small_scale is a 4-input correlator using the 4 inputs ADC0 - ADC3
	
noise3 is the 12-input extension of small_scale correlator
	no quantization feature
	script does not solve for all plots of each correlation
	script records the data from all BRAMs in the model

quantized is the 12-input correlator with each input with its own scale to quantize to 4_3
	quantized.py currently only takes in a single value '-c' to scale all 12 data lines at once, code would need to be changed to scale each individually should it be necessary
