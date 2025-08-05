import sys
from math import ceil
from data_processing import DataProcessing
import subprocess
import os

def calc_sample_rate(times):
    dtime = 0
    prev_time = times[0]
    for this_time in times[1:]:
        dtime += float(this_time) - float(prev_time)
        prev_time = this_time
    dtime /= len(times) - 1
    return 1.0 / dtime

def write_remodnav_file(indata, outfile):
    lx, ly, rx, ry = indata[0]
    head_pos_x, head_pos_y, head_pos_z = indata[3]
    roll_x, pitch_y, yaw_z = indata[4]

    with open(outfile + "l", 'w') as fl, open(outfile + "r", 'w') as fr:
        for i in range(len(lx)):
            fl.write("{:.6f}\t{:.6f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.2f}\t{:.2f}\t{:.2f}\n".format(
                lx[i], ly[i], head_pos_x[i], head_pos_y[i], head_pos_z[i], roll_x[i], pitch_y[i], yaw_z[i]))
            fr.write("{:.6f}\t{:.6f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.2f}\t{:.2f}\t{:.2f}\n".format(
                rx[i], ry[i], head_pos_x[i], head_pos_y[i], head_pos_z[i], roll_x[i], pitch_y[i], yaw_z[i]))

def calc_min_savgol(sample_rate):
    decimals = 5
    sl = 5.0 / sample_rate
    factor = 10 ** decimals
    return ceil(sl * factor) / factor

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage " + sys.argv[0] + " <infile> <outfile_prefix>")
    else:
        conv = DataProcessing(sys.argv[1])
        data = conv.gaze_conversion()
        head_pos = conv.head_pos_conversion()
        head_rot = conv.head_rot_conversion()
        Kpix_deg = 0.068055
        write_remodnav_file((data[0], data[1], data[2], head_pos, head_rot), sys.argv[2])
        sample_rate = calc_sample_rate(data[2])
        print("average sample rate: {:f}".format(sample_rate))
        savgol = calc_min_savgol(sample_rate)
        print("mininum savgol len: ~{:f}".format(savgol))
        print("remodnav --savgol-length {:f} ".format(savgol) +
              sys.argv[2] + "l outfile_l {:f} {:f}".format(Kpix_deg, sample_rate))
        print("remodnav --savgol-length {:f} ".format(savgol) +
              sys.argv[2] + "r outfile_r {:f} {:f}".format(Kpix_deg, sample_rate))

        cmd_left = f"remodnav --savgol-length {savgol:.6f} {sys.argv[2]}l outfile_l {Kpix_deg:.6f} {sample_rate:.6f}"
        cmd_right = f"remodnav --savgol-length {savgol:.6f} {sys.argv[2]}r outfile_r {Kpix_deg:.6f} {sample_rate:.6f}"

        print("Running RemoDNaV for left eye:")
        result_left = subprocess.run(cmd_left, shell=True, capture_output=True, text=True)
        print("STDOUT (left):", result_left.stdout)
        print("STDERR (left):", result_left.stderr)

        print("Running RemoDNaV for right eye:")
        result_right = subprocess.run(cmd_right, shell=True, capture_output=True, text=True)
        print("STDOUT (right):", result_right.stdout)
        print("STDERR (right):", result_right.stderr)

        project_dir = r"C:\Users\mbarbieri\PycharmProjects\RealterAnalysis"
        activate_script = os.path.join(project_dir, "venv", "Scripts", "activate.bat")
        full_command = f'cmd.exe /k "cd /d {project_dir} && call {activate_script} && {cmd_left} && {cmd_right}"'
        subprocess.Popen(full_command, shell=True)