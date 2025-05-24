import tkinter as tk
from tkinter.messagebox import*
import json

def settings(root, settings_data):
	lang_rb = False
	settings_w = tk.Toplevel(root)
	settings_w.title("Settings")
	
	def languages():
		nonlocal lang_rb
		
		def change_lang():
			settings_data["language"] =lang_var.get()
			
			
			with open("data/settings_data.json", "w") as f:
				json.dump(settings_data, f)
				
			showinfo(title="Reboot", message="This action required program reboot")
			root.destroy()
		
		if lang_rb==False:	
			lang_var = tk.StringVar()
			lang_var.set(settings_data["language"])
			en_lang_rb = tk.Radiobutton(settings_w, text="  English", variable=lang_var, value="en", command=change_lang)
			fr_lang_rb = tk.Radiobutton(settings_w, text="Français", variable=lang_var, value="fr", command=change_lang)
			en_lang_rb.grid(row=0,column=1)
			fr_lang_rb.grid(row=1, column=1)
			lang_rb = True
			
	def about():
		about_w = tk.Toplevel(root)
		about_w.title("About")
		ex1 = tk.PhotoImage(file="exemple.png")
		ex1_lb = tk.Label(about_w, image=ex1)
		ex1_lb.image = ex1
		ex1_lb.grid(row=1, column=0, padx=20, pady=20)
		exp1_lb = tk.Label(about_w, text="You can now switch between English or French !").grid(row=2, column=0)
		exp2_lb = tk.Label(about_w, text="""-Update UI
- Books gestions improvement 
- Internal changes""").grid(row=3, column=0)
		exp3_lb = tk.Label(about_w, text="v.2.1.1 Released the 2025/05/19").grid(row=0, column=0)
			
	about_b = tk.Button(settings_w, text="About", command=about, width=15)
	about_b.grid(row=1, column=0)	
	
		
	lang_settings_b = tk.Button(settings_w, text="Language", command=languages, width=15)
	lang_settings_b.grid(row=0, column=0, pady=10)
		
if __name__=="__main__":
	print("Please run 'main.py'\nVeuillez lancer le fichier 'main.py'")