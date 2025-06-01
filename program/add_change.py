from tkinter.messagebox import*
import tkinter as tk

def add(table, title_e, autor_e, nb_pages_e, lang):
	l_ac = lang["add_change"]
	title = title_e.get()
	autor = autor_e.get()
	nb_pages = nb_pages_e.get()
	
	if title and autor and nb_pages:
			
			try:
				nb_pages = int(nb_pages_e.get())
				
			except ValueError:
				showerror(title="Error", message=l_ac["value_error.msg"])
				
			else:
				data = []
						
				for item in table.get_children():
					values = table.item(item)["values"]
					data.append({"values":values})
					
				if data:
					
					if title not in data[0]["values"]:
						table.insert("", "end", values=(title, autor, nb_pages))
							
					else:
						showerror(title="Error", message=l_ac["exists_error.msg"])
						
				else:
					table.insert("", "end", values=(title, autor, nb_pages))
		
	else:
		showerror(title="Error", message=l_ac["empty_fields_error.msg"])
		
def change(event, table, title_e, autor_e, nb_pages_e, add_b, root, lang):
	l_ac = lang["add_change"]
	selected_item = table.selection()
	values = table.item(selected_item)["values"]
	
	def change_selection():
		
		if selected_item:
			
				
			if title_e.get() and autor_e.get() and nb_pages_e.get():
						title = title_e.get()
						autor = autor_e.get()
						
						try:
							nb_pages = int(nb_pages_e.get())
							
						except ValueError:
							showerror(title="Error", message=l_ac["value_error.msg"])
							
						else:
								data = []
						
								for item in table.get_children():
									values = table.item(item)["values"]
									data.append({"values":values})
					
								if title not in data[0]["values"]:
									table.item(selected_item[0], values=(title, autor, nb_pages))
									
								else:
									showerror(title="Error", message=l_ac["exists_error.msg"])
				
			else:
				showerror(title="Error", message=l_ac["empty_fields_error.msg"])
				
	def back():
				table.selection_set(())
				change_b.grid_remove()
				back_b.grid_remove()
				del_b.grid_remove()
				add_b.config(command=lambda: add(table, title_e, autor_e, nb_pages_e, lang))
				add_b.grid(row=3, column=1)
				title_e.delete(0, tk.END)
				autor_e.delete(0, tk.END)
				nb_pages_e.delete(0, tk.END)
				
		
	def delete_selection():
		item_select = table.selection()
		
		for item in item_select:
				table.delete(item)
		back()
				
		table.selection_set(())
		title_e.delete(0, tk.END)
		autor_e.delete(0, tk.END)
		nb_pages_e.delete(0, tk.END)
				
				
	if selected_item:
		title_e.delete(0, tk.END)
		autor_e.delete(0, tk.END)
		nb_pages_e.delete(0, tk.END)
		title_e.insert(0, values[0])
		autor_e.insert(0, values[1])
		nb_pages_e.insert(0, values[2])
		add_b.grid_remove()
		change_b = tk.Button(root, text=l_ac["change_b.text"], command=change_selection, width=8)
		change_b.grid(row=3, column=1)
		del_b = tk.Button(root, text=l_ac["delete_b.text"], command=delete_selection, width=8)
		del_b.grid(row=4, column=1)
		back_b = tk.Button(root, text=l_ac["back_b.text"], command=back, width=8)
		back_b.grid(row=5, column=1)
		
if __name__=="__main__":
	print("Please run 'main.py'\nVeuillez lancer le fichier 'main.py'")
