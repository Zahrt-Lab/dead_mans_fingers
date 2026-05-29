1) After finishing one analog, it prompts if one wants to start a new run or resume an older. The decision should be made only once every experiment run. (Need to figure out a way to prevent this from occurring where is the ax folder being saved.)

2) Make sure emergency stop works. (4/29/2026) S

3) Make sure it converges at steady state. (4/29/2026) S

4) Need to make sure valve position is set correctly for each xylopyridine analog. (Should probably do this in the priming run)

5) Need a priming protocol, think about this (4/31/2026) COMPLETED

6) Need to get blank and dark spectra while solution is running, need a test or check to make sure it was properly blanked (4/29/2026)

7) We can think of tracking the absorbance at a wavelength far from the chromophore absorbance, perhaps around 700 nm. That would capture any change in the baseline. (Same idea is point 6)

8) Make option to get rid of the cosolvent (Future TODO). In other words, accept high boudary = 0 (Workaround found)

9) Include a warnings if flow rate any pump is below 25 uL/min (4/29/2026) S (COMPLETE)

10) Add temporary patch to set cosolvent range from 0 to 0 (4/29/2026) S (Workaround found)

11) There is a bug in the generate_instrument_config.py. If com_ports, then ports.update runs and gives an error. Something about different dictionary sizes. I came across this when developing the priming function. I guess update has never been called so far, that's why we never had this bug before. 

12) Instead of having it turn on and off again between each run (30 trials), we could have it turn on and off again every 2 hours, thus minimizing the amount of times we do this while improving the accuracy. (Moderate Priority)

13) Adjust flow rate of pump 4 during wash step so it is equal to the flow rate used in experiment 4. (High Priority) Solved

14) Modify the wash commands to do the UV callibration there, then load those results to test 4. (Moderate Priority) Solved



