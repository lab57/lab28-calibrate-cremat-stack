#import "template.typ": *

// Take a look at the file `template.typ` in the file panel
// to customize this template and discover how it works.
#show: project.with(
  title: "Lab 28 Signal Processing",
  authors: (
    (name: "Luc Barrett", email: "labarrett@umass.edu", affiliation: "Kumar Lab 028"),
  ),
  date: datetime.today().display("[month repr:long] [day], [year]"),
)
#set heading(numbering: "1.1")
#outline()
#pagebreak()
= Charge Sensitive Preamplifier

== Function & Purpose
A Charge Sensitive Preamplifier (CSP) is a device used for detecting electrical pulses from detectors.  A CSP can take in a pulse of current, and in its most basic form, the result is proportional to the integral of charge passing through
#align(center, 
grid(
  columns: 2, rows: 1,
figure(image("SimpleCircuit.jpg", height: 20%), caption: [Simplified circuit diagram]),
figure(
  image("CSP_pulses.jpg", width: 50%), caption: [Detector pulse and resulting signal from CSP]
)
))

This arrangement is generally problematic, as multiple pulses will keep causing an increase to an unbounded size. This can be resolved by adding a bleed resistor

#figure(image("bleed.jpg", height: 20%), caption: [More typical circuit digram including the bleed resistor $R_f$])

#figure(image("taildecay.jpg", height: 30%), caption: [Resulting pulse from introducing the bleed resistor])

This pulse will decay with a time constant of $tau = C_f R_f$. It is not depdendant on any other properties of the pulse, though a slow rise time will affect the overall shape.

== Calibration

To know the gain of the CSP, we must inject it with a current pulse with a known charge. To do so, a capacitor can be placed in series with a function generator producing a square wave. Then, when there is a change in voltage, the amount of charge injected is
$ Q = C_f Delta V$ (discussed more in the next section). In the evaluation boards, there is one of these capacitors with $C_f=1 "pF"$ already in the test input.


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

= Shaper
== Introduction and Purpose
The CR-200 is a Gaussian shaping amplifier module, and is used to read out the “tail pulse” signals such as from charge sensitive preamplifiers, PMTs, and other similar detection circuits. Gaussian shaping amplifiers are also known as 'pulse amplifiers', 'linear amplifiers', or 'spectroscopy amplifiers' in the general literature. They accept a step-like input pulse and produce an output pulse shaped like a Gaussian function (bell curve). The purpose of these amplifiers is not only to transform the shape of the event pulse from a tail pulse to a bell curve, but also to filter much of the noise from the signal of interest. Use of shaping amplifiers will reduce the fall time of the pulse signals, reducing the incidence of pulse 'pile up', and improve the signal-to-noise of the detection system.

#figure(
  image("shaper_func.jpg", width: 70%),
  caption: [Response of shaper unit]
)

The shaping time is defined as the time-equivalent of the "standard deviation" of the Gaussian output pulse. A simpler measurement to make in the laboratory is the full width of the pulse at half of it's maximum value (FWHM). This value is greater than the shaping time by a factor of 2.4. For example, a Gaussian shaping amplifier with a shaping time of 1.0 $mu s$ would have a FWHM of 2.4 $mu s$.

== Modification and Calibration
The shaper has it's own gain that can be adjusted with controls on the front of the device. Calibration hasnt been done yet as these controls could change. It will still be proportional to the total charge of the pulse.
=== Jumper Wire
In the absense of a CR-200X module, as in our case, a jumper wire had to be installed that was previously missing. This was done according to the documentation of the unit.
#figure(image("DS0053.png", height: 40%), caption: [View from oscilliscope, with same color coorrespondance as before. The view is zoomed in to make the signal of the shaper clear])<osc-zoomed>