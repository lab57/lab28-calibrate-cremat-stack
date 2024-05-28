#
# Copyright (C) 2018 Pico Technology Ltd. See LICENSE file for terms.
#
# PicoScope 3000 (A API) Series Signal Generator Example
# This example demonstrates how to use the PicoScope 3000 Series (ps3000a) driver API functions to set up the signal generator to do the following:
# 
# 1. Output a sine wave 
# 2. Output a square wave 
# 3. Output a sweep of a square wave signal

import ctypes
from email.errors import BoundaryError
from picosdk.ps3000a import ps3000a as ps
import time
from picosdk.functions import assert_pico_ok
import numpy as np
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok, mV2adc
from tqdm import tqdm 

def openDevice():
    """
    Opens the picoscope 3000a device. Returns chandle, the device.
    
    """

    print("Opening unit")
    status = {}
    chandle = ctypes.c_int16()

    # Opens the device/s
    status["openunit"] = ps.ps3000aOpenUnit(ctypes.byref(chandle), None)

    try:
        assert_pico_ok(status["openunit"])
    except:

        # powerstate becomes the status number of openunit
        powerstate = status["openunit"]

        # If powerstate is the same as 282 then it will run this if statement
        if powerstate == 282:
            # Changes the power input to "PICO_POWER_SUPPLY_NOT_CONNECTED"
            status["ChangePowerSource"] = ps.ps3000aChangePowerSource(chandle, 282)
        # If the powerstate is the same as 286 then it will run this if statement
        elif powerstate == 286:
            # Changes the power input to "PICO_USB3_0_DEVICE_NON_USB3_0_PORT"
            status["ChangePowerSource"] = ps.ps3000aChangePowerSource(chandle, 286)
        else:
            raise

        assert_pico_ok(status["ChangePowerSource"])
    print("Sucess")
    return chandle

def set_square_wave(chandle, frequency_hz, amplitude_v):
    """ Set the function generator to output a square wave.

    Args:
        chandle (ctypes.c_int16): The handle of the PicoScope device.
        frequency_hz (float): Frequency of the square wave in Hz.
        amplitude_v (float): Amplitude of the square wave in volts.

    """
    print(f"Setting square wave f={frequency_hz} hz, A={amplitude_v} V")
    # Convert amplitude from volts to microvolts because ps3000a API uses microvolts for amplitude settings
    amplitude_uv = int(amplitude_v * 1e6)
    offset_voltage_uv = 0
    wave_type = ctypes.c_int16(1)  # PS3000A_SQUARE
    sweep_type = ctypes.c_int32(0) # PS3000A_UP
    trigger_type = ctypes.c_int32(0) # PS3000A_SIGGEN_RISING
    trigger_source = ctypes.c_int32(0) # P3000A_SIGGEN_NONE
    
    status = ps.ps3000aSetSigGenBuiltIn(chandle, offset_voltage_uv, amplitude_uv, wave_type, frequency_hz, frequency_hz, 0, 1, sweep_type, 0, 0, 0, trigger_type, trigger_source, 1)
    assert_pico_ok(status)

import ctypes
from picosdk.ps3000a import ps3000a as ps
from picosdk.functions import assert_pico_ok, adc2mV
import numpy as np
import matplotlib.pyplot as plt


def calculate_samples(n, T):
    """
    n: timebase number
    T: sample width in seconds
    
    """
    sample_interval = (n - 2) / 125000000
    num_samples = int(T / sample_interval)
    return num_samples

rangeMap = {
    .01:ps.PS3000A_RANGE["PS3000A_10MV"],
    .02:ps.PS3000A_RANGE["PS3000A_20MV"],
    .05:ps.PS3000A_RANGE["PS3000A_50MV"],
    .1:ps.PS3000A_RANGE["PS3000A_100MV"],
    .2:ps.PS3000A_RANGE["PS3000A_200MV"],
    .5:ps.PS3000A_RANGE["PS3000A_500MV"],
    1:ps.PS3000A_RANGE["PS3000A_1V"],
    2:ps.PS3000A_RANGE["PS3000A_2V"],
    5:ps.PS3000A_RANGE["PS3000A_5V"],
    10:ps.PS3000A_RANGE["PS3000A_10V"],
    20:ps.PS3000A_RANGE["PS3000A_20V"],
    50:ps.PS3000A_RANGE["PS3000A_50V"],
}

rangeMapInv = dict((v, k) for k, v in rangeMap.items())

def take_and_plot_sample(chandle, channel, trigger_mv, window, range):
    """ Take a sample of data from a specified channel with trigger settings and plot the data.
    
    Args:
        chandle (ctypes.c_int16): The handle of the PicoScope device.
        channel (int): Channel number (0 for Channel A, 1 for Channel B, etc.).
        trigger_mv (int): Trigger voltage in millivolts.
        window. Width of the sample window in seconds,
        range: Enum voltage range. Use rangemap to get.
    """

    if not (0 <= range <= 11):
        raise ValueError(f"Range must be in {rangeMap.values()}. Use rangeMap to convert V to this.")
    print(f"Sampling Data. Channel={channel}, trigger={trigger_mv}mV, window={window}, range={range}")
    # Set up the specified channel
    enabled = 1
    coupling_type = ps.PS3000A_COUPLING["PS3000A_AC"]
    #voltage_range = ps.PS3000A_RANGE["PS3000A_100MV"]  # Adjust this based on your needs, corresponds to ±10V
    voltage_range = range
    analogue_offset = 0#-.04
    status_set_channel = ps.ps3000aSetChannel(chandle, channel, enabled, coupling_type, voltage_range, analogue_offset)
    TRIGGER_CHANNEL = 3 #channel D
    status_set_channel2 = ps.ps3000aSetChannel(chandle, TRIGGER_CHANNEL, enabled, coupling_type, ps.PS3000A_RANGE["PS3000A_20MV"], analogue_offset)

    assert_pico_ok(status_set_channel)

    # Prepare the trigger using mV2adc for precise ADC threshold setting
    max_adc = ctypes.c_int16()
    ps.ps3000aMaximumValue(chandle, ctypes.byref(max_adc))
    threshold_adc = mV2adc(trigger_mv, voltage_range, max_adc)
    threshold_adc = mV2adc(0, voltage_range, max_adc)
    # Set up trigger
    trigger_direction = 3  # PS3000A_FALLING
    auto_trigger_ms = 1000
    status_set_trigger = ps.ps3000aSetSimpleTrigger(chandle, 1, TRIGGER_CHANNEL, threshold_adc, trigger_direction, 0, auto_trigger_ms)
    assert_pico_ok(status_set_trigger)
    

    # Determine the timebase
    window_width = window
    timebase =  3
    n_samples = calculate_samples(timebase, window_width)
  
    #no_samples = int((sample_window_us * 1000) / 8)  # Needs adjustment based on actual interval
    preTrigSamples = n_samples//2
    postTrigSamples = n_samples//2
    maxSamples = preTrigSamples + postTrigSamples
    #print(f"Taking data. Timebase: {timebase}, window width: {window_width} s, trigger: {trigger_mv}mV")
    #print(f"Taking {maxSamples} samples")
    time_interval_ns = ctypes.c_float()
    max_samples = ctypes.c_int16()
    status_get_timebase = ps.ps3000aGetTimebase2(chandle, timebase, maxSamples, ctypes.byref(time_interval_ns), 0, ctypes.byref(max_samples), 0)
    assert_pico_ok(status_get_timebase)

    # Allocate memory for the buffer
    buffer_a = (ctypes.c_int16 * maxSamples)()
    overflow = ctypes.c_int16()
    status_set_buffers = ps.ps3000aSetDataBuffers(chandle, channel, ctypes.byref(buffer_a), None, maxSamples, 0, 0)
    assert_pico_ok(status_set_buffers)

    # Start the block capture
    status_run_block = ps.ps3000aRunBlock(chandle, preTrigSamples, postTrigSamples, timebase, 1, None, 0, None, None)
    assert_pico_ok(status_run_block)

    # Check for device readiness
    ready = ctypes.c_int16(0)
    while not ready.value:
        ps.ps3000aIsReady(chandle, ctypes.byref(ready))

    # Retrieve data
    status_get_values = ps.ps3000aGetValues(chandle, 0, ctypes.byref(ctypes.c_int32(maxSamples)), 0, 0, 0, ctypes.byref(overflow))
    assert_pico_ok(status_get_values)

    # Convert ADC counts to mV
    data_mv = adc2mV(buffer_a, voltage_range, max_adc)

    # Correct time scaling: calculate total time in microseconds
    #total_time_us = no_samples * time_interval_ns.value / 1000  # Convert ns to us
    #time_axis = np.linspace(0, total_time_us, no_samples)  # Time axis in microseconds
    cmaxSamples = ctypes.c_int32(maxSamples)
    time = np.linspace(-(window_width/2 * 1e6), (window_width/2 * 1e6), cmaxSamples.value)
    print("Done\n")

    return time, data_mv
    # Plotting

def plotSample(time, data_mv):
    plt.plot(time, data_mv)
    plt.xlabel('Time (us)')
    plt.ylabel('Voltage (mV)')
    plt.title(f'Sampled Data')
    #plt.ylim(top=rangeMapInv[range]*1e3)
    plt.show()

    return data_mv  # Optionally return data for further processing



def takeDataVal(chandle, siggen_amp, range = rangeMap[0.1], trigger=20, window=1e-3, channel=2):
    """
    Take data and validate it doesnt max out the range
    """
    set_square_wave(chandle, 90, siggen_amp)
    time.sleep(.1)
    t, data = take_and_plot_sample(chandle, channel, trigger, window, range)
    max_amp = max(data)*1e-3 #convert to volts
    if abs(max_amp - rangeMapInv[range]) < .0001:
        print("Maxed out range")
        raise BoundaryError(f"Signal out of voltage range ({max_amp} V). Increase range and try again.")

    return t, data


def getSamples(chandle, inputs, range, trigger, window):
    """
    Sweep inputs and take data for each one
    
    """
    cur_range = range
    data_samples = []
    times = []

    if isinstance(trigger, int) :
        trig_mv = trigger
    for i, i_v in enumerate(inputs):
        if isinstance(trigger, list) or isinstance(trigger, np.ndarray):
            trig_mv = trigger[i]
            
        while True:
            try:
                t, data = takeDataVal(chandle, i_v, cur_range, trig_mv, window)
                break
            except BoundaryError:
                cur_range += 1
                print(f"Signal out of range, increasing max range to +- {rangeMapInv[cur_range]} V\n")
        times.append(t)
        data_samples.append(data)

    return times, data_samples
    

from scipy.optimize import curve_fit

def gauss(x, A, mu, sigma, b):
    return A*np.exp(-(x-mu)**2/(2*sigma**2)) + b

def fitGaussian(time, data, p0=(100, 0, .5,  0)):
    ps, cov = curve_fit(gauss, time, data, p0=p0)
    errs = np.sqrt(np.diag(cov))
    return ps, errs

def getGains(times, datas):
    gains = []
    gains_err = []
    print("Fitting Gaussians")
    for t_axis, data in tqdm(zip(times, datas)):
        ps, errs = fitGaussian(t_axis, data)
        gains.append(ps[0])
        gains_err.append(errs[0])
    return gains, gains_err

        
if __name__ == "__main__":


    chandle = openDevice()

    print("Beginning test")
    initRange = rangeMap[2]
    t, datas = getSamples(1, initRange, 800, 5e-6)
    #plotSample(t, data)

    gains, gains_err = getGains(t, datas)
    print("gains", gains)
    plt.scatter(initRange, gains)
    plt.show()

    print("Closing Unit")
    # Closes the unit
    # Handle = chandle
    status = ps.ps3000aCloseUnit(chandle)
    assert_pico_ok(status)

    print("Closed")