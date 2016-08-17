#	Eddie Toral
#	CAMPARE 2016 Summer Research Undergrad
#	August 16th 2016
#
#	4-input Correlator for SNAP Board
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
#	Model & code will Correlate all 4 inputs at the same time
#	small_scale_2016-8-16_1657.bof
#--------------------------------------------------------------------------------------------------------------------------------------
#Import necessary Libraries
import corr, struct, numpy as np, matplotlib.pyplot as plt, time

#--------------------------------------------------------------------------------------------------------------------------------------
#To incorporate options chosen w/ host
from argparse import ArgumentParser
p = ArgumentParser(description = 'python small_scale.py [options] ')
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
#If FFT Biplex block overflows, the output here would be 1
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

#Cross Correlation Data
#Antenna 0 Cross 1 - 3
cc01r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a1_real',2048)))
cc01i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a1_imag',2048)))
cc02r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a2_real',2048)))
cc02i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a2_imag',2048)))
cc03r = np.asarray(struct.unpack('>512l',s.read('cc_a0_a3_real',2048)))
cc03i = np.asarray(struct.unpack('>512l',s.read('cc_a0_a3_imag',2048)))

#Antenna 1 Cross 2 - 3
cc12r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a2_real',2048)))
cc12i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a2_imag',2048)))
cc13r = np.asarray(struct.unpack('>512l',s.read('cc_a1_a3_real',2048)))
cc13i = np.asarray(struct.unpack('>512l',s.read('cc_a1_a3_imag',2048)))

#Atenna 2 Cross 3
cc23r = np.asarray(struct.unpack('>512l',s.read('cc_a2_a3_real',2048)))
cc23i = np.asarray(struct.unpack('>512l',s.read('cc_a2_a3_imag',2048)))

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

#Cross Correlation of 2 and 3
cc23rl = list(cc23r)
cc23il = list(cc23i)
cc23 = merge(cc23rl,cc23il)
magcc23 = abs(cc23)
phasecc23 = np.angle(cc23)*180/np.pi

#--------------------------------------------------------------------------------------------------------------------------------------
print "Plotting Data"
#Autocorrelation Plots
plt.figure(1)
plt.title('Autocorrelation of Antenna 0')
plt.title('Magnitude Response of AC of 0')
plt.plot(fn,magac0,'g')
plt.ylabel('Power (Arbitrary Units)')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(2)
plt.title('Autocorrelation of Antenna 1')
plt.title('Magnitude Response of AC of 1')
plt.plot(fn,magac1,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(3)
plt.title('Autocorrelation of Antenna 2')
plt.title('Magnitude Response of AC of 2')
plt.plot(fn,magac2,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(4)
plt.title('Autocorrelation of Antenna 3')
plt.title('Magnitude Response of AC of 3')
plt.plot(fn,magac3,'y')
plt.ylabel('Power (Arbitrary Units)')
plt.xlabel('Channel')
plt.grid(True)

#--------------------------------------------------------------------------------------------------------------------------------------
#Cross Correlation Plots

plt.figure(5)
plt.title('Cross Correlation of Antennas 0 & 1')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 1')
plt.plot(fn,magcc01,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 1')
plt.plot(fn,phasecc01,'k')
plt.ylabel('Phase in Degrees')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(6)
plt.title('Cross Correlation of Antennas 0 & 2')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 2')
plt.plot(fn,magcc02,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 2')
plt.plot(fn,phasecc02,'m')
plt.ylabel('Phase in Degrees')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(7)
plt.title('Cross Correlation of Antennas 0 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 0 & 3')
plt.plot(fn,magcc03,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 0 & 3')
plt.plot(fn,phasecc03,'k')
plt.ylabel('Phase in Degrees')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(8)
plt.title('Cross Correlation of Antennas 1 & 2')
plt.subplot(211)
plt.title('Magnitude Response of CC of 1 & 2')
plt.plot(fn,magcc12,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 1 & 2')
plt.plot(fn,phasecc12,'k')
plt.ylabel('Phase in Degrees')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(9)
plt.title('Cross Correlation of Antennas 1 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 1 & 3')
plt.plot(fn,magcc13,'m')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 1 & 3')
plt.plot(fn,phasecc13,'m')
plt.ylabel('Phase in Degrees')
plt.xlabel('Channel')
plt.grid(True)

plt.figure(10)
plt.title('Cross Correlation of Antennas 2 & 3')
plt.subplot(211)
plt.title('Magnitude Response of CC of 2 & 3')
plt.plot(fn,magcc23,'k')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)
plt.subplot(212)
plt.title('Phase Response of CC of 2 & 3')
plt.plot(fn,phasecc23,'k')
plt.ylabel('Phase in Degrees')
plt.xlabel('Channel')
plt.grid(True)

plt.show()
