# Welcome to the Beacon AI Robotics/Edge Software Assessment!

## Problem

In the data/cessna_182t folder, you will find flight data dumps from a Cessna 182 Skylane. This is an aircraft we do not support, and we do not plan to use this data, so this data is provided just for interview purposes. The data is similarly structured to data for aircraft that we do support. Each CSV file contains data for a single flight, with each row containing values for specific parameters at the given timestamp. Not every CSV file is necessarily a complete flight - the data recorder may have been turned on late or turned off early. Additionally, there may be dropouts and/or noise in the data.

You have been given a starter implementation in Python of a simple takeoff detector which, given an input csv file, determines when a valid takeoff was initiated in the file if one is present. Bugs have been intentionally introduced in the implementation you have been provided. Some of these bugs will be obvious, and some will be more subtle. 

Your task is to debug the starter implementation so that it functions correctly. You should feel free to add some unit tests to check for correctness. Please keep track of the bugs you encounter and fix during this process.

Once you have debugged the starter implementation, you will need to make further additions to the code in order for it to comply with all of the requirements listed in the [Requirements](#requirements) section.


## Dependencies

Dependencies are given in the `requirements.txt` file. Feel free to use/include any others you'd like, within reason. If you have doubts about whether a library is allowed or not, please ask.

## Requirements

1. For the purposes of this take-home, a valid takeoff initiation is defined as one in which the following conditions are true:
    - The airplane is *on the ground* on the runway AND
    - Either of the following two conditions is true:
        - The airplane's ground speed is greater than 25 knots OR 
        - The airplane's engine rpm is greater than 1200 rpm.
    - AND the above conditions were not previously true (in other words, we are looking for the rising edge)
2. Your implementation must find the _first_ instance of a valid takeoff initiation in a data file, if one exists. If the file does not contain a takeoff which conforms to the requirements above, then the implementation should output `None` for the timestamp.

## Instructions for running
Create a virtual environment and install the packages in `requirements.txt`. Then, navigate to the `src` folder of this repository, and run `python3 takeoff_detector.py`. This will search the data directory for all CSVs, call the takeoff detector on each of them, and write the timestamp of detected takeoff to a file.

## Instructions for Submitting

1. Commit your changes to this repository. Tag the final commit you would like to submit with the tag `submission`. (`git tag submission` followed by `git push origin --tags`)
2. Include a file (.txt or .md) in which you
    - List/describe the steps you took to set up the environment
    - List/describe the bugs you found and fixed
    - Describe the additional code you added in order to comply with the requirements
3. After you submit, members of the team will review your submission and schedule a short (~30 minute) call to go over the assessment with you in more detail.

## Notes/Tips
1. It may be useful for your own understanding of the data (and to ensure you are catching edge cases) to add in some sort of visualization capability, but this is not required for the assignment