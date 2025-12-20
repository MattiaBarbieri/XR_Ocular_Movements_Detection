import sys
import scipy
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


class DataProcessing(object):

    def __init__(self, infile):
        self.infile = infile
        self._read_data()

    def _read_data(self):
        # Upload file according to its extension
        if self.infile.endswith('.xlsx'):
            df = pd.read_excel(self.infile)
        elif self.infile.endswith('.tsv') or self.infile.endswith('.txt'):
            df = pd.read_csv(self.infile, sep='\t')
        else:
            raise ValueError("File format not supported. Use instead .xlsx, .tsv o .txt")

        # Colimns Check
        expected_columns = [
            "time_unity", "eye_valid_L", "eye_valid_R",
            "gaze_origin_L.x(mm)", "gaze_origin_L.y(mm)", "gaze_origin_L.z(mm)",
            "gaze_direct_L.x", "gaze_direct_L.y", "gaze_direct_L.z",
            "pupil_position_L.x", "pupil_position_L.y",
            "gaze_contingency_L.x", "gaze_contingency_L.y",
            "gaze_origin_R.x(mm)", "gaze_origin_R.y(mm)", "gaze_origin_R.z(mm)",
            "gaze_direct_R.x", "gaze_direct_R.y", "gaze_direct_R.z",
            "pupil_position_R.x", "pupil_position_R.y",
            "gaze_contingency_R.x", "gaze_contingency_R.y",
            "head.position.x", "head.position.y", "head.position.z",
            "head.rotation.x", "head.rotation.y", "head.rotation.z", "head.rotation.w"
        ]

        missing = [col for col in expected_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns in file: {missing}")


        # Assign data to Class
        self.time = df["time_unity"]
        self.eye_valid_L = df["eye_valid_L"]
        self.eye_valid_R = df["eye_valid_R"]

        self.gaze_origin_Lx = df["gaze_origin_L.x(mm)"]
        self.gaze_origin_Ly = df["gaze_origin_L.y(mm)"]
        self.gaze_origin_Lz = df["gaze_origin_L.z(mm)"]

        self.gaze_direct_Lx = df["gaze_direct_L.x"]
        self.gaze_direct_Ly = df["gaze_direct_L.y"]
        self.gaze_direct_Lz = df["gaze_direct_L.z"]

        self.pupil_position_Lx = df["pupil_position_L.x"]
        self.pupil_position_Ly = df["pupil_position_L.y"]

        self.gaze_contingency_Lx = df["gaze_contingency_L.x"]
        self.gaze_contingency_Ly = df["gaze_contingency_L.y"]

        self.gaze_origin_Rx = df["gaze_origin_R.x(mm)"]
        self.gaze_origin_Ry = df["gaze_origin_R.y(mm)"]
        self.gaze_origin_Rz = df["gaze_origin_R.z(mm)"]


        self.gaze_direct_Rx = df["gaze_direct_R.x"]
        self.gaze_direct_Ry = df["gaze_direct_R.y"]
        self.gaze_direct_Rz = df["gaze_direct_R.z"]

        self.pupil_position_Rx = df["pupil_position_R.x"]
        self.pupil_position_Ry = df["pupil_position_R.y"]

        self.gaze_contingency_Rx = df["gaze_contingency_R.x"]
        self.gaze_contingency_Ry = df["gaze_contingency_R.y"]

        self.head_pos_x = df["head.position.x"]
        self.head_pos_y = df["head.position.y"]
        self.head_pos_z = df["head.position.z"]

        self.x = df["head.rotation.x"]
        self.y = df["head.rotation.y"]
        self.z = df["head.rotation.z"]
        self.w = df["head.rotation.w"]

    def gaze_conversion(self):
        self.gaze_direct_Lx[self.eye_valid_L < 31] = np.nan
        self.gaze_direct_Ly[self.eye_valid_L < 31] = np.nan
        self.gaze_direct_Lz[self.eye_valid_L < 31] = np.nan

        self.gaze_direct_Rx[self.eye_valid_R < 31] = np.nan
        self.gaze_direct_Ry[self.eye_valid_R < 31] = np.nan
        self.gaze_direct_Rz[self.eye_valid_R < 31] = np.nan


        # conversion of GAZE DIRECTION to Vector3 in MM.
        K_L = - self.gaze_origin_Lz / self.gaze_direct_Lz
        K_R = - self.gaze_origin_Rz / self.gaze_direct_Rz

        mm_L_x = self.gaze_direct_Lx * K_L + self.gaze_origin_Lx
        mm_L_y = self.gaze_direct_Ly * K_L + self.gaze_origin_Ly
        mm_R_x = self.gaze_direct_Rx * K_R + self.gaze_origin_Rx
        mm_R_y = self.gaze_direct_Ry * K_R + self.gaze_origin_Ry

        screen_width = 59.5
        screen_height = 66.1
        screen_width_pix = 1400
        screen_height_pix = 1600

        gaze_pix_L_x = screen_width_pix + mm_L_x * (screen_width_pix / screen_width)
        gaze_pix_L_y = screen_height_pix + mm_L_y * (screen_height_pix / screen_height)
        gaze_pix_R_x = screen_width_pix + mm_R_x * (screen_width_pix / screen_width)
        gaze_pix_R_y = screen_height_pix + mm_R_y * (screen_height_pix / screen_height)


        #conversion of GAZE DIRECTION from PIXELS  in DEGREES.
        horizontal_FOV = 106
        vertical_FOV = 110

        gaze_deg_L_x = gaze_pix_L_x * (horizontal_FOV / screen_width_pix )
        gaze_deg_L_y = gaze_pix_L_y * (vertical_FOV / screen_height_pix)
        gaze_deg_R_x = gaze_pix_R_x * (horizontal_FOV / screen_width_pix )
        gaze_deg_R_y = gaze_pix_R_y * (vertical_FOV / screen_height_pix)
        print(gaze_deg_L_x[0], gaze_deg_R_x[0])
        
        return((gaze_pix_L_x, gaze_pix_L_y, gaze_pix_R_x, gaze_pix_R_y),                 # ritorno in due tuple i dati converiti
                (gaze_deg_L_x, gaze_deg_L_y, gaze_deg_R_x, gaze_deg_R_y), self.time)     # nelle variabili pixel_data e deg_data


    def head_pos_conversion(self):
        head_pos_x_cm = self.head_pos_x * 100
        head_pos_y_cm = self.head_pos_y * 100
        head_pos_z_cm = self.head_pos_z * 100

        return(head_pos_x_cm, head_pos_y_cm, head_pos_z_cm)


    def head_rot_conversion(self):
        # CALCULATE ROLL_X
        t0 = +2.0 * (self.w * self.x + self.y * self.z)
        t1 = +1.0 - 2.0 * (self.x * self.x + self.y * self.y)
        roll_x_rad = np.arctan2(t0, t1)  # eulear angle in rad

        # from rad to deg
        pi = 22 / 7
        roll_x = roll_x_rad * (180 / pi)  # eulear angle in deg

        # CALCULATE PITCH_Y
        t2 = +2.0 * (self.w * self.y - self.z * self.x)
        pitch_y_rad = np.arcsin(t2)

        # from rad to deg
        pi = 22 / 7
        pitch_y = pitch_y_rad * (180 / pi)  # eulear angle in deg

        #CALCULATE YAW_Z
        t3 = +2.0 * (self.w * self.z + self.x * self.y)
        t4 = +1.0 - 2.0 * (self.y * self.y + self.z * self.z)
        yaw_z_rad = np.arctan2(t3, t4)  # eulear angle in rad

        # from rad to deg
        pi = 22 / 7
        yaw_z = yaw_z_rad * (180 / pi)  # eulear angle in deg

        return (roll_x, pitch_y, yaw_z)


    def calc_head_eyes_velocity(self):
        # IMPORT EYES DATA PROCESSED
        pixel_data, deg_data, time = self.gaze_conversion()
        gaze_L_x, gaze_L_y, gaze_R_x, gaze_R_y = deg_data

        # IMPORT HEAD DATA PROCESSED
        head_position_converted = self.head_pos_conversion()
        head_rotation_converted =  self.head_rot_conversion()
        head_pos_x, head_pos_y, head_pos_z = head_position_converted
        roll_x, pitch_y, yaw_z = head_rotation_converted


        # CALCULATE HEAD VELOCITY (POSITION AND ROTATION)
        vel_head_pos_x = scipy.signal.savgol_filter(head_pos_x, 17, 4, deriv=1, delta=1 / 120)
        vel_head_pos_y = scipy.signal.savgol_filter(head_pos_y, 17, 4, deriv=1, delta=1 / 120)
        vel_head_pos_z = scipy.signal.savgol_filter(head_pos_z, 17, 4, deriv=1, delta=1 / 120)

        vel_roll_x  = scipy.signal.savgol_filter(roll_x, 17, 4, deriv=1, delta=1 / 120)
        vel_pitch_y = scipy.signal.savgol_filter(pitch_y, 17, 4, deriv=1, delta=1 / 120)
        vel_yaw_z   = scipy.signal.savgol_filter(yaw_z, 17, 4, deriv=1, delta=1 / 120)


        # CALCULATE GAZE VELOCITY (POSITION AND ROTATION) with FILTRATION
        vel_gaze_L_x = scipy.signal.savgol_filter(gaze_L_x, 3, 2, deriv=1, delta=1 / 120)
        vel_gaze_L_y = scipy.signal.savgol_filter(gaze_L_y, 3, 2, deriv=1, delta=1 / 120)

        vel_gaze_R_x = scipy.signal.savgol_filter(gaze_R_x, 3, 2, deriv=1, delta=1 / 120)
        vel_gaze_R_y = scipy.signal.savgol_filter(gaze_R_y, 3, 2, deriv=1, delta=1 / 120)


        # CALCULATE EUCLIDEAN DISTANCE FROM HEAD (POS/ROT) AND GAZE
        head_pos_euclidean_distance = np.add(np.square(vel_head_pos_x), np.square(vel_head_pos_y), np.square(vel_head_pos_z))
        head_rot_euclidean_distance = np.add(np.square(vel_roll_x), np.square(vel_pitch_y), np.square(vel_yaw_z))
        gaze_L_euclidean_distance   = np.add(np.square(vel_gaze_L_x), np.square(vel_gaze_L_y))
        gaze_R_euclidean_distance   = np.add(np.square(vel_gaze_R_x), np.square(vel_gaze_R_y))


        # CALCULATE ABSOLUTE VELOCITY
        vel_abs_head_pos   = np.sqrt(head_pos_euclidean_distance)
        vel_abs_head_rot   = np.sqrt(head_rot_euclidean_distance)
        vel_abs_gaze_L     = np.sqrt(gaze_L_euclidean_distance)
        vel_abs_gaze_R     = np.sqrt(gaze_R_euclidean_distance)

        return(vel_abs_head_pos, vel_abs_head_rot, vel_abs_gaze_L, vel_abs_gaze_R)


    def FromRawtoDeg(self):
        # Sostituisci i valori non validi con NaN
        self.gaze_direct_Lx[self.eye_valid_L < 31] = np.nan
        self.gaze_direct_Ly[self.eye_valid_L < 31] = np.nan
        self.gaze_direct_Lz[self.eye_valid_L < 31] = np.nan

        self.gaze_direct_Rx[self.eye_valid_R < 31] = np.nan
        self.gaze_direct_Ry[self.eye_valid_R < 31] = np.nan
        self.gaze_direct_Rz[self.eye_valid_R < 31] = np.nan


        # Conversione in gradi visivi ( togliere * 180 / np.pi se si vogliono i rad)
        eye_L_x = np.arctan2(self.gaze_direct_Lx, self.gaze_direct_Lz) * 180 / np.pi
        eye_L_y = np.arctan2(self.gaze_direct_Ly, self.gaze_direct_Lz) * 180 / np.pi
        eye_R_x = np.arctan2(self.gaze_direct_Rx, self.gaze_direct_Rz) * 180 / np.pi
        eye_R_y = np.arctan2(self.gaze_direct_Ry, self.gaze_direct_Rz) * 180 / np.pi


        # Conversione in pixels
        tot_pixel_width = 2880
        tot_pixel_height = 1600
        horizontal_FOV = 107
        vertical_FOV = 110

        # per pxel . eye-l-x * tot pixel width / horizontal fov
        pix_L_x = eye_L_x * tot_pixel_width / horizontal_FOV
        pix_L_y = eye_L_y * tot_pixel_height / vertical_FOV
        pix_R_x = eye_R_x * tot_pixel_width / horizontal_FOV
        pix_R_y = eye_R_y * tot_pixel_height / vertical_FOV

        return eye_L_x, eye_L_y, eye_R_x, eye_R_y, self.time


    def plot_results(self):
        # IMPORT DATA
        # Data from xlsx file (put name in parameters)
        # data = DataProcessing(sys.argv[1])

        # EYE Data Processed and Time
        pixel_data, deg_data, time = self.gaze_conversion()
        gaze_L_x, gaze_L_y, gaze_R_x, gaze_R_y = deg_data


        # HEAD Data Processed
        head_pos_x, head_pos_y, head_pos_z = self.head_pos_conversion()
        head_rotation_converted = data.head_rot_conversion()
        roll_x, pitch_y, yaw_z = head_rotation_converted


        # VELOCITY data
        vel_abs_head_pos, vel_abs_head_rot, vel_abs_gaze_L, vel_abs_gaze_R = self.calc_head_eyes_velocity()
        start_time = time[0]  # extract first element from list
        time = time - start_time  # substract initial time from time

        head_pos_x_shift = head_pos_x - head_pos_x[0]  # substract first element from the list to shift posizion to 0
        head_pos_y_shift = head_pos_y - head_pos_y[0]
        head_pos_z_shift = head_pos_z - head_pos_z[0]

        roll_x_shift = roll_x - roll_x[0]  # substract first element from the list to shift posizion to 0
        pitch_y_shift = pitch_y - pitch_y[0]
        yaw_z_shift = yaw_z - yaw_z[0]

        gaze_R_x_shift = gaze_R_x - gaze_R_x[0]
        gaze_R_y_shift = gaze_R_y - gaze_R_y[0]


        # PLOT HEAD POSITION
        fig1, axis = plt.subplots(3)

        axis[0].plot(time, head_pos_x_shift, color="tab:red", label=("Horizontal X"))
        # axis[0].set_title("HORIZONTAL DIRECTION X")
        axis[0].set_xlabel("Time (s)")
        axis[0].set_ylabel("Horizontal Direct (cm)")
        axis[0].legend()

        axis[1].plot(time, head_pos_y_shift, color="tab:green", label=("Vertical Y"))
        # axis[1].set_title("VERTICAL DIRECTION Y")
        axis[1].set_xlabel("Time (s)")
        axis[1].set_ylabel("Vertical Direct (cm)")
        axis[1].legend()

        axis[2].plot(time, head_pos_z_shift, color="tab:blue", label=("Depth Z"))
        # axis[2].set_title("DEEP DIRECTION Z")
        axis[2].set_xlabel("Time (s)")
        axis[2].set_ylabel("Depth Direct (cm)")
        axis[2].legend()


        fig1.suptitle('Head Position', fontsize=16)
        fig1.canvas.manager.set_window_title('Head_Pos')
        plt.show()


        # PLOT HEAD ROTATION
        fig2, axis = plt.subplots(3)

        axis[0].plot(time, roll_x_shift, color="tab:red", label=("Roll_X"))
        # axis[0].set_title("ROLL X")
        axis[0].set_xlabel("Time (s)")
        axis[0].set_ylabel("Roll (°)")
        axis[0].legend()

        axis[1].plot(time, pitch_y_shift, color="tab:green", label=("Pitch_Y"))
        # axis[1].set_title("PITCH Y")
        axis[1].set_xlabel("Time (s)")
        axis[1].set_ylabel("Pitch (°)")
        axis[1].legend()

        axis[2].plot(time, yaw_z_shift, color="tab:blue", label=("Yaw_Z"))
        # axis[2].set_title("YAW Z")
        axis[2].set_xlabel("Time (s)")
        axis[2].set_ylabel("Yaw (°)")
        axis[2].legend()

        fig2.suptitle('Head Rotation ', fontsize=16)
        fig2.canvas.manager.set_window_title('Head_Rot')
        plt.show()


        # PLOT LEFT EYE
        fig3, axis = plt.subplots(2)

        axis[0].plot(time, self.gaze_direct_Lx, color="tab:blue", label=("Left Eye X"))
        axis[0].scatter(time, self.gaze_direct_Lx, color="tab:blue", alpha=0.2)
        # axis[0].set_title("GAZE DIRECTION X")
        axis[0].set_xlabel("Time (s)")
        axis[0].set_ylabel("Direct X (°)")
        axis[0].legend()

        axis[1].plot(time, self.gaze_direct_Ly, color="tab:blue", label=("Left Eye Y"))
        axis[1].scatter(time, self.gaze_direct_Ly, color="tab:blue", alpha=0.2)
        # axis[1].set_title("GAZE DIRECTION Y")
        axis[1].set_xlabel("Time (s)")
        axis[1].set_ylabel("Direct Y (°)")
        axis[1].legend()

        fig3.suptitle(' Left Gaze Direction', fontsize=16)
        fig3.canvas.manager.set_window_title('Left_Gaze')
        plt.show()


        # PLOT RIGHT EYE
        fig4, axis = plt.subplots(2)

        axis[0].plot(time, self.gaze_direct_Rx, color="tab:orange", label=("Right Eye X"))
        axis[0].scatter(time, self.gaze_direct_Rx, color="tab:orange", alpha=0.2)
        # axis[0].set_title("GAZE DIRECTION X")
        axis[0].set_xlabel("Time (s)")
        axis[0].set_ylabel("Direct X (Vector)")
        axis[0].legend()

        axis[1].plot(time, self.gaze_direct_Ry, color="tab:orange", label=("Right Eye Y"))
        axis[1].scatter(time, self.gaze_direct_Ry, color="tab:orange", alpha=0.2)
        # axis[1].set_title("GAZE DIRECTION Y")
        axis[1].set_xlabel("Time (s)")
        axis[1].set_ylabel("Direct X (Vector)")
        axis[1].legend()

        fig4.suptitle('Right Gaze Direction', fontsize=16)
        fig4.canvas.manager.set_window_title('Right_Gaze')
        plt.show()


        # PLOT BOTH EYES OVERVIEW
        fig5, (axis1, axis2) = plt.subplots(1, 2)

        axis1.plot(self.gaze_direct_Lx , self.gaze_direct_Ly, color="tab:blue", label=("Left Eye"), alpha=0.3)
        axis1.scatter(self.gaze_direct_Lx, self.gaze_direct_Ly, color="tab:blue", alpha=0.3)
        axis1.set_xlabel("Normalized Vector")
        axis1.set_ylabel("Normalized Vector")
        axis1.legend()

        axis2.plot( self.gaze_direct_Rx,  self.gaze_direct_Ry, color="tab:orange", label=("Right Eye"), alpha=0.3)
        axis2.scatter( self.gaze_direct_Rx,  self.gaze_direct_Ry, color="tab:orange", alpha=0.3)
        axis2.set_xlabel("Normalized Vector")
        axis2.set_ylabel("Normalized Vector")
        axis2.legend()

        fig5.suptitle('Gazes Direction ', fontsize=16)
        fig5.canvas.manager.set_window_title('Gazes')
        plt.show()


        # PLOT ABSOLUTE VEL
        fig6, axis = plt.subplots(3)

        axis[0].plot(time, vel_abs_head_pos, color="tab:red", label=("Head Pos Velocity"))
        # axis[0].set_title("Absolute Velocity Head Position")
        axis[0].set_xlabel("Time (s)")
        axis[0].set_ylabel("Velocity (cm/s)")
        axis[0].legend()

        axis[1].plot(time, vel_abs_head_rot, color="tab:green", label=("Head Rot Velocity"))
        # axis[1].set_title("Absolute Velocity Head Rotation")
        axis[1].set_xlabel("Time (s)")
        axis[1].set_ylabel("Velocity (°/s)")
        axis[1].legend()

        axis[2].plot(time, vel_abs_gaze_R, color="tab:orange", label=("Gaze Velocity"))
        # axis[2].set_title("Absolute Velocity Gaze Direction")
        axis[2].set_xlabel("Time (s)")
        axis[2].set_ylabel("Velocity (°/s)")
        axis[2].legend()

        fig6.suptitle('Velocity ', fontsize=16)
        fig6.canvas.manager.set_window_title('Head_Gaze_abs_vel')
        plt.show()


        # PLOT COMPARISON
        fig7, (axis1, axis2) = plt.subplots(1, 2)

        gaze_L_x = gaze_L_x - gaze_L_x[0]
        gaze_L_y = gaze_L_y - gaze_L_y[0]
        gaze_R_x = gaze_R_x - gaze_R_x[0]
        gaze_R_y = gaze_R_y - gaze_R_y[0]


        axis1.plot(gaze_L_x, gaze_L_y, color="tab:orange", label=("My Conv"), alpha=0.3)
        axis1.scatter(gaze_L_x, gaze_L_y, color="tab:orange", alpha=0.3)
        axis1.plot(gaze_R_x, gaze_R_y, color="tab:blue", alpha=0.3)
        axis1.scatter(gaze_R_x, gaze_R_y, color="tab:blue", alpha=0.3)
        axis1.set_xlabel("Horizontal Left Eye Position (deg)")
        axis1.set_ylabel("Time (s)")
        axis1.legend()

        eye_L_x, eye_L_y, eye_R_x, eye_R_y, self.time = self.FromRawtoDeg()
        eye_L_x = eye_L_x - eye_L_x[0]
        eye_L_y = eye_L_y - eye_L_y[0]
        eye_R_x = eye_R_x - eye_R_x[0]
        eye_R_y = eye_R_y - eye_R_y[0]

        axis2.plot(eye_R_x, eye_R_y, color="tab:orange", label=("Imaoka Conv"), alpha=0.3)
        axis2.scatter(eye_R_x, eye_R_y, color="tab:orange", alpha=0.3)
        axis2.plot(eye_L_x, eye_L_y, color="tab:blue", alpha=0.3)
        axis2.scatter(eye_L_x, eye_L_y, color="tab:blue", alpha=0.3)
        axis2.set_xlabel("Horizontal Right Eye Position (deg)")
        axis2.set_ylabel("Time (s)")
        axis2.legend()

        fig7.suptitle('Comparison', fontsize=16)
        fig7.canvas.manager.set_window_title('Gazes')
        plt.show()


        # PLOT SRANIPAL DATA
        fig8, axis = plt.subplots(2, 2)

        axis[0,0].plot(-self.gaze_origin_Lx, self.gaze_origin_Ly, color="tab:blue", label=("Left Eye"))
        axis[0,0].scatter(-self.gaze_origin_Lx, self.gaze_origin_Ly, color="tab:blue", alpha=0.3)
        axis[0,0].plot(-self.gaze_origin_Rx, self.gaze_origin_Ry, color="tab:orange", label=("Right Eye"))
        axis[0,0].scatter(-self.gaze_origin_Rx, self.gaze_origin_Ry, color="tab:orange", alpha=0.3)
        axis[0,0].set_title("Gaze Origin")

        axis[0,1].plot(self.gaze_direct_Lx, self.gaze_direct_Ly, color="tab:blue", label=("Left Eye"))
        axis[0,1].scatter(self.gaze_direct_Lx, self.gaze_direct_Ly, color="tab:blue", alpha=0.3)
        axis[0,1].plot(self.gaze_direct_Rx, self.gaze_direct_Ry, color="tab:orange", label=("Right Eye"))
        axis[0,1].scatter(self.gaze_direct_Rx, self.gaze_direct_Ry, color="tab:orange", alpha=0.3)
        axis[0,1].set_title("Gaze Direction")


        axis[1,0].plot(self.pupil_position_Lx, -self.pupil_position_Ly, color="tab:blue", label=("Left Eye"))
        axis[1,0].scatter(self.pupil_position_Lx, -self.pupil_position_Ly, color="tab:blue", alpha=0.3)
        axis[1,0].plot(self.pupil_position_Rx, -self.pupil_position_Ly, color="tab:orange", label=("Right Eye"))
        axis[1,0].scatter(self.pupil_position_Rx, -self.pupil_position_Ly, color="tab:orange", alpha=0.3)
        axis[1,0].set_title("Pupil Position")

        axis[1, 1].plot(self.gaze_contingency_Lx, self.gaze_contingency_Ly, color="tab:blue", label=("Left Eye"))
        axis[1, 1].scatter(self.gaze_contingency_Lx, self.gaze_contingency_Ly, color="tab:blue", alpha=0.3)
        axis[1, 1].plot(self.gaze_contingency_Rx, self.gaze_contingency_Ry, color="tab:orange", label=("Right Eye"))
        axis[1, 1].scatter(self.gaze_contingency_Rx, self.gaze_contingency_Ry, color="tab:orange", alpha=0.3)
        axis[1, 1].set_title("Gaze Contingency (not raw)")

        fig8.suptitle('SRanipal Data', fontsize=16)
        fig8.canvas.manager.set_window_title('SRanipal Data ')
        plt.show()



if __name__ == '__main__':         # varibiliatoe python che controlla s elo script è lanciato o importato da un altro script; se eseguo saccadesconv da un altro script, queste righe non vengono eseguite
    if len(sys.argv) != 2:          # sosituisco la riga12 , mettendo nei paramteri dello script il nome del file xlsx su cui lavorare
        print("Usage " + sys.argv[0] + " <infile>")
    else:
        data = DataProcessing(sys.argv[1])        #creo oggetto di tipo DataProcessing
        # print(data.gaze_conversion())           #collaudo del modulo

        plot = data.plot_results()
