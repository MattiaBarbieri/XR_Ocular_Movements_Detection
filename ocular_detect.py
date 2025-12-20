import math
import sys
import statistics
import numpy as np


def parse_remodnav_file(filepath):
    with open(filepath) as f:
        lines = f.readlines()
    hdr = lines[0].split('\t')
    return lines[1:], hdr

def extract_indices(hdr):
    return {
        'event': hdr.index('label'),
        'x1': hdr.index('start_x'),
        'y1': hdr.index('start_y'),
        'x2': hdr.index('end_x'),
        'y2': hdr.index('end_y'),
        'duration': hdr.index('duration'),
        'peak_vel': hdr.index('peak_vel'),
        'med_vel': hdr.index('med_vel'),
        'amp': hdr.index('amp'),
        'avg_vel': hdr.index('avg_vel\n')
    }

def compute_prl(fixa_coords):
    coords = np.array(fixa_coords)
    x_mean = coords[:, 0].mean()
    y_mean = coords[:, 1].mean()
    x_std = coords[:, 0].std()
    y_std = coords[:, 1].std()
    return x_mean, y_mean, x_std, y_std

def process_events(lines, indices):
    Kpix_deg = 0.068075 #from data processing, deg conversion, horizontal_FOV / screen_height_pix
    sacc_ampl_min_threshold = 2 / Kpix_deg #2°
    fixa_dur_min_threshold = 0.1  #100ms
    purs_vel_min_threshold = 5 #5°/s


    sacc_count = 0; sacc_ampl = []; sacc_ampl_deg = []; sacc_duration = []; sacc_peakvel = []; sacc_medvel = []; sacc_avgvel = []; sacc_rawamp = []
    micro_sacc_count = 0; micro_sacc_ampl = []; micro_sacc_duration = []; micro_sacc_peakvel = []; micro_sacc_medvel = []; micro_sacc_avgvel = []
    pso_count = 0; pso_ampl = []; pso_ampl_deg = []; pso_duration = []; pso_peakvel = []; pso_medvel = []; pso_avgvel = []; pso_rawamp = []
    purs_count = 0; purs_ampl = []; purs_ampl_deg = []; purs_duration = []; purs_peakvel = []; purs_medvel= []; purs_avgvel = []; purs_rawamp = []
    fixa_count = 0; fixa_ampl = []; fixa_ampl_deg = []; fixa_duration = []; fixa_peakvel = []; fixa_medvel = []; fixa_avgvel = []; fixa_rawamp = []
    fixa_coords = []


    for l in lines:
        data = l.split('\t')
        event_type = data[indices['event']]

        if event_type in ['SACC', 'ISAC']:
            dx = float(data[indices['x1']]) - float(data[indices['x2']])
            dy = float(data[indices['y2']]) - float(data[indices['y2']])
            temp = abs(math.hypot(dx, dy))
            temp2 = temp * Kpix_deg

            if temp >= sacc_ampl_min_threshold:
                sacc_count += 1
                sacc_ampl.append(temp)
                sacc_ampl_deg.append(temp2)
                sacc_duration.append(float(data[indices['duration']]))
                sacc_peakvel.append(float(data[indices['peak_vel']]))
                sacc_medvel.append(float(data[indices['med_vel']]))
                sacc_avgvel.append(float(data[indices['avg_vel']]))
                sacc_rawamp.append(float(data[indices['amp']]))
            #else:
                #micro_sacc_count += 1
                #micro_sacc_ampl.append(temp)
                #micro_sacc_duration.append(float(data[indices['duration']]))
                #micro_sacc_peakvel.append(float(data[indices['peak_vel']]))
                #micro_sacc_medvel.append(float(data[indices['med_vel']]))
                #micro_sacc_avgvel.append(float(data[indices['avg_vel']]))

        elif event_type in ['PURS']:
            dx = float(data[indices['x1']]) - float(data[indices['x2']])
            dy = float(data[indices['y2']]) - float(data[indices['y2']])
            temp = abs(math.hypot(dx,dy))
            temp2 = temp * Kpix_deg
            temp3 = float(data[indices['avg_vel']])

            if temp3 >= purs_vel_min_threshold:

                purs_count += 1
                purs_ampl.append(temp)
                purs_ampl_deg.append(temp2)
                purs_duration.append(float(data[indices['duration']]))
                purs_peakvel.append(float(data[indices['peak_vel']]))
                purs_medvel.append(float(data[indices['med_vel']]))
                purs_avgvel.append(float(data[indices['avg_vel']]))
                purs_rawamp.append(float(data[indices['amp']]))

        elif event_type in ['HPSO', 'LPSO']:
            dx = float(data[indices['x1']]) - float(data[indices['x2']])
            dy = float(data[indices['y2']]) - float(data[indices['y2']])
            temp = abs(math.hypot(dx, dy))
            temp2 = temp * Kpix_deg

            pso_count += 1
            pso_ampl.append(temp)
            pso_ampl_deg.append(temp2)
            pso_duration.append(float(data[indices['duration']]))
            pso_peakvel.append(float(data[indices['peak_vel']]))
            pso_medvel.append(float(data[indices['med_vel']]))
            pso_avgvel.append(float(data[indices['avg_vel']]))
            pso_rawamp.append(float(data[indices['amp']]))

        elif event_type in ['FIXA']:
            dx = float(data[indices['x1']]) - float(data[indices['x2']])
            dy = float(data[indices['y2']]) - float(data[indices['y2']])
            temp = abs(math.hypot(dx,dy))
            temp2 = temp * Kpix_deg
            temp3 = float(data[indices['duration']])

            if  temp3 >= fixa_dur_min_threshold:
                fixa_count += 1
                fixa_ampl.append(temp)
                fixa_ampl_deg.append(temp2)
                fixa_duration.append(float(data[indices['duration']]))
                fixa_peakvel.append(float(data[indices['peak_vel']]))
                fixa_medvel.append(float(data[indices['med_vel']]))
                fixa_avgvel.append(float(data[indices['avg_vel']]))
                fixa_rawamp.append(float(data[indices['amp']]))

                cx = (float(data[indices['x1']]) + float(data[indices['x2']])) / 2 #coordinata orrizontale del centro di fissazione. Per PRL ((starx + endx)/2). Solo su Fix valide (vedi soglia).
                cy = (float(data[indices['y1']]) + float(data[indices['y2']])) / 2 #coordinata verticale del centro di fissazione. Per PRL ((stary + endy)/2). Solo su Fix valide (vedi soglia).
                fixa_coords.append((cx, cy))

    return {
        'sacc_count': sacc_count,
        'sacc_ampl': sacc_ampl,
        'sacc_ampl_deg': sacc_ampl_deg,
        'sacc_duration': sacc_duration,
        'sacc_peakvel': sacc_peakvel,
        'sacc_medvel': sacc_medvel,
        'sacc_avgvel': sacc_avgvel,
        'sacc_rawamp': sacc_rawamp,

        'purs_count': purs_count,
        'purs_ampl': purs_ampl,
        'purs_ampl_deg': purs_ampl_deg,
        'purs_duration': purs_duration,
        'purs_peakvel': purs_peakvel,
        'purs_medvel': purs_medvel,
        'purs_avgvel': purs_avgvel,
        'purs_rawamp': purs_rawamp,

        'pso_count': pso_count,
        'pso_ampl': pso_ampl,
        'pso_ampl_deg': pso_ampl_deg,
        'pso_duration': pso_duration,
        'pso_peakvel': pso_peakvel,
        'pso_medvel': pso_medvel,
        'pso_avgvel': pso_avgvel,
        'pso_rawamp': pso_rawamp,

        'fixa_count': fixa_count,
        'fixa_duration': fixa_duration,
        'fixa_coords': fixa_coords
    }

def compute_and_print_stats(data):
    # --- SACCADES ---
    macro_sacc_count = data['sacc_count']

    if macro_sacc_count > 0:
        mean_sacc_ampl = np.mean(data['sacc_ampl'])
        mean_sacc_ampl_deg = np.mean(data['sacc_ampl_deg'])
        mean_sacc_duration = np.mean(data['sacc_duration'])
        mean_sacc_peakvel = np.mean(data['sacc_peakvel'])
        mean_sacc_medvel = np.mean(data['sacc_medvel'])
        mean_sacc_avgvel = np.mean(data['sacc_avgvel'])
        mean_sacc_rawamp = np.mean(data['sacc_rawamp'])

        median_sacc_ampl = np.median(data['sacc_ampl'])
        median_sacc_ampl_deg = np.median(data['sacc_ampl_deg'])
        median_sacc_duration = np.median(data['sacc_duration'])
        median_sacc_peakvel = np.median(data['sacc_peakvel'])
        median_sacc_medvel = np.median(data['sacc_medvel'])
        median_sacc_avgvel = np.median(data['sacc_avgvel'])
        median_sacc_rawampl = np.median(data['sacc_rawamp'])

        sd_sacc_ampl = statistics.stdev(data['sacc_ampl']) if len(data['sacc_ampl']) > 1 else 0.0
        sd_sacc_ampl_deg = statistics.stdev(data['sacc_ampl_deg']) if len(data['sacc_ampl_deg']) > 1 else 0.0
        sd_sacc_duration = statistics.stdev(data['sacc_duration']) if len(data['sacc_duration']) > 1 else 0.0
        sd_sacc_peakvel = statistics.stdev(data['sacc_peakvel']) if len(data['sacc_peakvel']) > 1 else 0.0
        sd_sacc_medvel = statistics.stdev(data['sacc_medvel']) if len(data['sacc_medvel']) > 1 else 0.0
        sd_sacc_avgvel = statistics.stdev(data['sacc_avgvel']) if len(data['sacc_avgvel']) > 1 else 0.0
        sd_sacc_rawamp = statistics.stdev(data['sacc_rawamp']) if len(data['sacc_rawamp']) > 1 else 0.0

    else:
        print("No Saccades Detected.")
        mean_sacc_ampl = median_sacc_ampl = sd_sacc_ampl = float('nan')
        mean_sacc_ampl_deg = median_sacc_ampl_deg = sd_sacc_ampl_deg = float('nan')
        mean_sacc_duration = median_sacc_duration = sd_sacc_duration = float('nan')
        mean_sacc_peakvel = median_sacc_peakvel = sd_sacc_peakvel = float('nan')
        mean_sacc_medvel = median_sacc_medvel = sd_sacc_medvel = float('nan')
        mean_sacc_avgvel = median_sacc_avgvel = sd_sacc_avgvel = float('nan')
        mean_sacc_rawamp = median_sacc_rawampl = sd_sacc_rawamp = float('nan')

    # --- SMOOTH PURSUITS ---
    purs_count = data['purs_count']

    if purs_count > 0:
        mean_purs_ampl = np.mean(data['purs_ampl'])
        mean_purs_ampl_deg = np.mean(data['purs_ampl_deg'])
        mean_purs_duration = np.mean(data['purs_duration'])
        mean_purs_peakvel = np.mean(data['purs_peakvel'])
        mean_purs_medvel = np.mean(data['purs_medvel'])
        mean_purs_avgvel = np.mean(data['purs_avgvel'])
        mean_purs_rawamp = np.mean(data['purs_rawamp'])

        median_purs_ampl = np.median(data['purs_ampl'])
        median_purs_ampl_deg = np.median(data['purs_ampl_deg'])
        median_purs_duration = np.median(data['purs_duration'])
        median_purs_peakvel = np.median(data['purs_peakvel'])
        median_purs_medvel = np.median(data['purs_medvel'])
        median_purs_avgvel = np.median(data['purs_avgvel'])
        median_purs_rawamp = np.median(data['purs_rawamp'])

        sd_purs_ampl = statistics.stdev(data['purs_ampl']) if len(data['purs_ampl']) > 1 else 0.0
        sd_purs_ampl_deg = statistics.stdev(data['purs_ampl_deg']) if len(data['purs_ampl_deg']) > 1 else 0.0
        sd_purs_duration = statistics.stdev(data['purs_duration']) if len(data['purs_duration']) > 1 else 0.0
        sd_purs_peakvel = statistics.stdev(data['purs_peakvel']) if len(data['purs_peakvel']) > 1 else 0.0
        sd_purs_medvel = statistics.stdev(data['purs_medvel']) if len(data['purs_medvel']) > 1 else 0.0
        sd_purs_avgvel = statistics.stdev(data['purs_avgvel']) if len(data['purs_avgvel']) > 1 else 0.0
        sd_purs_rawamp = statistics.stdev(data['purs_rawamp']) if len(data['purs_rawamp']) > 1 else 0.0
    else:
        print("No Smooth Pursuit Detected.")
        mean_purs_ampl = median_purs_ampl = sd_purs_ampl = float('nan')
        mean_purs_ampl_deg = median_purs_ampl_deg = sd_purs_ampl_deg = float('nan')
        mean_purs_duration = median_purs_duration = sd_purs_duration = float('nan')
        mean_purs_peakvel = median_purs_peakvel = sd_purs_peakvel = float('nan')
        mean_purs_medvel = median_purs_medvel = sd_purs_medvel = float('nan')
        mean_purs_avgvel = median_purs_avgvel = sd_purs_avgvel = float('nan')
        mean_purs_rawamp = median_purs_rawamp = sd_purs_rawamp = float('nan')


    # --- PSO (Pursuit Onsets) ---
    pso_count = data['pso_count']

    if pso_count > 0:
        mean_pso_ampl = np.mean(data['pso_ampl'])
        mean_pso_ampl_deg = np.mean(data['pso_ampl_deg'])
        mean_pso_duration = np.mean(data['pso_duration'])
        mean_pso_peakvel = np.mean(data['pso_peakvel'])
        mean_pso_medvel = np.mean(data['pso_medvel'])
        mean_pso_avgvel = np.mean(data['pso_avgvel'])
        mean_pso_rawamp = np.mean(data['pso_rawamp'])

        median_pso_ampl = np.median(data['pso_ampl'])
        median_pso_ampl_deg = np.median(data['pso_ampl_deg'])
        median_pso_duration = np.median(data['pso_duration'])
        median_pso_peakvel = np.median(data['pso_peakvel'])
        median_pso_medvel = np.median(data['pso_medvel'])
        median_pso_avgvel = np.median(data['pso_avgvel'])
        median_pso_rawamp = np.median(data['pso_rawamp'])

        sd_pso_ampl = statistics.stdev(data['pso_ampl']) if len(data['pso_ampl']) > 1 else 0.0
        sd_pso_ampl_deg = statistics.stdev(data['pso_ampl_deg']) if len(data['pso_ampl_deg']) > 1 else 0.0
        sd_pso_duration = statistics.stdev(data['pso_duration']) if len(data['pso_duration']) > 1 else 0.0
        sd_pso_peakvel = statistics.stdev(data['pso_peakvel']) if len(data['pso_peakvel']) > 1 else 0.0
        sd_pso_medvel = statistics.stdev(data['pso_medvel']) if len(data['pso_medvel']) > 1 else 0.0
        sd_pso_avgvel = statistics.stdev(data['pso_avgvel']) if len(data['pso_avgvel']) > 1 else 0.0
        sd_pso_rawamp = statistics.stdev(data['pso_rawamp']) if len(data['pso_rawamp']) > 1 else 0.0
    else:
        print("No PSO Detected.")
        mean_pso_ampl = median_pso_ampl = sd_pso_ampl = float('nan')
        mean_pso_ampl_deg = median_pso_ampl_deg = sd_pso_ampl_deg = float('nan')
        mean_pso_duration = median_pso_duration = sd_pso_duration = float('nan')
        mean_pso_peakvel = median_pso_peakvel = sd_pso_peakvel = float('nan')
        mean_pso_medvel = median_pso_medvel = sd_pso_medvel = float('nan')
        mean_pso_avgvel = median_pso_avgvel = sd_pso_avgvel = float('nan')
        mean_pso_rawamp = median_pso_rawamp = sd_pso_rawamp = float('nan')


    # --- FIXATIONS ---
    fixa_count = data['fixa_count']

    if fixa_count > 0:
        mean_fixa_duration = np.mean(data['fixa_duration'])
        median_fixa_duration = np.median(data['fixa_duration'])
        sd_fixa_duration = statistics.stdev(data['fixa_duration']) if len(data['fixa_duration']) > 1 else 0.0
    else:
        print("No Fixation Detected.")
        mean_fixa_duration = median_fixa_duration = sd_fixa_duration = float('nan')


    # PRINT RESULTS ON CONSOLE
    print("Found: {:d} Macrosaccades (ampl: {:f} pixels (median: {:f}),(sd: {:f}) / {:f} degrees: (median: {:f}), (sd:{:f}), rawamp: {:f} (median: {:f}, (sd:{:f}); duration: {:f} (median: {:f}), (sd: {:f}); peak_vel: {:f} (median: {:f}), (sd: {:f}); med_vel: {:f} (median: {:f}), (sd: {:f}); med_vel: {:f} (median: {:f}), (sd: {:f}))".format(
        macro_sacc_count,
        mean_sacc_ampl, median_sacc_ampl, sd_sacc_ampl,
        mean_sacc_ampl_deg, median_sacc_ampl_deg, sd_sacc_ampl_deg,
        mean_sacc_rawamp, median_sacc_rawampl, sd_sacc_rawamp,
        mean_sacc_duration, median_sacc_duration, sd_sacc_duration,
        mean_sacc_peakvel, median_sacc_peakvel, sd_sacc_peakvel,
        mean_sacc_medvel, median_sacc_medvel, sd_sacc_medvel,
        mean_sacc_avgvel, median_sacc_avgvel, sd_sacc_avgvel
    ))

    print("Found: {:d} Smooth Pursuits (ampl: {:.3f} pixels (median: {:.3f}), (sd: {:.3f}) / {:.3f} degrees (median: {:.3f}), (sd: {:.3f}), rawamp: {:.3f} (median: {:.3f}), (sd: {:.3f}); duration: {:.3f} (median: {:.3f}), (sd: {:.3f}); peak_vel: {:.3f} (median: {:.3f}), (sd: {:.3f}); med_vel: {:.3f} (median: {:.3f}), (sd: {:.3f}); avg_vel: {:.3f} (median: {:.3f}), (sd: {:.3f}))".format(
        purs_count,
        mean_purs_ampl, median_purs_ampl, sd_purs_ampl,
        mean_purs_ampl_deg, median_purs_ampl_deg, sd_purs_ampl_deg,
        mean_purs_rawamp, median_purs_rawamp, sd_purs_rawamp,
        mean_purs_duration, median_purs_duration, sd_purs_duration,
        mean_purs_peakvel, median_purs_peakvel, sd_purs_peakvel,
        mean_purs_medvel, median_purs_medvel, sd_purs_medvel,
        mean_purs_avgvel, median_purs_avgvel, sd_purs_avgvel
    ))

    print("Found: {:d} PSO (ampl: {:.3f} pixels (median: {:.3f}), (sd: {:.3f}) / {:.3f} degrees (median: {:.3f}), (sd: {:.3f}), rawamp: {:.3f} (median: {:.3f}), (sd: {:.3f}); duration: {:.3f} (median: {:.3f}), (sd: {:.3f}); peak_vel: {:.3f} (median: {:.3f}), (sd: {:.3f}); med_vel: {:.3f} (median: {:.3f}), (sd: {:.3f}); avg_vel: {:.3f} (median: {:.3f}), (sd: {:.3f}))".format(
        pso_count,
        mean_pso_ampl, median_pso_ampl, sd_pso_ampl,
        mean_pso_ampl_deg, median_pso_ampl_deg, sd_pso_ampl_deg,
        mean_pso_rawamp, median_pso_rawamp, sd_pso_rawamp,
        mean_pso_duration, median_pso_duration, sd_pso_duration,
        mean_pso_peakvel, median_pso_peakvel, sd_pso_peakvel,
        mean_pso_medvel, median_pso_medvel, sd_pso_medvel,
        mean_pso_avgvel, median_pso_avgvel, sd_pso_avgvel
    ))

    print("Found: {:d} Fixations (duration: {:f} (median: {:f}), (sd: {:f}))".format(
        fixa_count,
        mean_fixa_duration, median_fixa_duration, sd_fixa_duration
    ))

    if data['fixa_coords']:
        prl_x, prl_y, prl_x_std, prl_y_std = compute_prl(data['fixa_coords'])
        print("PRL (Preferred Retinal Locus):")
        print(f"  PRLx: {prl_x:.2f}  (sd: {prl_x_std:.2f})")
        print(f"  PRLy: {prl_y:.2f}  (sd: {prl_y_std:.2f})")


    # Scrittura su file
    with open("Data.tsv", "a") as f:
        if f.tell() == 0:
            f.write("NAME\tTASK\tCONDITION\t"
                    "Sacc_N\t"
                    "Sacc_amp_pix_mean\tSacc_amp_pix_med\tSacc_amp_pix_sd\t"
                    "Sacc_amp_deg_mean\tSacc_amp_deg_med\tSacc_amp_deg_sd\t"
                    "Sacc_raw_amp_mean\tSacc_raw_amp_med\tSacc_raw_amp_sd\t"
                    "Sacc_dur_mean\tSacc_dur_med\tSacc_dur_sd\t"
                    "Sacc_peakvel_mean\tSacc_peakvel_med\tSacc_peakvel_sd\t"
                    "Sacc_medvel_mean\tSacc_medvel_med\tSacc_medvel_sd\t"
                    "Sacc_avgvel_mean\tSacc_avgvel_med\tSacc_avgvel_sd\t"
                    
                    "SmoothPurs_N\t"
                    "SmoothPurs_amp_pix_mean\tSmoothPurs_amp_pix_med\tSmoothPurs_amp_pix_sd\t"
                    "SmoothPurs_amp_deg_mean\tSmoothPurs_amp_deg_med\tSmoothPurs_amp_deg_sd\t"
                    "SmoothPurs_raw_amp_mean\tSmoothPurs_raw_amp_med\tSmoothPurs_raw_amp_sd\t"
                    "SmoothPurs_dur_mean\tSmoothPurs_dur_med\tSmoothPurs_dur_sd\t"
                    "SmoothPurs_peakvel_mean\tSmoothPurs_peakvel_med\tSmoothPurs_peakvel_sd\t"
                    "SmoothPurs_medvel_mean\tSmoothPurs_medvel_med\tSmoothPurs_medvel_sd\t"
                    "SmoothPurs_avgvel_mean\tSmoothPurs_avgvel_med\tSmoothPurs_avgvel_sd\t"
                    
                    "PSO_N\t"
                    "PSO_amp_pix_mean\tPSO_amp_pix_med\tPSO_amp_pix_sd\t"
                    "PSO_amp_deg_mean\tPSO_amp_deg_med\tPSO_amp_deg_sd\t"
                    "PSO_raw_amp_mean\tPSO_raw_amp_med\tPSO_raw_amp_sd\t"
                    "PSO_dur_mean\tPSO_dur_med\tPSO_dur_sd\t"
                    "PSO_peakvel_mean\tPSO_peakvel_med\tPSO_peakvel_sd\t"
                    "PSO_medvel_mean\tPSO_medvel_med\tPSO_medvel_sd\t"
                    "PSO_avgvel_mean\tPSO_avgvel_med\tPSO_avgvel_sd\t"

                    "Fixa_N\t"
                    "Fixa_dur_mean\tFixa_dur_med\tFixa_dur_sd\t"
                    "PRLx\tPRLx_sd\tPRLy\tPRLy_sd\n")

        if data['fixa_coords']:
            prl_x, prl_y, prl_x_std, prl_y_std = compute_prl(data['fixa_coords'])
        else:
            prl_x = prl_y = prl_x_std = prl_y_std = float('nan')


        f.write("USER\tXX\tXX\t"
                f"{macro_sacc_count:.3f}\t"
                f"{mean_sacc_ampl:.3f}\t{median_sacc_ampl:.3f}\t{sd_sacc_ampl:.3f}\t"
                f"{mean_sacc_ampl_deg:.3f}\t{median_sacc_ampl_deg:.3f}\t{sd_sacc_ampl_deg:.3f}\t"
                f"{mean_sacc_rawamp:.3f}\t{median_sacc_rawampl:.3f}\t{sd_sacc_rawamp:.3f}\t"
                f"{mean_sacc_duration:.3f}\t{median_sacc_duration:.3f}\t{sd_sacc_duration:.3f}\t"
                f"{mean_sacc_peakvel:.3f}\t{median_sacc_peakvel:.3f}\t{sd_sacc_peakvel:.3f}\t"
                f"{mean_sacc_medvel:.3f}\t{median_sacc_medvel:.3f}\t{sd_sacc_medvel:.3f}\t"
                f"{mean_sacc_avgvel:.3f}\t{median_sacc_avgvel:.3f}\t{sd_sacc_avgvel:.3f}\t"
                
                
                f"{purs_count:.3f}\t"
                f"{mean_purs_ampl:.3f}\t{median_purs_ampl:.3f}\t{sd_purs_ampl:.3f}\t"
                f"{mean_purs_ampl_deg:.3f}\t{median_purs_ampl_deg:.3f}\t{sd_purs_ampl_deg:.3f}\t"
                f"{mean_purs_rawamp:.3f}\t{median_purs_rawamp:.3f}\t{sd_purs_rawamp:.3f}\t"
                f"{mean_purs_duration:.3f}\t{median_purs_duration:.3f}\t{sd_purs_duration:.3f}\t"
                f"{mean_purs_peakvel:.3f}\t{median_purs_peakvel:.3f}\t{sd_purs_peakvel:.3f}\t"
                f"{mean_purs_medvel:.3f}\t{median_purs_medvel:.3f}\t{sd_purs_medvel:.3f}\t"
                f"{mean_purs_avgvel:.3f}\t{median_purs_avgvel:.3f}\t{sd_purs_avgvel:.3f}\t"
                
                f"{pso_count:.3f}\t"
                f"{mean_pso_ampl:.3f}\t{median_pso_ampl:.3f}\t{sd_pso_ampl:.3f}\t"
                f"{mean_pso_ampl_deg:.3f}\t{median_pso_ampl_deg:.3f}\t{sd_pso_ampl_deg:.3f}\t"
                f"{mean_pso_rawamp:.3f}\t{median_pso_rawamp:.3f}\t{sd_pso_rawamp:.3f}\t"
                f"{mean_pso_duration:.3f}\t{median_pso_duration:.3f}\t{sd_pso_duration:.3f}\t"
                f"{mean_pso_peakvel:.3f}\t{median_pso_peakvel:.3f}\t{sd_pso_peakvel:.3f}\t"
                f"{mean_pso_medvel:.3f}\t{median_pso_medvel:.3f}\t{sd_pso_medvel:.3f}\t"
                f"{mean_pso_avgvel:.3f}\t{median_pso_avgvel:.3f}\t{sd_pso_avgvel:.3f}\t"

                f"{fixa_count:.3f}\t"
                f"{mean_fixa_duration:.3f}\t{median_fixa_duration:.3f}\t{sd_fixa_duration:.3f}\t"
                f"{prl_x:.3f}\t{prl_x_std:.3f}\t{prl_y:.3f}\t{prl_y_std:.3f}\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <remodnav_out_file>")
        exit(1)

    lines, hdr = parse_remodnav_file(sys.argv[1])
    indices = extract_indices(hdr)
    data = process_events(lines, indices)
    compute_and_print_stats(data)

if __name__ == "__main__":
    main()

