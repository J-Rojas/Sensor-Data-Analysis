# Environment

0. I am using a Mac M1 Laptop. I also had to add 'matplotlib' to the requirements.txt
1. Installed 'geos' via Brew on MacOS
2. python3.11 -m venv myenv
3. source myenv/bin/activate
4. pip3 install -r requirements.txt

# Bug Fixes

1. The CSV files were not loading properly due to problems with extra white space used as delimiter between fields. This was fixed by using a delimiter regular expression to identify the extra whitespace.
2. Also the column header row needed to be supplied to propertly read the CSVs, which in this case was on line 1 of each CSV.
3. The running averages were not working correctly using the Numpy convolve function which expects 1D arrays. I fixed by convolving each column separately, then using mode='same' to maintain the same number of output data samples as the original input.
4. I increased the running average to 10 samples to reduce noise. In certain cases, the engine RPM would spike above 1200 while the aircraft was manuvering on the ground which caused false positive detections for the takeoff. Extending the window to this value removed the false positives.
5. I found a bug in the low pass filter code where a higher alpha was decreasing the smoothing. The docstring suggested increasing the alpha should increase the smoothing so the code was modified to fix this. The additional noise filtering is used with the engine RPM signal.

# Code Additions

1. I added extra code to detect if the aircraft was on the ground prior to takeoff. This was done by checking that the altitude of the aircraft during some point when the aircraft was not moving was similar within some error tolerance when the aircraft takes off. This filtered out an edge case where the aircraft was already airborne during the sensor recordings.
2. After visualizing the flight data, I noticed there was always a spike in the engine RPM prior to a takeoff. This spike always occurred more than a minute before the takeoff, thus I interpreted this as a preflight engine check. With some research, I determined this is done prior to entering the runway, thus the preflight engine check became a clear indicator of an emminient takeoff and presence on the runway. I detected the preflight engine check by monitoring the rise and fall of the engine RPM using threshold values. A class called 'SpikeDetect' was used to cleanly monitor this state. There was at least one data file that had a preflight check but no actual takeoff from the ground, so this edge case was handled correctly.
3. I ensured the OR condition for the engine RPM and ground speed was correctly implemented. However I never encountered a case where the engine speed reached the threshold before the engine RPM reached 1200 rpm. This would make sense as the engine provides the thrust for the aircraft speed to increase, thus there is a delayed response with the ground speed with respect to the engine RPM.
4. I checked the runway and ground presense detections occur before the engine RPM or ground speed reach critical threshold values.

5. A unit test was added to test the takeoff detection. The test determines when the aircraft first leaves the ground and finds the first instance of engine RPM or ground speed that happens before this event. It confirms the takeoff initiation timestamp is the same this test-predicted timestamp.

