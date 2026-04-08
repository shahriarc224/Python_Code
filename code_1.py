# This code is for Sarcasm_Present class 

import sys
import os
import pandas as pd
import tkinter as tk
from tkinter import messagebox


# ---------- SYSTEM CHECK ----------

try:
    from PIL import Image, ImageTk
except ImportError:
    print("❌ Missing dependencies. Run: sudo apt install python3-pil python3-pil.imagetk")
    sys.exit(1)


# ================= CONFIG =================

IMAGE_FOLDER = "/home/md-shahriar-chowdhury/Sabbir Research/Memes 2-20260328T163131Z-1-001/Memes 2"
EXCEL_PATH = "/home/md-shahriar-chowdhury/Sabbir Research/Memes_2.xlsx"
TARGET_COLUMN = "Sarcasm_Present"

IMAGES_PER_BATCH = 8
ROWS = 2
COLS = 4
STATE_FILE = "review_state.txt"


# ================= DATA SETUP =================

if not os.path.exists(EXCEL_PATH):
    print(f"❌ Excel file not found: {EXCEL_PATH}")
    sys.exit(1)

try:
    df = pd.read_excel(EXCEL_PATH)
    if TARGET_COLUMN not in df.columns:
        df[TARGET_COLUMN] = None
    
    # Auto-fill empty with 0
    df[TARGET_COLUMN] = df[TARGET_COLUMN].fillna(0).astype(int)
    print(f"✅ Excel loaded. {len(df)} rows ready.")
except Exception as e:
    print(f"❌ Error loading Excel: {e}")
    sys.exit(1)

current_index = 0
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, "r") as f:
            current_index = int(f.read().strip())
    except: current_index = 0



# ================= GUI CORE =================

root = tk.Tk()
root.title("Meme Annotator - Search Integrated")
root.configure(bg="#121212")


try:
    root.attributes('-zoomed', True)
except:
    root.geometry("1200x800")

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()
IMG_W = (SCREEN_W // COLS) - 40
IMG_H = (SCREEN_H // ROWS) - 220


# --- UI Header ---
header = tk.Frame(root, bg="#121212")
header.pack(fill="x", padx=20, pady=10)

tk.Label(header, text=f"Reviewing: {TARGET_COLUMN}", fg="#3b82f6", 
         bg="#121212", font=("Arial", 16, "bold")).pack(side="left")



# --- JUMP/SEARCH BOX (Right Side) ---
search_frame = tk.Frame(header, bg="#121212")
search_frame.pack(side="right")


tk.Label(search_frame, text="Jump to Name/Row:", fg="#aaa", bg="#121212").pack(side="left", padx=5)
search_var = tk.StringVar()
search_entry = tk.Entry(search_frame, textvariable=search_var, width=25, bg="#2d2d2d", fg="white", insertbackground="white")
search_entry.pack(side="left", padx=5)


# --- UI Counter ---
counter_label = tk.Label(root, fg="#888", bg="#121212", font=("Arial", 10))
counter_label.pack(anchor="w", padx=20)

grid_frame = tk.Frame(root, bg="#121212")
grid_frame.pack(expand=True, fill="both", padx=10, pady=10)

panels = []


# ================= LOGIC =================

def save_to_disk():
    try:
        df.to_excel(EXCEL_PATH, index=False)
        with open(STATE_FILE, "w") as f:
            f.write(str(current_index))
    except Exception as e:
        
        print(f"❌ Save error: {e}")

def update_visuals(panel_idx):
    p = panels[panel_idx]
    actual_idx = current_index + panel_idx
    if actual_idx < len(df):
        current_val = df.at[actual_idx, TARGET_COLUMN]
        for val, btn in p["buttons"].items():
            btn.config(bg="#3b82f6" if current_val == val else "#2d2d2d", 
                       fg="white" if current_val == val else "#666")

def set_value(panel_idx, new_val):
    actual_idx = current_index + panel_idx
    if actual_idx < len(df):
        df.at[actual_idx, TARGET_COLUMN] = new_val
        update_visuals(panel_idx)
        save_to_disk()


def jump_logic(event=None):
    global current_index
    query = search_var.get().strip().lower()
    if not query:
        return

    # 1. Try to jump by row index number
    if query.isdigit():
        target_idx = int(query)
        if 0 <= target_idx < len(df):
            current_index = (target_idx // IMAGES_PER_BATCH) * IMAGES_PER_BATCH
            load_batch()
            search_entry.delete(0, tk.END)
            return

    
    # 2. Try to jump by filename
    
    matches = df.index[df['Image_Name'].astype(str).str.lower().str.contains(query)].tolist()
    if matches:
        target_idx = matches[0]
        current_index = (target_idx // IMAGES_PER_BATCH) * IMAGES_PER_BATCH
        load_batch()
        search_entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Not Found", f"Meme '{query}' not found in Excel.")

search_entry.bind("<Return>", jump_logic)


def load_batch():
    for i in range(IMAGES_PER_BATCH):
        idx = current_index + i
        p = panels[i]
        if idx < len(df):
            img_name = str(df.at[idx, "Image_Name"])
            path = os.path.join(IMAGE_FOLDER, img_name)
            p["name_label"].config(text=f"[{idx}] {img_name}")
            
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    img.thumbnail((IMG_W, IMG_H))
                    tk_img = ImageTk.PhotoImage(img)
                    p["img_label"].config(image=tk_img, text="")
                    p["img_label"].image = tk_img
                except:
                    p["img_label"].config(image="", text="CORRUPT IMAGE", fg="red")
            else:
                p["img_label"].config(image="", text="FILE NOT FOUND", fg="red")
            update_visuals(i)
            # Show buttons
            for btn in p["buttons"].values(): btn.pack(side="left", padx=5)
        else:
            p["img_label"].config(image="", text="")
            p["name_label"].config(text="")
            for btn in p["buttons"].values(): btn.pack_forget()

    counter_label.config(text=f"Current Batch Start: {current_index} | Total Rows: {len(df)}")


# --- Panel Creation ---

for i in range(IMAGES_PER_BATCH):
    f = tk.Frame(grid_frame, bg="#1e1e1e", highlightbackground="#333", highlightthickness=1)
    f.grid(row=i//COLS, column=i%COLS, padx=5, pady=5, sticky="nsew")
    grid_frame.grid_columnconfigure(i%COLS, weight=1)
    grid_frame.grid_rowconfigure(i//COLS, weight=1)

    p = {"buttons": {}}
    p["img_label"] = tk.Label(f, bg="#1e1e1e")
    p["img_label"].pack(pady=5)
    p["name_label"] = tk.Label(f, fg="#777", bg="#1e1e1e", font=("Arial", 8))
    p["name_label"].pack()

    btn_row = tk.Frame(f, bg="#1e1e1e")
    btn_row.pack(pady=10)

    for v in [0, 1]:
        lbl = "0: No" if v == 0 else "1: Yes"
        b = tk.Label(btn_row, text=lbl, width=10, bg="#2d2d2d", fg="white", cursor="hand2", font=("Arial", 10, "bold"))
        b.bind("<Button-1>", lambda e, p_idx=i, val=v: set_value(p_idx, val))
        p["buttons"][v] = b
    panels.append(p)

# --- Navigation ---
def next_pg():
    global current_index
    if current_index + IMAGES_PER_BATCH < len(df):
        current_index += IMAGES_PER_BATCH
        save_to_disk()
        load_batch()

def prev_pg():
    global current_index
    if current_index - IMAGES_PER_BATCH >= 0:
        current_index -= IMAGES_PER_BATCH
        save_to_disk()
        load_batch()


root.bind("<d>", lambda e: next_pg())
root.bind("<a>", lambda e: prev_pg())

footer = tk.Frame(root, bg="#121212")
footer.pack(fill="x", pady=10)
tk.Button(footer, text=" << PREVIOUS (A) ", command=prev_pg, width=20, bg="#333", fg="white").pack(side="left", padx=50)
tk.Button(footer, text=" NEXT (D) >> ", command=next_pg, width=20, bg="#333", fg="white").pack(side="right", padx=50)

def on_closing():
    save_to_disk()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
load_batch()
root.mainloop()


root.protocol("WM_DELETE_WINDOW", on_closing)
load_batch()
root.mainloop()


root.protocol("WM_DELETE_WINDOW", on_closing)
load_batch()
root.mainloop()


