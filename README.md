# Flight Sensor Data : Portfolio Project

## Project Overview

This project involves developing a **Takeoff Detection System** for flight data collected from an undisclosed aircraft. The task is to identify when a valid takeoff is initiated, based on specific conditions within flight data logs.
These logs, represented as CSV files, contain recorded parameters such as ground speed, engine RPM, and timestamp for each flight.
The data is organized into individual files, each representing a single flight, though the records may not always contain complete or noise-free data due to recording limitations.

## Problem Breakdown

### Data Format and Characteristics
- **Input Files**: Each CSV file contains flight data, with each row representing a specific timestamp and its associated flight parameters.
- **Potential Issues**: Data may have incomplete entries (e.g., the data recorder may be turned on late or off early) or contain dropouts and noise.
- **Valid Takeoff Detection**: The key challenge is to identify when a valid takeoff is initiated, based on specific conditions. A valid takeoff initiation occurs when:
  1. The aircraft is on the ground and within the runway bounds.
  2. The airplane’s engine RPM exceeds a certain RPM or its ground speed exceeds a certain threshold.
  3. Only the first case should be detected.

### Code Debugging and Development
1. Analyze the data files and determine edge case for takeoff detection logic.
2. Write functionality to detect the first valid takeoff initiation in a flight data file, if any.
3. Debug test cases by using visualization to determine correctness.
4. Adding appropriate unit tests to validate correctness.

### Requirements
- **Detect First Valid Takeoff**: The system must identify and return the timestamp of a valid takeoff initiation, if one exists. If no takeoff is detected, it should return `None`.
- **Edge Cases Handling**: Data may have noise or missing entries. The solution must handle these appropriately while ensuring correctness in the takeoff detection.

## Key Features and Functionality

1. **Takeoff Detection**:
   - The core feature is the ability to detect when the takeoff criteria are met: either a ground speed engine RPM exceeding 1500 RPM, while ensuring the airplane is on the ground and the conditions are rising for the first time.

2. **CSV Parsing and Data Handling**:
   - The code processes CSV files containing flight data, extracting relevant parameters such as ground speed and engine RPM.

3. **Edge Case Handling**:
   - The implementation accounts for noisy data, missing timestamps, and other inconsistencies that may arise due to incomplete data records.

4. **Visualization and Debugging**:
   - Visualization features were added for better understanding of the data and debugging. This helped in identifying edge cases and ensuring accurate takeoff detection.

5. **Unit Testing**:
   - Additional unit tests were added to validate the correctness of the takeoff detection system. These tests cover various scenarios, including edge cases where data might be incomplete or noisy.

## Setup Instructions

1. **Environment Setup**:
   - Create a virtual environment and install the required dependencies:
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use venv\Scripts\activate
     pip install -r requirements.txt
     ```

2. **Running the System**:
   - Navigate to the `src` directory and run the takeoff detector script:
     ```bash
     cd src
     python3 detector.py
     ```
   - This will process all the CSV files in the `data` directory, detect any takeoff initiations, and output the timestamp of the first valid takeoff found.

## Bugs Identified and Fixed

### 1. Incorrect Ground Speed Threshold:
   - The initial implementation had an incorrect threshold for ground speed, which was not being evaluated correctly. This was fixed by ensuring the speed exceeded 25 knots before considering the takeoff condition.

### 2. Engine RPM Threshold:
   - The engine RPM condition was misinterpreted, leading to incorrect takeoff detection. The logic was updated to correctly evaluate RPM thresholds greater than 1200 rpm.

### 3. Missing Data Handling:
   - Incomplete or missing data caused issues when evaluating conditions. The code was updated to skip over incomplete rows and continue processing valid entries.

### 4. Rising Edge Detection:
   - The starter code failed to correctly detect the "rising edge" of takeoff conditions. This was fixed by ensuring that the system tracks whether the conditions were previously false before detecting a valid takeoff.

## Additional Code Implemented

1. **Takeoff Initiation Detection**:
   - Code was added to specifically identify the first occurrence where both conditions for takeoff (speed > 25 knots or RPM > 1200) are met after the airplane has been on the ground.

2. **Unit Tests**:
   - Several unit tests were created to validate the accuracy of the takeoff detection logic under various conditions, including edge cases like missing timestamps or noisy data.

3. **Logging and Output**:
   - The system outputs the timestamp of the first valid takeoff initiation to a file for review. If no valid takeoff is detected, it outputs `None`.
