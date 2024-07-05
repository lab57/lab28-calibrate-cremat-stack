== Performing Calibration
To calibrate the CSP, a BNC splitter was attatched to the output of a function generator.  One output went directly into the oscilloscope, and the other went into the CSP. The output voltage of the two branches are reduced from the original output, but are equal. The function generator would be set to a square wave, and the amplitude would be measured. The signal would then be sent through the preamplifier. As described above, the test input of the CR-110 has a 1 pF capacitor in series. The square wave going through this capacitor will result in sending a burst of current (or bundle of electrons) through into the preamplifier, similar to what the output of a detector would look like (@test-waveforms).

#figure(
  image("test-waveforms.jpg", width: 95%),
  caption: [Waveforms from wave generatorm, after capacitor, and after the preamp. (Source: Cremat Inc)]
)<test-waveforms>

 The total charge of this bundle can be calculated as 
$ Q = C_f V $
Where $C_f$ is the capacitance of the capacitor and $V$ is peak-to peak-voltage difference of the square wave.
The output of the preamplifier is fed back into the oscilloscope as well, so we can measure the amplitude of the peaks. Doing this for various voltages, we expect a linear relationship and can extract the slope as the sensitivity or gain of the preamp.

#figure(image("DS0052.png", height: 40%), caption: [View from oscilloscope of function generator signal (yellow), preamp (blue), and shaper (pink). The pulse width of the shaper is so small it is difficult to see in this image; Refer to @osc-zoomed])
#figure(image("VperN.png", height: 40%), caption: [Output Voltage per Electron])
#figure(image("VperQ.png", height: 40%), caption: [Output Voltage per Charge])
#pagebreak()
#figure(table(columns: (auto,auto,  auto),
[*Input $Delta V$  (V)*], [*Converted Charge (fC)*], [*Output Voltage (V)*],
[0.04], [39], [0.02],
[0.05], [50], [0.03],
[0.12],[	120],	[0.13],
[0.25],[	252],	[0.28],
[0.58],[	584],	[0.66],
[1.04],[	1,040],	[1.20],
[1.72],[	1,720],	[1.92],
[1.96],[	1,960],	[2.16],
[2.44],[	2,440],	[2.64],
[2.76],[	2,760],	[3.04],
), caption: [Calibration Data taken in the week of 6/16/23])


The equation for fitting is $ V = alpha Q $
Where $alpha$ is the resulting output gain per charge. From this fit we arrive at a value for $alpha= 1.1 "V " slash "pC"$, or about 0.822 mV per 5000 electrons $approx$ 1 mV per 6082 electrons.

== Future tasks
This gain differs from the spec calibration of 1.4 V/pC. To confirm if the value is correct, I want to take more measurements using a different capacitor of seperately measured capacitance, going into the main input, bypassing the built in capacitor. 

There is existing data from a previous paper from this unit, but the measurements are taken at lower input voltages than our function generator can reliably produce. It would be nice to borrow another one that might be able to do this.