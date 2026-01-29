import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ---------------- CONFIG ----------------
image_folder = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes"
excel_path = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes\Meme_annotations_Binar.xlsx"
progress_file = "review_progress.txt" 
target_column = "Prejudice"
BATCH_SIZE = 8  
# ----------------------------------------

def load_last_index():
    if os.path.exists(progress_file):
        try:
            with open(progress_file, "r") as f:
                content = f.read().strip()
                return int(content) if content else 0
        except: return 0
    return 0

def save_progress(idx):
    with open(progress_file, "w") as f:
        f.write(str(idx))

# Load and Sort Data
df = pd.read_excel(excel_path)
df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

# Filter for rows that HAVE been annotated
rows_to_review = df[df[target_column].notna()].index.tolist()

if not rows_to_review:
    print("No annotated data found to review!")
    exit()

current_index = load_last_index()

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Meme Review Tool - Persistent Progress")
root.state('zoomed')
root.configure(bg="#121212")

header_label = tk.Label(root, text="", fg="#fbbf24", bg="#121212", font=("Arial", 18, "bold"))
header_label.pack(pady=10)

main_frame = tk.Frame(root, bg="#121212")
main_frame.pack(expand=True, fill="both")

image_widgets = []
value_vars = []
photo_refs = []

# Build the grid (2 rows, 4 columns)
for i in range(BATCH_SIZE):
    frame = tk.Frame(main_frame, bg="#1e1e1e", bd=1, relief="solid")
    frame.grid(row=i // 4, column=i % 4, padx=5, pady=5, sticky="nsew")
    
    main_frame.grid_columnconfigure(i % 4, weight=1)
    main_frame.grid_rowconfigure(i // 4, weight=1)

    img_label = tk.Label(frame, bg="#1e1e1e")
    img_label.pack(pady=5)

    # Label showing FileName and the Saved Result
    info_label = tk.Label(frame, fg="#3b82f6", bg="#1e1e1e", font=("Arial", 11, "bold"))
    info_label.pack()

    value_var = tk.IntVar(value=-1)
    value_vars.append(value_var)

    btn_frame = tk.Frame(frame, bg="#1e1e1e")
    btn_frame.pack(pady=5)

    for val in [0, 1]:
        tk.Radiobutton(
            btn_frame, text=str(val), variable=value_var, value=val,
            indicatoron=False, width=8, bg="#333", fg="white",
            selectcolor="#10b981", font=("Arial", 12, "bold")
        ).pack(side="left", padx=10)

    image_widgets.append((img_label, info_label))

# ---------------- LOGIC ----------------

def load_batch():
    global photo_refs
    photo_refs = []
    total = len(rows_to_review)
    
    header_label.config(text=f"Reviewing Memes: {current_index + 1} to {min(current_index + BATCH_SIZE, total)} (Total: {total})")

    for i in range(BATCH_SIZE):
        idx_pos = current_index + i
        
        if idx_pos >= total:
            image_widgets[i][0].config(image="")
            image_widgets[i][1].config(text="")
            value_vars[i].set(-1)
            continue

        df_idx = rows_to_review[idx_pos]
        img_name = df.at[df_idx, "Image_Name"]
        saved_val = df.at[df_idx, target_column]
        img_path = os.path.join(image_folder, img_name)

        # Set UI state from Excel data
        value_vars[i].set(int(saved_val))
        image_widgets[i][1].config(text=f"{img_name} | SAVED: {int(saved_val)}", fg="#60a5fa")

        if os.path.exists(img_path):
            img = Image.open(img_path)
            # SIZE UPDATED HERE
            img.thumbnail((420, 300)) 
            tk_img = ImageTk.PhotoImage(img)
            image_widgets[i][0].config(image=tk_img)
            image_widgets[i][0].image = tk_img 
            photo_refs.append(tk_img)
        else:
            image_widgets[i][1].config(text=f"{img_name} (NOT FOUND)", fg="#ef4444")

def save_data():
    """Saves current batch state to Excel and progress file"""
    for i in range(BATCH_SIZE):
        idx_pos = current_index + i
        if idx_pos < len(rows_to_review):
            df_idx = rows_to_review[idx_pos]
            df.at[df_idx, target_column] = int(value_vars[i].get())
    
    df.to_excel(excel_path, index=False)
    save_progress(current_index)

def go_next(event=None):
    global current_index
    save_data()
    if current_index + BATCH_SIZE < len(rows_to_review):
        current_index += BATCH_SIZE
        load_batch()
    else:
        messagebox.showinfo("Done", "Review completed!")

def go_back(event=None):
    global current_index
    save_data()
    if current_index - BATCH_SIZE >= 0:
        current_index -= BATCH_SIZE
        load_batch()
    else:
        messagebox.showwarning("Start", "You're at the beginning!")

# ---------------- CONTROLS ----------------
root.bind("<Right>", go_next)
root.bind("<Left>", go_back)
root.bind("<Return>", go_next)

def quick_toggle(i):
    if i < BATCH_SIZE:
        current = value_vars[i].get()
        value_vars[i].set(1 if current == 0 else 0)

for i in range(8):
    root.bind(str(i+1), lambda e, i=i: quick_toggle(i))

footer = tk.Frame(root, bg="#121212")
footer.pack(pady=10)

tk.Button(footer, text="◀ BACK (Left Arrow)", command=go_back, width=20, bg="#444", fg="white", font=("Arial", 12)).pack(side="left", padx=10)
tk.Button(footer, text="SAVE & NEXT (Right Arrow) ▶", command=go_next, width=30, bg="#10b981", fg="white", font=("Arial", 12, "bold")).pack(side="left", padx=10)

load_batch()
root.mainloop()