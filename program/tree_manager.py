import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import*	

manage_books_w = tk.Tk()
manage_books_w.title("Manage books")
# Interface
# Title
title_lb = tk.Label(manage_books_w, text="Titre")
title_lb.grid(row=0, column=0, padx=100, pady=50)
title_e = tk.Entry(manage_books_w)
title_e.grid(row=0, column=1)
# Autor
autor_lb = tk.Label(manage_books_w, text="Autor")
autor_lb.grid(row=1, column=0)
autor_e = tk.Entry(manage_books_w)
autor_e.grid(row=1, column=1)
# Number of pages
nb_pages_lb = tk.Label(manage_books_w, text="Number of pages")
nb_pages_lb.grid(row=2, column=0, pady=50)
nb_pages_e = tk.Entry(manage_books_w)
nb_pages_e.grid(row=2, column=1)
# Button
add_b = tk.Button(manage_books_w, text="Add", width=8)
add_b.grid(row=3, column=1)
# Table
table_columns = ("Title", "Autor","Number of pages")
table = ttk.Treeview(manage_books_w, column=table_columns, show="headings")

for col in table_columns:
	table.heading(col, text=col)
table.grid(row=0, column=2,rowspan=4,  padx=200)
manage_books_w.mainloop()