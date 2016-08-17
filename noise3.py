#	Eddie Toral
#	CAMPARE 2016 Summer Research Undergrad
#	August 16th 2016
#
#	12-input Correlator for SNAP Board
#
#	Testing info:
#		Clk Freq = 250 MHz, Input signal freq = 75 Mhz at -6.0 dBm 
#	Noise sources: 
#		Amps in series for one source, L-band generator for the other. 
#		Couplers used in reverse to combine tone with noise to use for testing.
#
#	Using 12-input SNAP Board w/ RaspberryPi 
#	10 stage fft_biplex_real_2x
#	4-tap 1024 polyphase filter bank
#	Model & code will Correlate all 12 inputs at the same time
#	12 input, 3 ADC works (noise3_2016-8-15_1450_.bof)
#--------------------------------------------------------------------------------------------------------------------------------------
#Import necessary Libraries
import corr, struct, numpy as np, matplotlib.pyplot as plt, time

#--------------------------------------------------------------------------------------------------------------------------------------
#To incorporate options chosen w/ host
from argparse import ArgumentParser
p = ArgumentParser(description = 'python noise3.py [options] ')
p.add_argument('host', type = str, default = '10.0.1.217', help = 'Specify the host name')
p.add_argument('-s', '--shift', dest = 'shift', type = int, default = 2047, help = 'set shift value for fft biplex block')
p.add_argument('-l', '--length', dest = 'length', type = int, default = 2e6, help = 'set # of spectra to be accumulated')

args = p.parse_args()
host = args.host
shift = args.shift
length = args.length 

#--------------------------------------------------------------------------------------------------------------------------------------
#Merges real and imaginary parts of Cross Correlation data into a single number
def merge(x,y):
	temp = []
	w = 0
	while w < 512:
		temp.append(x[w] + y[w]*1j)
		w += 1
	return np.asarray(temp)
	
#--------------------------------------------------------------------------------------------------------------------------------------
#Establishing a connection to the FPGA from your computer
print "Connecting to Fpga"
s = corr.katcp_wrapper.FpgaClient(host,7147,timeout = 10)
time.sleep(1)

#--------------------------------------------------------------------------------------------------------------------------------------
#To make sure RaspberryPi and SNAP Board are connected
if s.is_connected():
	print "Connected"
else:
	print "Not connected"

#--------------------------------------------------------------------------------------------------------------------------------------
#To be used for plotting purposes at the end of the code
fn = np.linspace(0,511,512)

#--------------------------------------------------------------------------------------------------------------------------------------
#Setting FFT Biplex x2 Shift value
print "Setting Shift value"
s.write_int('shift',shift)
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
#Setting the Accumulation length to option choice selected
print "Starting accumulation process"
s.write_int('acc_len',length)

#--------------------------------------------------------------------------------------------------------------------------------------
#Start Data Processing & Capture
#Sending Sync Pulse
s.write_int('trig',0)
s.write_int('trig',1)
s.write_int('trig',0)

#Extra accumulations done before reading data from BRAMs for saftey of data
#It tosses out unknown initial state junk values that would mess up data.
#Should be working by final accumulation transition to read BRAMs
#Dont freakout if the numbers are big or negative, only thing that matters is that acc_num goes up by 1 each time it's printed.
acc_num = s.read_int('acc_num')
while s.read_int('acc_num') == acc_num:
	time.sleep(0.1)
print acc_num
acc_num = s.read_int('acc_num')
while s.read_int('acc_num') == acc_num:
	time.sleep(0.1)
print acc_num
acc_num = s.read_int('acc_num')
while s.read_int('acc_num') == acc_num:
	time.sleep(0.1)
print acc_num
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
#If FFT Biplex block overflows, the output here would be non-zero
overflow = s.read_int('overflow')
print overflow

#--------------------------------------------------------------------------------------------------------------------------------------
#Reading Data from all Correlation BRAM Blocks
#Antenna names correspond to the antenna names for the inputs on the SNAP board.
#		ie. ADC0 Board input -> ac0,a0, etc. in the following lines
#Cross Correlations will have the naming convention of ccantenna_Aantenna_B
#		ie. Cross correlation of ADC0 and ADC3 board inputs will be named cc03, etc.

#Autocorrelation Data
ac0 = np.asarray(struct.unpack('>512l',s.read('ac_a0_real',2048)))
ac1 = np.asarray(struct.unpack('>512l',s.read('ac_a1_real',2048)))
ac2 = np.asarray(struct.unpack('>512l',s.read('ac_a2_real',2048)))
ac3 = np.asarray(struct.unpack('>512l',s.read('ac_a3_real',2048)))
ac4 = np.asarray(struct.unpack('>512l',s.read('ac_a4_real',2048)))
ac5 = np.asarray(struct.unpack('>512l',s.read('ac_a5_real',2048)))
ac6 = np.asarray(struct.unpack('>512l',s.read('ac_a6_real',2048)))
ac7 = np.asarray(struct.unpack('>512l',s.read('ac_a7_real',2048)))
ac8 = np.asarray(struct.unpack('>512l',s.read('ac_a8_real',2048)))
ac9 = np.asarray(struct.unpack('>512l',s.read('ac_a9_real',2048)))
ac10 = np.asarray(struct.unpack('>512l',s.read('ac_a10_real',2048)))
ac11 = np.asarray(struct.unpack('>512l',s.read('ac_a11_real',2048)))

#Cross Correlation Data
#Antenna 0 Cross 1 - 11
cc01r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a1_real',2048)))
cc01i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a1_imag',2048)))
cc02r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a2_real',2048)))
cc02i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a2_imag',2048)))
cc03r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a3_real',2048)))
cc03i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a3_imag',2048)))
cc04r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a4_real',2048)))
cc04i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a4_imag',2048)))
cc05r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a5_real',2048)))
cc05i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a5_imag',2048)))
cc06r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a6_real',2048)))
cc06i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a6_imag',2048)))
cc07r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a7_real',2048)))
cc07i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a7_imag',2048)))
cc08r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a8_real',2048)))
cc08i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a8_imag',2048)))
cc09r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a9_real',2048)))
cc09i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a9_imag',2048)))
cc010r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a10_real',2048)))
cc010i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a10_imag',2048)))
cc011r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a11_real',2048)))
cc011i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a11_imag',2048)))

#Antenna 1 Cross 2 - 11
cc12r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a2_real',2048)))
cc12i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a2_imag',2048)))
cc13r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a3_real',2048)))
cc13i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a3_imag',2048)))
cc14r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a4_real',2048)))
cc14i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a4_imag',2048)))
cc15r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a5_real',2048)))
cc15i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a5_imag',2048)))
cc16r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a6_real',2048)))
cc16i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a6_imag',2048)))
cc17r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a7_real',2048)))
cc17i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a7_imag',2048)))
cc18r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a8_real',2048)))
cc18i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a8_imag',2048)))
cc19r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a9_real',2048)))
cc19i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a9_imag',2048)))
cc110r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a10_real',2048)))
cc110i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a10_imag',2048)))
cc111r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a11_real',2048)))
cc111i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a11_imag',2048)))

#Atenna 2 Cross 3 - 11
cc23r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a3_real',2048)))
cc23i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a3_imag',2048)))
cc24r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a4_real',2048)))
cc24i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a4_imag',2048)))
cc25r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a5_real',2048)))
cc25i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a5_imag',2048)))
cc26r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a6_real',2048)))
cc26i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a6_imag',2048)))
cc27r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a7_real',2048)))
cc27i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a7_imag',2048)))
cc28r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a8_real',2048)))
cc28i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a8_imag',2048)))
cc29r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a9_real',2048)))
cc29i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a9_imag',2048)))
cc210r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a10_real',2048)))
cc210i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a10_imag',2048)))
cc211r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a11_real',2048)))
cc211i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a11_imag',2048)))

#Antenna 3 Cross 4 - 11
cc34r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a4_real',2048)))
cc34i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a4_imag',2048)))
cc35r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a5_real',2048)))
cc35i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a5_imag',2048)))
cc36r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a6_real',2048)))
cc36i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a6_imag',2048)))
cc37r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a7_real',2048)))
cc37i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a7_imag',2048)))
cc38r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a8_real',2048)))
cc38i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a8_imag',2048)))
cc39r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a9_real',2048)))
cc39i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a9_imag',2048)))
cc310r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a10_real',2048)))
cc310i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a10_imag',2048)))
cc311r = np.asarray(struct.unpack('>512l',s.read('cc_a3_a11_real',2048)))
cc311i = np.asarray(struct.unpack('>512l',s.read('cc_a3_a11_imag',2048)))

#Antenna 4 Cross 5 - 11
cc45r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a5_real',2048)))
cc45i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a5_imag',2048)))
cc46r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a6_real',2048)))
cc46i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a6_imag',2048)))
cc47r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a7_real',2048)))
cc47i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a7_imag',2048)))
cc48r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a8_real',2048)))
cc48i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a8_imag',2048)))
cc49r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a9_real',2048)))
cc49i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a9_imag',2048)))
cc410r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a10_real',2048)))
cc410i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a10_imag',2048)))
cc411r = np.asarray(struct.unpack('>512l',s.read('cc_a4_a11_real',2048)))
cc411i = np.asarray(struct.unpack('>512l',s.read('cc_a4_a11_imag',2048)))

#Antenna 5 Cross 6 - 11
cc56r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a6_real',2048)))
cc56i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a6_imag',2048)))
cc57r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a7_real',2048)))
cc57i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a7_imag',2048)))
cc58r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a8_real',2048)))
cc58i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a8_imag',2048)))
cc59r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a9_real',2048)))
cc59i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a9_imag',2048)))
cc510r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a10_real',2048)))
cc510i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a10_imag',2048)))
cc511r = np.asarray(struct.unpack('>512l',s.read('cc_a5_a11_real',2048)))
cc511i = np.asarray(struct.unpack('>512l',s.read('cc_a5_a11_imag',2048)))

#Antenna 6 Cross 7 - 11
cc67r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a7_real',2048)))
cc67i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a7_imag',2048)))
cc68r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a8_real',2048)))
cc68i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a8_imag',2048)))
cc69r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a9_real',2048)))
cc69i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a9_imag',2048)))
cc610r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a10_real',2048)))
cc610i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a10_imag',2048)))
cc611r = np.asarray(struct.unpack('>512l',s.read('cc_a6_a11_real',2048)))
cc611i = np.asarray(struct.unpack('>512l',s.read('cc_a6_a11_imag',2048)))

#Antenna 7 Cross 8 - 11
cc78r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a8_real',2048)))
cc78i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a8_imag',2048)))
cc79r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a9_real',2048)))
cc79i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a9_imag',2048)))
cc710r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a10_real',2048)))
cc710i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a10_imag',2048)))
cc711r = np.asarray(struct.unpack('>512l',s.read('cc_a7_a11_real',2048)))
cc711i = np.asarray(struct.unpack('>512l',s.read('cc_a7_a11_imag',2048)))

#Antenna 8 Cross 9 - 11
cc89r = np.asarray(struct.unpack('>512l',s.read('cc_a8_a9_real',2048)))
cc89i = np.asarray(struct.unpack('>512l',s.read('cc_a8_a9_imag',2048)))
cc810r = np.asarray(struct.unpack('>512l',s.read('cc_a8_a10_real',2048)))
cc810i = np.asarray(struct.unpack('>512l',s.read('cc_a8_a10_imag',2048)))
cc811r = np.asarray(struct.unpack('>512l',s.read('cc_a8_a11_real',2048)))
cc811i = np.asarray(struct.unpack('>512l',s.read('cc_a8_a11_imag',2048)))

#Antenna 9 Cross 10 - 11
cc910r = np.asarray(struct.unpack('>512l',s.read('cc_a9_a10_real',2048)))
cc910i = np.asarray(struct.unpack('>512l',s.read('cc_a9_a10_imag',2048)))
cc911r = np.asarray(struct.unpack('>512l',s.read('cc_a9_a11_real',2048)))
cc911i = np.asarray(struct.unpack('>512l',s.read('cc_a9_a11_imag',2048)))

#Antenna 10 Cross 11
cc1011r = np.asarray(struct.unpack('>512l',s.read('cc_a10_a11_real',2048)))
cc1011i = np.asarray(struct.unpack('>512l',s.read('cc_a10_a11_imag',2048)))


#--------------------------------------------------------------------------------------------------------------------------------------
#Determination of the Magnitude Responses of the Autocorrelations of each input
#Phase Responses not solved for to save BRAM Space (no accumulation & storage of imaginary data stream)
#Phase Responses are 0 for Autocorrelations

#Autocorrelation of 0
magac0 = abs(ac0)
#Autocorrelation of 1
magac1 = abs(ac1)
#Autocorrelation of 2
magac2 = abs(ac2)
#Autocorrelation of 3
magac3 = abs(ac3)
#Autocorrelation of 4
magac4 = abs(ac4)
#Autocorrelation of 5
magac5 = abs(ac5)
#Autocorrelation of 6
magac6 = abs(ac6)
#Autocorrelation of 7
magac7 = abs(ac7)
#Autocorrelation of 8
magac8 = abs(ac8)
#Autocorrelation of 9
magac9 = abs(ac9)
#Autocorrelation of 10
magac10 = abs(ac10)
#Autocorrelation of 11
magac11 = abs(ac11)

#--------------------------------------------------------------------------------------------------------------------------------------
#Recombing real and imaginary parts of the Accumulated Cross Correlations 
#Solving for Magnitudes and Phase Responses of the Cross Correlations

#Cross Correlation of 0 and 1
cc01rl = list(cc01r)
cc01il = list(cc01i)
cc01 = merge(cc01rl,cc01il)
magcc01 = abs(cc01)
phasecc01 = np.angle(cc01)*180/np.pi
#Cross Correlation of 0 and 2
cc02rl = list(cc02r)
cc02il = list(cc02i)
cc02 = merge(cc02rl,cc02il)
magcc02 = abs(cc02)
phasecc02 = np.angle(cc02)*180/np.pi
#Cross Correlation of 0 and 3
cc03rl = list(cc03r)
cc03il = list(cc03i)
cc03 = merge(cc03rl,cc03il)
magcc03 = abs(cc03)
phasecc03 = np.angle(cc03)*180/np.pi
#Cross Correlation of 0 and 4
cc04rl = list(cc04r)
cc04il = list(cc04i)
cc04 = merge(cc04rl,cc04il)
magcc04 = abs(cc04)
phasecc04 = np.angle(cc04)*180/np.pi
#Cross Correlation of 0 and 5
cc05rl = list(cc05r)
cc05il = list(cc05i)
cc05 = merge(cc05rl,cc05il)
magcc05 = abs(cc05)
phasecc05 = np.angle(cc05)*180/np.pi
#Cross Correlation of 0 and 6
cc06rl = list(cc06r)
cc06il = list(cc03i)
cc06 = merge(cc06rl,cc06il)
magcc06 = abs(cc06)
phasecc06 = np.angle(cc06)*180/np.pi
#Cross Correlation of 0 and 7
cc07rl = list(cc07r)
cc07il = list(cc07i)
cc07 = merge(cc07rl,cc07il)
magcc07 = abs(cc07)
phasecc07 = np.angle(cc07)*180/np.pi
#Cross Correlation of 0 and 8
cc08rl = list(cc08r)
cc08il = list(cc08i)
cc08 = merge(cc08rl,cc08il)
magcc08 = abs(cc08)
phasecc08 = np.angle(cc08)*180/np.pi
#Cross Correlation of 0 and 9
cc09rl = list(cc09r)
cc09il = list(cc09i)
cc09 = merge(cc09rl,cc09il)
magcc09 = abs(cc09)
phasecc09 = np.angle(cc09)*180/np.pi
#Cross Correlation of 0 and 10
cc010rl = list(cc010r)
cc010il = list(cc010i)
cc010 = merge(cc010rl,cc010il)
magcc010 = abs(cc010)
phasecc010 = np.angle(cc010)*180/np.pi
#Cross Correlation of 0 and 11
cc011rl = list(cc011r)
cc011il = list(cc011i)
cc011 = merge(cc011rl,cc011il)
magcc011 = abs(cc011)
phasecc011 = np.angle(cc011)*180/np.pi

#Cross Correlation of 1 and 2
cc12rl = list(cc12r)
cc12il = list(cc12i)
cc12 = merge(cc12rl,cc12il)
magcc12 = abs(cc12)
phasecc12 = np.angle(cc12)*180/np.pi
#Cross Correlation of 1 and 3
cc13rl = list(cc13r)
cc13il = list(cc13i)
cc13 = merge(cc13rl,cc13il)
magcc13 = abs(cc13)
phasecc13 = np.angle(cc13)*180/np.pi
#Cross Correlation of 1 and 4
cc14rl = list(cc14r)
cc14il = list(cc14i)
cc14 = merge(cc14rl,cc14il)
magcc14 = abs(cc14)
phasecc14 = np.angle(cc14)*180/np.pi
#Cross Correlation of 1 and 5
cc15rl = list(cc15r)
cc15il = list(cc15i)
cc15 = merge(cc15rl,cc15il)
magcc15 = abs(cc15)
phasecc15 = np.angle(cc15)*180/np.pi
#Cross Correlation of 1 and 6
cc16rl = list(cc16r)
cc16il = list(cc16i)
cc16 = merge(cc16rl,cc16il)
magcc16 = abs(cc16)
phasecc16 = np.angle(cc16)*180/np.pi
#Cross Correlation of 1 and 7
cc17rl = list(cc17r)
cc17il = list(cc17i)
cc17 = merge(cc17rl,cc17il)
magcc17 = abs(cc17)
phasecc17 = np.angle(cc17)*180/np.pi
#Cross Correlation of 1 and 8
cc18rl = list(cc18r)
cc18il = list(cc18i)
cc18 = merge(cc18rl,cc18il)
magcc18 = abs(cc18)
phasecc18 = np.angle(cc18)*180/np.pi
#Cross Correlation of 1 and 9
cc19rl = list(cc19r)
cc19il = list(cc19i)
cc19 = merge(cc19rl,cc19il)
magcc19 = abs(cc19)
phasecc19 = np.angle(cc19)*180/np.pi
#Cross Correlation of 1 and 10
cc110rl = list(cc110r)
cc110il = list(cc110i)
cc110 = merge(cc110rl,cc110il)
magcc110 = abs(cc110)
phasecc110 = np.angle(cc110)*180/np.pi
#Cross Correlation of 1 and 11
cc111rl = list(cc111r)
cc111il = list(cc111i)
cc111 = merge(cc111rl,cc111il)
magcc111 = abs(cc111)
phasecc111 = np.angle(cc111)*180/np.pi

#Cross Correlation of 2 and 3
cc23rl = list(cc23r)
cc23il = list(cc23i)
cc23 = merge(cc23rl,cc23il)
magcc23 = abs(cc23)
phasecc23 = np.angle(cc23)*180/np.pi
#Cross Correlation of 2 and 4
cc24rl = list(cc24r)
cc24il = list(cc24i)
cc24 = merge(cc24rl,cc24il)
magcc24 = abs(cc24)
phasecc24 = np.angle(cc24)*180/np.pi
#Cross Correlation of 2 and 5
cc25rl = list(cc25r)
cc25il = list(cc25i)
cc25 = merge(cc25rl,cc25il)
magcc25 = abs(cc25)
phasecc25 = np.angle(cc25)*180/np.pi
#Cross Correlation of 2 and 6
cc26rl = list(cc26r)
cc26il = list(cc26i)
cc26 = merge(cc26rl,cc26il)
magcc26 = abs(cc26)
phasecc26 = np.angle(cc26)*180/np.pi
#Cross Correlation of 2 and 7
cc27rl = list(cc27r)
cc27il = list(cc27i)
cc27 = merge(cc27rl,cc27il)
magcc27 = abs(cc27)
phasecc27 = np.angle(cc27)*180/np.pi
#Cross Correlation of 2 and 8
cc28rl = list(cc28r)
cc28il = list(cc28i)
cc28 = merge(cc28rl,cc28il)
magcc28 = abs(cc28)
phasecc28 = np.angle(cc28)*180/np.pi
#Cross Correlation of 2 and 9
cc29rl = list(cc29r)
cc29il = list(cc29i)
cc29 = merge(cc29rl,cc29il)
magcc29 = abs(cc29)
phasecc29 = np.angle(cc29)*180/np.pi
#Cross Correlation of 2 and 10
cc210rl = list(cc210r)
cc210il = list(cc210i)
cc210 = merge(cc210rl,cc210il)
magcc210 = abs(cc210)
phasecc210 = np.angle(cc210)*180/np.pi
#Cross Correlation of 2 and 11
cc211rl = list(cc211r)
cc211il = list(cc211i)
cc211 = merge(cc211rl,cc211il)
magcc211 = abs(cc211)
phasecc211 = np.angle(cc211)*180/np.pi

#Cross Correlation of 3 and 4
cc34rl = list(cc34r)
cc34il = list(cc34i)
cc34 = merge(cc34rl,cc34il)
magcc34 = abs(cc34)
phasecc34 = np.angle(cc34)*180/np.pi
#Cross Correlation of 3 and 5
cc35rl = list(cc35r)
cc35il = list(cc35i)
cc35 = merge(cc35rl,cc35il)
magcc35 = abs(cc35)
phasecc35 = np.angle(cc35)*180/np.pi
#Cross Correlation of 3 and 6
cc36rl = list(cc36r)
cc36il = list(cc36i)
cc36 = merge(cc36rl,cc36il)
magcc36 = abs(cc36)
phasecc36 = np.angle(cc36)*180/np.pi
#Cross Correlation of 3 and 7
cc37rl = list(cc37r)
cc37il = list(cc37i)
cc37 = merge(cc37rl,cc37il)
magcc37 = abs(cc37)
phasecc37 = np.angle(cc37)*180/np.pi
#Cross Correlation of 3 and 8
cc38rl = list(cc38r)
cc38il = list(cc38i)
cc38 = merge(cc38rl,cc38il)
magcc38 = abs(cc38)
phasecc38 = np.angle(cc38)*180/np.pi
#Cross Correlation of 3 and 9
cc39rl = list(cc39r)
cc39il = list(cc39i)
cc39 = merge(cc39rl,cc39il)
magcc39 = abs(cc39)
phasecc39 = np.angle(cc39)*180/np.pi
#Cross Correlation of 3 and 10
cc310rl = list(cc310r)
cc310il = list(cc310i)
cc310 = merge(cc310rl,cc310il)
magcc310 = abs(cc310)
phasecc310 = np.angle(cc310)*180/np.pi
#Cross Correlation of 3 and 11
cc311rl = list(cc311r)
cc311il = list(cc311i)
cc311 = merge(cc311rl,cc311il)
magcc311 = abs(cc311)
phasecc311 = np.angle(cc311)*180/np.pi

#Cross Correlation of 4 and 5
cc45rl = list(cc45r)
cc45il = list(cc45i)
cc45 = merge(cc45rl,cc45il)
magcc45 = abs(cc45)
phasecc45 = np.angle(cc45)*180/np.pi
#Cross Correlation of 4 and 6
cc46rl = list(cc46r)
cc46il = list(cc46i)
cc46 = merge(cc46rl,cc46il)
magcc46 = abs(cc46)
phasecc46 = np.angle(cc46)*180/np.pi
#Cross Correlation of 4 and 7
cc47rl = list(cc47r)
cc47il = list(cc47i)
cc47 = merge(cc47rl,cc47il)
magcc47 = abs(cc47)
phasecc47 = np.angle(cc47)*180/np.pi
#Cross Correlation of 4 and 8
cc48rl = list(cc48r)
cc48il = list(cc48i)
cc48 = merge(cc48rl,cc48il)
magcc48 = abs(cc48)
phasecc48 = np.angle(cc48)*180/np.pi
#Cross Correlation of 4 and 9
cc49rl = list(cc49r)
cc49il = list(cc49i)
cc49 = merge(cc49rl,cc49il)
magcc49 = abs(cc49)
phasecc49 = np.angle(cc49)*180/np.pi
#Cross Correlation of 4 and 10
cc410rl = list(cc410r)
cc410il = list(cc410i)
cc410 = merge(cc410rl,cc410il)
magcc410 = abs(cc410)
phasecc410 = np.angle(cc410)*180/np.pi
#Cross Correlation of 4 and 11
cc411rl = list(cc411r)
cc411il = list(cc411i)
cc411 = merge(cc411rl,cc411il)
magcc411 = abs(cc411)
phasecc411 = np.angle(cc411)*180/np.pi

#Cross Correlation of 5 and 6
cc56rl = list(cc56r)
cc56il = list(cc56i)
cc56 = merge(cc56rl,cc56il)
magcc56 = abs(cc56)
phasecc56 = np.angle(cc56)*180/np.pi
#Cross Correlation of 5 and 7
cc57rl = list(cc57r)
cc57il = list(cc57i)
cc57 = merge(cc57rl,cc57il)
magcc57 = abs(cc57)
phasecc57 = np.angle(cc57)*180/np.pi
#Cross Correlation of 5 and 8
cc58rl = list(cc58r)
cc58il = list(cc58i)
cc58 = merge(cc58rl,cc58il)
magcc58 = abs(cc58)
phasecc58 = np.angle(cc58)*180/np.pi
#Cross Correlation of 5 and 9
cc59rl = list(cc59r)
cc59il = list(cc59i)
cc59 = merge(cc59rl,cc59il)
magcc59 = abs(cc59)
phasecc59 = np.angle(cc59)*180/np.pi
#Cross Correlation of 5 and 10
cc510rl = list(cc510r)
cc510il = list(cc510i)
cc510 = merge(cc510rl,cc510il)
magcc510 = abs(cc510)
phasecc510 = np.angle(cc510)*180/np.pi
#Cross Correlation of 5 and 11
cc511rl = list(cc511r)
cc511il = list(cc511i)
cc511 = merge(cc511rl,cc511il)
magcc511 = abs(cc511)
phasecc511 = np.angle(cc511)*180/np.pi

#Cross Correlation of 6 and 7
cc67rl = list(cc67r)
cc67il = list(cc67i)
cc67 = merge(cc67rl,cc67il)
magcc67 = abs(cc67)
phasecc67 = np.angle(cc67)*180/np.pi
#Cross Correlation of 6 and 8
cc68rl = list(cc68r)
cc68il = list(cc68i)
cc68 = merge(cc68rl,cc68il)
magcc68 = abs(cc68)
phasecc68 = np.angle(cc68)*180/np.pi
#Cross Correlation of 6 and 9
cc69rl = list(cc69r)
cc69il = list(cc69i)
cc69 = merge(cc69rl,cc69il)
magcc69 = abs(cc69)
phasecc69 = np.angle(cc69)*180/np.pi
#Cross Correlation of 6 and 10
cc610rl = list(cc610r)
cc610il = list(cc610i)
cc610 = merge(cc610rl,cc610il)
magcc610 = abs(cc610)
phasecc610 = np.angle(cc610)*180/np.pi
#Cross Correlation of 6 and 11
cc611rl = list(cc611r)
cc611il = list(cc611i)
cc611 = merge(cc611rl,cc611il)
magcc611 = abs(cc611)
phasecc611 = np.angle(cc611)*180/np.pi


#Cross Correlation of 7 and 8
cc78rl = list(cc78r)
cc78il = list(cc78i)
cc78 = merge(cc78rl,cc78il)
magcc78 = abs(cc78)
phasecc78 = np.angle(cc78)*180/np.pi
#Cross Correlation of 7 and 9
cc79rl = list(cc79r)
cc79il = list(cc79i)
cc79 = merge(cc79rl,cc79il)
magcc79 = abs(cc79)
phasecc79 = np.angle(cc79)*180/np.pi
#Cross Correlation of 7 and 10
cc710rl = list(cc710r)
cc710il = list(cc710i)
cc710 = merge(cc710rl,cc710il)
magcc710 = abs(cc710)
phasecc710 = np.angle(cc710)*180/np.pi
#Cross Correlation of 7 and 11
cc711rl = list(cc711r)
cc711il = list(cc711i)
cc711 = merge(cc711rl,cc711il)
magcc711 = abs(cc711)
phasecc711 = np.angle(cc711)*180/np.pi

#Cross Correlation of 8 and 9
cc89rl = list(cc89r)
cc89il = list(cc89i)
cc89 = merge(cc89rl,cc89il)
magcc89 = abs(cc89)
phasecc89 = np.angle(cc89)*180/np.pi
#Cross Correlation of 8 and 10
cc810rl = list(cc810r)
cc810il = list(cc810i)
cc810 = merge(cc810rl,cc810il)
magcc810 = abs(cc810)
phasecc810 = np.angle(cc810)*180/np.pi
#Cross Correlation of 8 and 11
cc811rl = list(cc811r)
cc811il = list(cc811i)
cc811 = merge(cc811rl,cc811il)
magcc811 = abs(cc811)
phasecc811 = np.angle(cc811)*180/np.pi

#Cross Correlation of 9 and 10
cc910rl = list(cc910r)
cc910il = list(cc910i)
cc910 = merge(cc910rl,cc910il)
magcc910 = abs(cc910)
phasecc910 = np.angle(cc910)*180/np.pi
#Cross Correlation of 9 and 11
cc911rl = list(cc911r)
cc911il = list(cc911i)
cc911 = merge(cc911rl,cc911il)
magcc911 = abs(cc911)
phasecc911 = np.angle(cc911)*180/np.pi

#Cross Correlation of 10 and 11
cc1011rl = list(cc1011r)
cc1011il = list(cc1011i)
cc1011 = merge(cc1011rl,cc1011il)
magcc1011 = abs(cc1011)
phasecc1011 = np.angle(cc1011)*180/np.pi

#--------------------------------------------------------------------------------------------------------------------------------------
print "Plotting Data"
#Autocorrelation Plots
plt.figure(1)
plt.title('Autocorrelation of Antenna 0')
plt.title('Magnitude Response of AC of 0')
plt.plot(fn,magac0,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.figure(2)
plt.title('Autocorrelation of Antenna 4')
plt.title('Magnitude Response of AC of 4')
plt.plot(fn,magac4,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.figure(3)
plt.title('Autocorrelation of Antenna 8')
plt.title('Magnitude Response of AC of 8')
plt.plot(fn,magac8,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)


plt.figure(4)
plt.title('Autocorrelation of Antenna 11')
plt.title('Magnitude Response of AC of 11')
plt.plot(fn,magac11,'y')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

#--------------------------------------------------------------------------------------------------------------------------------------
#Cross Correlation Plots

plt.figure(5)
plt.title('Cross Correlation of Antennas 0 & 11')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 11')
plt.plot(fn,magcc011,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 11')
plt.plot(fn,phasecc011,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(6)
plt.title('Cross Correlation of Antennas 0 & 4')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 4')
plt.plot(fn,magcc04,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 4')
plt.plot(fn,phasecc04,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(7)
plt.title('Cross Correlation of Antennas 0 & 8')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 8')
plt.plot(fn,magcc08,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 8')
plt.plot(fn,phasecc08,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(8)
plt.title('Cross Correlation of Antennas 4 & 8')
plt.subplot(211)
plt.title('Magnitude Response of CC of 4 & 8')
plt.plot(fn,magcc48,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 4 & 8')
plt.plot(fn,phasecc48,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(9)
plt.title('Cross Correlation of Antennas 4 & 11')
plt.subplot(211)
plt.title('Magnitude Response of CC of 4 & 11')
plt.plot(fn,magcc411,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 4 & 11')
plt.plot(fn,phasecc411,'m')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.figure(10)
plt.title('Cross Correlation of Antennas 8 & 11')
plt.subplot(211)
plt.title('Magnitude Response of CC of 8 & 11')
plt.plot(fn,magcc811,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 8 & 11')
plt.plot(fn,phasecc811,'k')
plt.ylabel('Phase in Degrees')
plt.grid(True)

plt.show()
