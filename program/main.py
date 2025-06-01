import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import*
import json, os, save_load, add_change, settings

# Charger les données des paramètres
with open("data/settings_data.json", "r") as f:
	settings_data = json.load(f)
	
lang = settings_data["language"]
	
with open(f"data/{lang}.lang", "r") as f:
	lang = json.load(f)
	
l_m = lang["main"]
	
root = tk.Tk()
root.title("Book Quest")

def add():
	add_change.add(table, title_e, autor_e, nb_pages_e, lang)
	
def change(event):
	add_change.change(event, table, title_e, autor_e, nb_pages_e, add_b, root, lang)
	
def exit():
	exit = askyesno(title="Exit", message=l_m["exit.msg"])
	if exit == True:
		root.destroy()
		
def save():
	save_load.save_tree_data(table, lang)
	
def show_settings():
	settings.settings(root, settings_data)
	
	
# Interface
# Title
title_lb = tk.Label(root, text=l_m["title_lb.text"])
title_lb.grid(row=0, column=0, padx=100, pady=50)
title_e = tk.Entry(root)
title_e.grid(row=0, column=1)
# Autor
autor_lb = tk.Label(root, text=l_m["autor_lb.text"])
autor_lb.grid(row=1, column=0)
autor_e = tk.Entry(root)
autor_e.grid(row=1, column=1)
# Number of pages
nb_pages_lb = tk.Label(root, text=l_m["number_of_pages_lb.text"])
nb_pages_lb.grid(row=2, column=0, pady=50)
nb_pages_e = tk.Entry(root)
nb_pages_e.grid(row=2, column=1)
# Button
add_b = tk.Button(root, text=l_m["add_b.text"], command=add, width=8)
add_b.grid(row=3, column=1)
# Table
table_columns = (l_m["table_col_name.text"][0], l_m["table_col_name.text"][1], l_m["table_col_name.text"][2])
table = ttk.Treeview(root, column=table_columns, show="headings")
save_load.load_tree_data(table, lang)
#Menu
menubar = tk.Menu(root)
menu = tk.Menu(menubar)
menubar.add_cascade(label="Menu", menu=menu)
menu.add_command(label=l_m["menu_lb.text"][0], command=save)
menu.add_command(label=l_m["menu_lb.text"][1], command=show_settings)
menu.add_command(label=l_m["menu_lb.text"][2], command=exit)
root.config(menu=menubar)

for col in table_columns:
	table.heading(col, text=col)
table.bind("<<TreeviewSelect>>", change)
table.grid(row=0, column=2,rowspan=4,  padx=200)
root.mainloop()
