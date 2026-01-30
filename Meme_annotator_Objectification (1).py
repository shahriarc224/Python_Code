import os
import pandas as pd
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox

# ---------- CONFIG ----------
image_folder = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes"
excel_path = r"E:\meme resesarch by sabbir\Memes (2)(1)\Memes\Meme_annotations_Binar.xlsx"
field = "Objectification"
translation = "বস্তুনিষ্ঠকরণ"
values = [0, 1]
IMAGES_PER_PAGE = 8
COLS = 4
# ----------------------------

# ---------- LOAD DATA ----------
if not os.path.exists(excel_path):
    print(f"Error: Could not find Excel file at {excel_path}")
    exit()

df = pd.read_excel(excel_path)
if field not in df.columns:
    df[field] = None

total_memes = len(df)
rows = df.index.tolist()
page_index = 0
temp_labels = {}

# ---------- GUI ----------
root = tk.Tk()
root.title("Meme Annotation Tool")
root.state("zoomed")
root.configure(bg="#121212")

# ---------- HEADER ----------
header = tk.Frame(root, bg="#121212", pady=5)
header.pack(fill="x")

tk.Label(
    header,
    text=f"{field} ({translation})",
    font=("Arial", 22, "bold"),
    fg="#3b82f6",
    bg="#121212"
).pack()

progress_label = tk.Label(header, fg="#aaaaaa", bg="#121212", font=("Arial", 11))
progress_label.pack()

# ---------- SEARCH & JUMP SECTION ----------
nav_bar = tk.Frame(header, bg="#121212")
nav_bar.pack(pady=10)

# Search by Name Box
tk.Label(nav_bar, text="Search Meme Name:", fg="#3b82f6", bg="#121212", font=("Arial", 10, "bold")).pack(side="left", padx=5)
search_entry = tk.Entry(nav_bar, width=25, font=("Arial", 10))
search_entry.pack(side="left", padx=5)

def perform_search():
    global page_index
    query = search_entry.get().strip()
    if not query:
        return

    # Look for the first image name that contains the query text
    match = df[df['Image_Name'].astype(str).str.contains(query, case=False, na=False)]
    
    if not match.empty:
        target_idx = match.index[0]
        page_index = target_idx // IMAGES_PER_PAGE
        load_page()
        # Optional: highlight the specific entry or just inform the user
        search_entry.delete(0, tk.END)
    else:
        messagebox.showinfo("Not Found", f"No meme found with name: {query}")

tk.Button(nav_bar, text="FIND & JUMP", command=perform_search, bg="#3b82f6", fg="white", padx=10).pack(side="left", padx=5)

# Quick Index Jump
tk.Label(nav_bar, text="|  Jump to Index:", fg="white", bg="#121212").pack(side="left", padx=15)
idx_entry = tk.Entry(nav_bar, width=8)
idx_entry.pack(side="left")

def jump_to_index():
    global page_index
    try:
        val = int(idx_entry.get().strip())
        if 0 <= val < total_memes:
            page_index = val // IMAGES_PER_PAGE
            load_page()
            idx_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Out of Range", f"Please enter index between 0 and {total_memes-1}")
    except ValueError:
        pass

tk.Button(nav_bar, text="GO", command=jump_to_index, bg="#444", fg="white").pack(side="left", padx=5)

# ---------- GRID ----------
main_container = tk.Frame(root, bg="#121212")
main_container.pack(fill="both", expand=True)

grid_frame = tk.Frame(main_container, bg="#121212")
grid_frame.pack(expand=True)

img_refs = []
button_refs = {}

def update_status():
    done = df[field].notna().sum()
    percent = (done / total_memes) * 100
    progress_label.config(
        text=f"Progress: {done}/{total_memes} ({percent:.1f}%) | Page {page_index+1}"
    )

def set_label(idx, val):
    temp_labels[idx] = val
    if idx in button_refs:
        for v, btn in button_refs[idx].items():
            btn.config(bg="#10b981" if v == val else "#444")

def load_page():
    for w in grid_frame.winfo_children():
        w.destroy()
    img_refs.clear()
    button_refs.clear()
    update_status()

    start = page_index * IMAGES_PER_PAGE
    end = min(start + IMAGES_PER_PAGE, total_memes)
    page_rows = rows[start:end]

    for i, idx in enumerate(page_rows):
        r, c = i // COLS, i % COLS
        cell = tk.Frame(grid_frame, bg="#1e1e1e", highlightthickness=1, highlightbackground="#333")
        cell.grid(row=r, column=c, padx=12, pady=8)

        tk.Label(cell, text=f"Index: {idx}", fg="#888", bg="#1e1e1e", font=("Arial", 8)).pack()

        img_name = str(df.at[idx, "Image_Name"])
        img_path = os.path.join(image_folder, img_name)
        try:
            img = Image.open(img_path)
            img.thumbnail((300, 240))
            tk_img = ImageTk.PhotoImage(img)
            img_refs.append(tk_img)
            tk.Label(cell, image=tk_img, bg="#1e1e1e").pack()
        except:
            tk.Label(cell, text=f"Missing:\n{img_name}", fg="red", bg="#1e1e1e", width=25, height=10).pack()

        btn_frame = tk.Frame(cell, bg="#1e1e1e", pady=5)
        btn_frame.pack()

        current_val = temp_labels.get(idx, df.at[idx, field])
        button_refs[idx] = {}

        for v in values:
            is_active = (current_val == v and current_val is not None)
            btn = tk.Button(
                btn_frame, text=str(v), width=10,
                bg="#10b981" if is_active else "#444",
                fg="white", font=("Arial", 10, "bold")
            )
            btn.pack(side="left", padx=5)
            btn.config(command=lambda i=idx, val=v: set_label(i, val))
            button_refs[idx][v] = btn

def save_current():
    if temp_labels:
        for idx, val in temp_labels.items():
            df.at[idx, field] = val
        df.to_excel(excel_path, index=False)
        temp_labels.clear()

def next_page(event=None):
    global page_index
    save_current()
    if (page_index + 1) * IMAGES_PER_PAGE < total_memes:
        page_index += 1
        load_page()
    else:
        messagebox.showinfo("Done", "You reached the last page.")

def prev_page(event=None):
    global page_index
    save_current()
    if page_index > 0:
        page_index -= 1
        load_page()

def bulk_zero(event=None):
    start = page_index * IMAGES_PER_PAGE
    end = min(start + IMAGES_PER_PAGE, total_memes)
    for idx in rows[start:end]:
        set_label(idx, 0)

# ---------- FOOTER ----------
footer = tk.Frame(root, bg="#121212", pady=15)
footer.pack(fill="x", side="bottom")

tk.Button(footer, text="⬅ PREVIOUS (Left Arrow)", command=prev_page, bg="#444", fg="white", width=25).pack(side="left", padx=100)
tk.Button(footer, text="SAVE & NEXT (Enter) ➡", command=next_page, bg="#3b82f6", fg="white", font=("Arial", 14, "bold"), width=30).pack(side="right", padx=100)

# ---------- KEY BINDINGS ----------
root.bind("<Left>", prev_page)
root.bind("<Return>", next_page)
root.bind("0", bulk_zero)

load_page()
root.mainloop()