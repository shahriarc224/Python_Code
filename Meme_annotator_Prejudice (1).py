import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ---------------- CONFIG ----------------
image_folder = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes"
excel_path = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes\Meme_annotations_Binar.xlsx"
target_column = "Prejudice"
BATCH_SIZE = 6 # You mentioned 4 in your text, but your code uses 6. I kept 6 to match your grid.
# ----------------------------------------

df = pd.read_excel(excel_path)

if target_column not in df.columns:
    df[target_column] = None

# Sorting logic to keep images in order
df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

rows_to_annotate = df[df[target_column].isna()].index.tolist()

if not rows_to_annotate:
    print(f"All '{target_column}' annotations are completed!")
    exit()

current_index = 0

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Prejudice Annotation Tool")
root.geometry("1500x900")
root.configure(bg="#1e1e1e")

subject_label = tk.Label(
    root,
    text="Prejudice Annotation (Press '0' to set all to 0, Click '1' to change)",
    fg="white",
    bg="#1e1e1e",
    font=("Arial", 18, "bold")
)
subject_label.pack(anchor="nw", padx=20, pady=10)

main_frame = tk.Frame(root, bg="#1e1e1e")
main_frame.pack(expand=True)

image_widgets = []
value_vars = []
photo_refs = []

for i in range(BATCH_SIZE):
    frame = tk.Frame(
        main_frame,
        bg="#1e1e1e",
        highlightthickness=2,
        highlightbackground="#3b82f6"
    )
    frame.grid(row=i // 3, column=i % 3, padx=25, pady=20)

    img_label = tk.Label(frame, bg="#1e1e1e")
    img_label.pack()

    name_label = tk.Label(frame, fg="white", bg="#1e1e1e", font=("Arial", 10))
    name_label.pack()

    value_var = tk.IntVar(value=-1)
    value_vars.append(value_var)

    btn_frame = tk.Frame(frame, bg="#1e1e1e")
    btn_frame.pack(pady=6)

    for val in [0, 1]:
        tk.Radiobutton(
            btn_frame,
            text=str(val),
            variable=value_var,
            value=val,
            indicatoron=False,
            width=6,
            bg="#333",
            fg="white",
            selectcolor="#3b82f6",
            font=("Arial", 11)
        ).pack(side="left", padx=5)

    image_widgets.append((img_label, name_label))

# ---------------- LOGIC ----------------

def set_all_zero(event=None):
    """Sets all visible images in the batch to 0"""
    for i in range(BATCH_SIZE):
        idx_position = current_index + i
        # Only set to 0 if there is actually an image in that slot
        if idx_position < len(rows_to_annotate):
            value_vars[i].set(0)

def load_batch():
    global photo_refs
    photo_refs = []
    for i in range(BATCH_SIZE):
        idx_position = current_index + i
        if idx_position >= len(rows_to_annotate):
            image_widgets[i][0].config(image="")
            image_widgets[i][1].config(text="")
            value_vars[i].set(-1)
            continue

        df_idx = rows_to_annotate[idx_position]
        img_name = df.at[df_idx, "Image_Name"]
        img_path = os.path.join(image_folder, img_name)

        if os.path.exists(img_path):
            img = Image.open(img_path)
            img.thumbnail((420, 260))
            tk_img = ImageTk.PhotoImage(img)
            image_widgets[i][0].config(image=tk_img)
            image_widgets[i][0].image = tk_img 
            image_widgets[i][1].config(text=img_name)
            photo_refs.append(tk_img)
        
        value_vars[i].set(-1) # Reset to unselected for new batch

def save_next(event=None):
    global current_index
    # Check if all visible images are annotated
    for i in range(BATCH_SIZE):
        idx_position = current_index + i
        if idx_position < len(rows_to_annotate) and value_vars[i].get() == -1:
            messagebox.showwarning("Missing Annotation", "Please annotate all images (or press '0' for all zero).")
            return

    # Save to DataFrame
    for i in range(BATCH_SIZE):
        idx_position = current_index + i
        if idx_position < len(rows_to_annotate):
            df_idx = rows_to_annotate[idx_position]
            df.at[df_idx, target_column] = int(value_vars[i].get())

    df.to_excel(excel_path, index=False)
    current_index += BATCH_SIZE

    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("DONE", "Annotation completed!")
        root.destroy()
    else:
        load_batch()

# ---------------- KEYBOARD BINDINGS ----------------
root.bind("0", set_all_zero)  # Pressing 0 sets all visible to 0
root.bind("<Return>", save_next) # Pressing Enter saves and moves to next batch

# Optional: Number keys 1-6 to toggle '1' for specific images
def toggle_one(idx):
    if value_vars[idx].get() == 1:
        value_vars[idx].set(0)
    else:
        value_vars[idx].set(1)

root.bind("1", lambda e: toggle_one(0))
root.bind("2", lambda e: toggle_one(1))
root.bind("3", lambda e: toggle_one(2))
root.bind("4", lambda e: toggle_one(3))
root.bind("5", lambda e: toggle_one(4))
root.bind("6", lambda e: toggle_one(5))

# ---- SAVE BUTTON ----
tk.Button(
    root,
    text="Save & Next (Enter)",
    command=save_next,
    width=25,
    height=2,
    bg="#3b82f6",
    fg="white",
    font=("Arial", 14, "bold")
).pack(pady=20)

load_batch()
root.mainloop()
