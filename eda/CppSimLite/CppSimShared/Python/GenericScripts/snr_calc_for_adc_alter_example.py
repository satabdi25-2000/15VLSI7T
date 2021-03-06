from __future__ import division

# import cppsimdata module
import sys
import os
cppsimsharedhome = os.getenv("CPPSIMSHAREDHOME")
if cppsimsharedhome != None:
   CPPSIMSHARED_PATH = '%s' % cppsimsharedhome
else:
   HOME = os.getenv("HOME")
   CPPSIMSHARED_PATH = '%s/CppSim/CppSimShared' % HOME

sys.path.append(CPPSIMSHARED_PATH + '/Python')
from cppsimdata import *

# import pylab package
from pylab import *

from scipy.signal import lfilter,welch,hann
from scipy import fft

fig = figure(1)
fig.clf()

filename = 'test_globals.tr0'
data = CppSimData(filename)
noise_enable_ktc1 = data.evalsig('noise_enable_ktc_gl1')
noise_enable_ktc2 = data.evalsig('noise_enable_ktc_gl2')
noise_enable_ktc3 = data.evalsig('noise_enable_ktc_gl3')
noise_enable_amp = data.evalsig('noise_enable_amp_gl')


alter_range = range(3)
# alter_range = [5]
for alter_val in alter_range:

   filename = 'test_out.tr%d' % alter_val 
   print "loading file '%s'" % filename
   data = CppSimData(filename)
   dout = data.evalsig('dout')
   t = data.evalsig('TIME')
   t_delta = lfilter([1,-1],[1],t)
   Ts = mean(t_delta[1:-1])
   fs = 1/Ts

   # assume dout corresponds to 1-bit Delta-Sigma sequence alternating between 0 and 1
   dout_mean = mean(dout)
   dout[dout < dout_mean] = 0
   dout[dout > dout_mean] = 1

   N = len(dout)
   hwin = hann(N)

   dout_win = dout*hwin
   # remove low frequency spectral bleeding
   dout_minus_mean = dout - mean(dout_win)/mean(hwin)
   dout_win = dout_minus_mean*hwin

   s_out = (4/sum(hwin)*absolute(fft(dout_win,N)))**2
   freq = arange(N)*1/N

   # look at frequencies in range of input sine wave
   bw = 1/(100*2)  # oversampling of 100 assumed
   f_ind_bw = freq[:] <= bw
   freq_bw = freq[f_ind_bw]
   s_out_bw = s_out[f_ind_bw]
   s_ind_max = argmax(s_out_bw)

   signal_power_raw = s_out_bw[s_ind_max] + s_out_bw[s_ind_max-1] + s_out_bw[s_ind_max+1]
   noise_power_raw = sum(s_out_bw) - signal_power_raw

   # scale signal and noise power by 2/3 due to Hann window
   signal_power = 2/3*signal_power_raw
   noise_power = 2/3*noise_power_raw
   sqnr_log = 10*log10(signal_power/noise_power)
   print "Signal Power:  %5.2f dB, Noise Power: %5.2f dB, SNR = %5.2f dB" % (10*log10(signal_power),10*log10(noise_power),sqnr_log)

   plot_label = 'ktc1=%d, ktc2=%d, ktc3=%d, amp=%d' % (noise_enable_ktc1[alter_val], noise_enable_ktc2[alter_val], noise_enable_ktc3[alter_val], noise_enable_amp[alter_val])
   semilogx(freq,10*log10(s_out),label=plot_label)

axis([1e-6, 0.5, -260, 0])
xlabel('Normalized Frequency (f/fs)')
ylabel('Spectral Density')
title('Simulated Spectral Density using CppSim')
grid(True,which='both')
legend(loc='upper right',prop={'size':10})
fig.show()
