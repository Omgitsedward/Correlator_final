#	Eddie Toral
#	CAMPARE Summer 2016 Research Undergrad
#	August 16th, 2016
#	
#	Simple model used to obtain data to determine analog input level to digital output level relationship.
#	75.0 MHz single tone from input levels +12dBm to -36.0 dBm.
#	Direct connection to input of SNAP Board, no attenuators or filters used during testing.
#	Only 1 antenna at a time, selectable by [option] -a to be selected when running script
#	adc_stats_2016-8-16_1606.bof

from argparse import ArgumentParser
p = ArgumentParser(description = 'python adc_stats.py [options] ')
p.add_argument('host', type = str, default = '10.0.1.217', help = 'Specify the host name')
p.add_argument('-a', '--antenna', dest = 'antenna', type = int, default = 2047, help = 'antenna selection')

args = p.parse_args()
host = args.host
antenna = args.antenna

import corr, struct, numpy as np, matplotlib.pyplot as plt, time
s = corr.katcp_wrapper.FpgaClient(host,7147,timeout = 10)
time.sleep(1)
s.write_int('antenna',antenna)
s.write_int('cnt_rst',0)
s.write_int('cnt_rst',1)
s.write_int('cnt_rst',0)

print s.read_int('address')

adc_data = s.read('acd_data',65536)
ad = struct.unpack('>65536b',adc_data)
ad = np.asarray(ad)
time = np.linspace(0,65535,65536)

sigma = np.sqrt(np.var(ad))
print "Hey this one is sigma"
print sigma

rms = np.sqrt(np.mean(np.square(ad)))
print "Hey this one is rms"
print rms

plt.figure(1)
plt.title('adc data: Antenna %n',antenna)
plt.plot(time,ad,'k')
plt.axis([0,65535,-136,135])
plt.grid(True)

plt.figure(2)
plt.hist(ad, bins=256) 
plt.title("Histogram with 256 bins")
plt.show()
