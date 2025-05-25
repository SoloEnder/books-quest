import tkinter as tk
from tkinter.messagebox import*
import json, os, datetime, sys

current_dir = os.path.dirname(__file__)  # dossier où se trouve A.py
users_infos_path = os.path.join(current_dir, "data", "users_infos.json")

with open(users_infos_path, "r") as f:
	users_infos = json.load(f)
	
users_list = users_infos["users"]
users_list_l = []

for user in users_list:
	users_list_l.append(user.lower())
print(users_list_l)
users_count = users_infos["count"]

# ajouter un utilisateur
def add_user(home_w):
	# Créer les éléments pour le nouvel utilisateur
	def create_user():
			global users_count
			new_user_name = new_user_name_e.get()
			new_user_data = {"name":new_user_name, "xp":0, "lvl":0}
			
			if new_user_name:
			
				if  users_count < 5 or users_count==5:
				
					if new_user_name.lower() not in users_list_l:
						add_user_apply = askyesno(message="Le programme doit redémarrer pour appliquer ces modifications (ne le fermez pas vous même, ça sera automatique)")
						
						if add_user_apply == True:
							os.mkdir(f"program/users/{new_user_name.lower()}")
							
							with open(f"program/users/{new_user_name.lower()}/user_infos.json", "w") as f:
								users_list.append(new_user_name)
								users_count += 1
								json.dump(new_user_data, f)
								
							with open(users_infos_path, "w") as f:
								users_infos["users"] = users_list
								users_infos["count"] = users_count
								json.dump(users_infos, f)
								
							home_w.destroy()
								
							
					else:
							showerror(message="Ce nom est déjà utilisé")
							
				else:
							showerror(message="Vous avez atteint la limite de 5 utilisateurs maximum")
							
			else:
				showerror(message="Veuillez remplir le champs !")
	
	# Interface				
	add_user_w = tk.Toplevel(home_w)
	add_user_w.title("New User")
	new_user_name_lb = tk.Label(add_user_w, text="Enter the name of the new user").grid(row=0, column=0, padx=20, pady=10)
	new_user_name_e = tk.Entry(add_user_w)
	new_user_name_e.grid(row=1, column=0)
	add_user_b = tk.Button(add_user_w, text="Create", command=create_user).grid(row=2, column=0, pady=10)
	