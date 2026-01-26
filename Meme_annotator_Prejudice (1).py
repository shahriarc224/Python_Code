import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

image_folder = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes"
excel_path = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes\Meme_annotations_Binar.xlsx"
target_column = "Prejudice"

df = pd.read_excel(excel_path)

if target_column not in df.columns:
    df[target_column] = None

df = df.sort_values(
    by="Image_Name",
    key=lambda x: x.astype(str).str.extract(r"(\d+)")[0].astype(float)
).reset_index(drop=True)

rows_to_annotate = df[df[target_column].isna()].index.tolist()
if not rows_to_annotate:
    print(f"All '{target_column}' annotations are completed!")
    exit()

current_index = 0
POSSIBLE_VALUES = [0, 1]

root = tk.Tk()
root.title(f"{target_column} Annotation Tool")
root.geometry("900x650")
root.configure(bg="#1e1e1e")

image_label = tk.Label(root, bg="#1e1e1e")
image_label.pack(pady=20)

filename_label = tk.Label(root, text="", fg="white", bg="#1e1e1e",
                          font=("Arial", 14, "bold"))
filename_label.pack(pady=5)

value_var = tk.IntVar(value=-1)

# Highlight frame
frame = tk.Frame(
    root,
    bg="#1e1e1e",
    highlightthickness=2,
    highlightbackground="#3b82f6",
    highlightcolor="#3b82f6"
)
frame.pack(pady=10)

def load():
    idx = rows_to_annotate[current_index]
    img_name = df.at[idx, "Image_Name"]
    img_path = os.path.join(image_folder, img_name)

    if not os.path.exists(img_path):
        messagebox.showerror("Error", f"Image not found:\n{img_path}")
        root.destroy()
        return

    img = Image.open(img_path)
    img.thumbnail((800, 500))
    tk_img = ImageTk.PhotoImage(img)

    image_label.configure(image=tk_img)
    image_label.image = tk_img

    filename_label.configure(
        text=f"{current_index+1}/{len(rows_to_annotate)} — {img_name}"
    )

    value_var.set(-1)
    update_display()

def save_next(event=None):
    global current_index

    val = value_var.get()
    if val == -1:
        messagebox.showwarning("Missing", "Press 0 or any number > 0 before Enter.")
        return

    idx = rows_to_annotate[current_index]
    df.at[idx, target_column] = int(val)

    # Save progress immediately
    df.to_excel(excel_path, index=False)

    current_index += 1

    if current_index >= len(rows_to_annotate):
        messagebox.showinfo("DONE", f"{target_column} Completed!")
        root.destroy()
        return

    load()

tk.Label(frame, text=target_column, fg="white", bg="#1e1e1e",
         font=("Arial", 12)).pack(pady=(8, 4))

row = tk.Frame(frame, bg="#1e1e1e")
row.pack(pady=(0, 5))

for v in POSSIBLE_VALUES:
    tk.Radiobutton(
        row,
        text=str(v),
        variable=value_var,
        value=v,
        indicatoron=False,
        width=6,
        font=("Arial", 12),
        bg="#333",
        fg="white",
        selectcolor="#3b82f6",
        relief="ridge"
    ).pack(side="left", padx=6)

value_display = tk.Label(
    frame, text="Value: -", fg="white", bg="#1e1e1e", font=("Arial", 12)
)
value_display.pack(pady=(4, 8))

def update_display():
    v = value_var.get()
    value_display.config(text=f"Value: {v if v != -1 else '-'}")

# --- MODIFIED KEYBOARD CONTROL ---
def on_key(event):
    char = event.char

    # If digit key pressed (0–9)
    if char.isdigit():
        num = int(char)

        if num == 0:
            value_var.set(0)
        else:
            value_var.set(1)

        update_display()

    # Enter key triggers save & next
    elif event.keysym == "Return":
        save_next()

value_var.trace_add("write", lambda *args: update_display())
root.bind("<Key>", on_key)

tk.Button(
    root, text="Save & Next", command=save_next,
    width=18, height=2, bg="#3b82f6", fg="white", font=("Arial", 14)
).pack(pady=20)

load()
root.mainloop()