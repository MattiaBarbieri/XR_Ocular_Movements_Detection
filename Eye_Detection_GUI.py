import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
import subprocess
from data_processing import DataProcessing
from launch_remodnav import calc_sample_rate, calc_min_savgol, write_remodnav_file
from ocular_detect import parse_remodnav_file, extract_indices, process_events, compute_and_print_stats


def show_file_selector_and_run_remodnav():
    def conferma():
        if filepath.get():
            nonlocal raw_file_path
            raw_file_path = filepath.get()
            root.quit()

    raw_file_path = None

    root = tk.Tk()
    root.title("Selezione File Dati")
    root.attributes('-fullscreen', True)
    root.configure(bg="#1A1A2E")

    try:
        logo_path = "TR_logo2.png"
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((500, 420), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
    except:
        logo_photo = None

    frame = tk.Frame(root, bg="#1A1A2E")
    frame.pack(expand=True)

    if logo_photo:
        logo_label = tk.Label(frame, image=logo_photo, bg="#1A1A2E")
        logo_label.image = logo_photo
        logo_label.pack(pady=(0, 40))

    label = tk.Label(frame, text="Update Raw Data File", font=("Segoe UI", 20), bg="#1A1A2E", fg="white")
    label.pack(pady=(0, 10))

    filepath = tk.StringVar()
    data_dir = os.path.join(os.getcwd(), "Data")

    file_button = tk.Button(frame, text="Sfoglia", font=("Segoe UI", 14),
                            bg="white", fg="#1A1A2E",
                            command=lambda: filepath.set(filedialog.askopenfilename(initialdir=data_dir)),
                            relief="raised", bd=2, padx=20, pady=10)
    file_button.pack(pady=10)

    file_label = tk.Label(frame, textvariable=filepath, font=("Segoe UI", 12), bg="#1A1A2E", fg="white", wraplength=1000)
    file_label.pack(pady=(0, 20))

    button = tk.Button(frame, text="Confirm", font=("Segoe UI", 16, "bold"),
                       bg="white", fg="#1A1A2E", activebackground="#333", activeforeground="white",
                       command=conferma, relief="raised", bd=2, padx=20, pady=10)
    button.pack(pady=20)

    root.bind("<Escape>", lambda e: root.quit())
    root.mainloop()
    root.destroy()

    if raw_file_path:
        conv = DataProcessing(raw_file_path)
        data = conv.gaze_conversion()
        head_pos = conv.head_pos_conversion()
        head_rot = conv.head_rot_conversion()
        outfile_prefix = "outfile_"
        write_remodnav_file((data[0], data[1], data[2], head_pos, head_rot), outfile_prefix)
        sample_rate = calc_sample_rate(data[2])
        savgol = calc_min_savgol(sample_rate)
        Kpix_deg = 0.068055

        cmd_left = f"remodnav --savgol-length {savgol:.6f} {outfile_prefix}l outfile_l {Kpix_deg:.6f} {sample_rate:.6f}"
        cmd_right = f"remodnav --savgol-length {savgol:.6f} {outfile_prefix}r outfile_r {Kpix_deg:.6f} {sample_rate:.6f}"

        print("Running RemoDNaV for left eye:")
        subprocess.run(cmd_left, shell=True)

        print("Running RemoDNaV for right eye:")
        subprocess.run(cmd_right, shell=True)



def show_analysis_selector():
    def run_analysis():
        selected_file = file_choice.get()
        if selected_file:
            lines, hdr = parse_remodnav_file(selected_file)
            indices = extract_indices(hdr)
            data = process_events(lines, indices)
            compute_and_print_stats(data)
            show_results_page()

    root = tk.Tk()
    root.title("Analisi Dati")
    root.attributes('-fullscreen', True)
    root.configure(bg="#1A1A2E")

    try:
        logo_img = Image.open("TR_logo2.png").resize((500, 420), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
    except:
        logo_photo = None

    frame = tk.Frame(root, bg="#1A1A2E")
    frame.pack(expand=True)

    if logo_photo:
        logo_label = tk.Label(frame, image=logo_photo, bg="#1A1A2E")
        logo_label.image = logo_photo
        logo_label.pack(pady=(0, 40))

    label = tk.Label(frame, text="Choose which eye process", font=("Segoe UI", 20), bg="#1A1A2E", fg="white")
    label.pack(pady=(0, 10))

    file_choice = tk.StringVar()
    file_options = [f for f in os.listdir() if f.startswith("outfile_") and not f.endswith(".png")]

    for f in file_options:
        tk.Radiobutton(frame, text=f, variable=file_choice, value=f,
                       font=("Segoe UI", 14), bg="#1A1A2E", fg="white", selectcolor="#0F3460").pack(anchor="w", padx=20)

    tk.Button(frame, text="Analyze", font=("Segoe UI", 16, "bold"),
              bg="white", fg="#1A1A2E", command=run_analysis,
              relief="raised", bd=2, padx=20, pady=10).pack(pady=30)

    root.bind("<Escape>", lambda e: root.quit())
    root.mainloop()
    root.destroy()

def show_results_page():
    root = tk.Tk()
    root.title("Results")
    root.attributes('-fullscreen', True)
    root.configure(bg="#1A1A2E")

    frame = tk.Frame(root, bg="#1A1A2E")
    frame.pack(expand=True)

    label = tk.Label(frame, text="Eye Movements Detection Results", font=("Segoe UI", 24, "bold"), bg="#1A1A2E", fg="white")
    label.pack(pady=20)

    try:
        with open("Data.tsv", "r") as f:
            lines = f.readlines()
            results = lines[-1] if len(lines) > 1 else "No Results Available."
    except FileNotFoundError:
        results = "File 'Data.tsv' not found."

    text_box = tk.Text(frame, wrap="word", font=("Segoe UI", 14), bg="white", fg="#1A1A2E", width=100, height=30)
    text_box.insert("1.0", results)
    text_box.config(state="disabled")
    text_box.pack(pady=20)

    root.bind("<Escape>", lambda e: root.quit())
    root.mainloop()
    root.destroy()



# Lancia direttamente la GUI
show_file_selector_and_run_remodnav()
show_analysis_selector()
