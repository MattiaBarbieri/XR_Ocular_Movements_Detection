# XR-Ocular-Movements-Detection
Detecting Ocular Movements from HTC Vive Pro Eye (SRanipal) Raw Data with REMoDNaV. 


🧪 1. data_processing.py
    This module is the core of the data pre-processing:
    - Reads a .xlsx/.tsv/.txt file containing raw data.
    - Extracts and converts:
        - Gaze direction from 3D coordinates to pixels and visual degrees.
        - Head position and rotation into centimeters and degrees.
        - Also computes the absolute velocity of head and eyes.
        - Includes a plot_results() function to visualize:
            - Head position and rotation.
            - Gaze direction (in degrees and pixels).
            - Velocity.

🚀 2. launch_remodnav.py
    REQUIRES AN INPUT FILE
    Debug Configuration ---> Parameters ---> "file.xlsx/.tsv/.txt" "out"
    - Uses the DataProcessing class to convert data from the previous script.
    - Writes two files (outfile_l and outfile_r) for left and right eye.
    - Computes:
        - Average sample rate.
        - Minimum length for the Savitzky-Golay filter.
        - Launches RemoDNaV via subprocess for both eyes.
        - Prints the commands and RemoDNaV outputs.
        - Also includes a command to activate a virtual environment and re-run the commands in a Windows shell.

👁️‍🗨️ 3. ocular_detect.py
    REQUIRES THE FILE outfile_L or outfile_R (depending on which eye is being analyzed) AS INPUT
    - Analyzes the output files from RemoDNaV.
    - Extracts events (SACC, PURS, PSO, FIXA).
    - Computes statistics:
        - Count, amplitude, duration, velocity (mean, median, standard deviation).
        - Computes the PRL (Preferred Retinal Locus) from fixations.
        - Prints the results and saves them in a Data.tsv file.

👁️‍🗨️ 4. Eye_detection_GUI.py
    Trigger the process from GUI
