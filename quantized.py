#used for various attempts to reduce resources to allow for 12 input correlation to fit on SNAP Board
import corr, struct, numpy as np, matplotlib.pyplot as plt, time

#--------------------------------------------------------------------------------------------------------------------------------------
from argparse import ArgumentParser
p = ArgumentParser(description = 'python quantized.py [options] ')
p.add_argument('host', type = str, default = '10.0.1.217', help = 'Specify the host name')
p.add_argument('-s', '--shift', dest = 'shift', type = int, default = 2047, help = 'set shift value for fft biplex block')
p.add_argument('-l', '--length', dest = 'length', type = int, default = 2e6, help = 'set # of spectra to be accumulated')
p.add_argument('-c', '--scale', dest = 'scale', type = int, default = 4096, help = 'scale coefficient')

args = p.parse_args()
host = args.host
shift = args.shift
length = args.length 
scale = args.scale

#--------------------------------------------------------------------------------------------------------------------------------------
print "Connecting to Fpga"
s = corr.katcp_wrapper.FpgaClient(host,7147,timeout = 10)
time.sleep(1)

#--------------------------------------------------------------------------------------------------------------------------------------
if s.is_connected():
	print "Connected"
else:
	print "Not connected"

#--------------------------------------------------------------------------------------------------------------------------------------
fn = np.linspace(0,511,512)

#--------------------------------------------------------------------------------------------------------------------------------------
print "Setting Shift value"
s.write_int('shift',shift)
print "Done"

#--------------------------------------------------------------------------------------------------------------------------------------
print "Starting accumulation process"
s.write_int('acc_len',length)
s.write_int('scale0',scale)
s.write_int('scale1',scale)
s.write_int('scale2',scale)
s.write_int('scale3',scale)

#--------------------------------------------------------------------------------------------------------------------------------------
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
overflow = s.read_int('overflow')
print overflow

#--------------------------------------------------------------------------------------------------------------------------------------
#Reading Data from BRAM Blocks
ac0 = np.asarray(struct.unpack('>512l',s.read('ac_a0_real',2048)))
ac1 = np.asarray(struct.unpack('>512l',s.read('ac_a1_real',2048)))
ac2 = np.asarray(struct.unpack('>512l',s.read('ac_a2_real',2048)))
ac3 = np.asarray(struct.unpack('>512l',s.read('ac_a3_real',2048)))

#--------------------------------------------------------------------------------------------------------------------------------------
#Autocorrelation of 0
magac0 = abs(ac0)
#Autocorrelation of 1
magac1 = abs(ac1)
#Autocorrelation of 2
magac2 = abs(ac2)
#Autocorrelation of 3
magac3 = abs(ac3)

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
plt.title('Autocorrelation of Antenna 1')
plt.title('Magnitude Response of AC of 1')
plt.plot(fn,magac1,'r')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.figure(3)
plt.title('Autocorrelation of Antenna 2')
plt.title('Magnitude Response of AC of 2')
plt.plot(fn,magac2,'c')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.figure(4)
plt.title('Autocorrelation of Antenna 3')
plt.title('Magnitude Response of AC of 3')
plt.plot(fn,magac3,'y')
plt.ylabel('Power (Arbitrary Units)')
plt.grid(True)

plt.show()
