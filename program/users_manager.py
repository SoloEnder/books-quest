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

# function for draw the user selector
	
def pack_users_i(users_infos, home_w):
	welcome_lb = tk.Label(home_w, text="Who is it ?")
	welcome_lb.grid(row=0, column=0)
	
	# Icon
	
	user_i = tk.PhotoImage(file="program/assets/user.png")
	add_user_i = tk.PhotoImage(file="program/assets/add_user.png")
	
	# Button for add a new user
	
	add_user_b = tk.Button(home_w, image=add_user_i, width=150, height=150)
	add_user_b.image = add_user_i
	add_user_b.grid(row=1, column=0, padx=10)
	
	# Method for pack user
	
	if users_infos["count"] == 1 or users_infos["count"] > 1:
		user_1_b = tk.Button(home_w, image=user_i, height=150, width=150)
		user_1_b.image = user_i
		user_1_b.grid(row=1, column=1, padx=10)
		user_1_lb = tk.Label(home_w, text=users_infos["users"][0]).grid(row=2, column=1)
		
	if users_infos["count"] == 2 or users_infos["count"] > 2:
		user_2_b = tk.Button(home_w, image=user_i, height=150, width=150)
		user_2_b.image = user_i
		user_2_b.grid(row=1, column=2, padx=10)
		user_2_lb = tk.Label(home_w, text=users_infos["users"][1]).grid(row=2, column=2)
		
	if users_infos["count"] == 3 or users_infos["count"] > 3:
		user_3_b = tk.Button(home_w, image=user_i, height=150, width=150)
		user_3_b.image = user_i
		user_3_b.grid(row=1, column=3, padx=10)
		user_3_lb = tk.Label(home_w, text=users_infos["users"][2]).grid(row=2, column=3)
		
	if users_infos["count"] == 4 or users_infos["count"] > 4:
		user_4_b = tk.Button(home_w, image=user_i, height=150, width=150)
		user_4_b.image = user_i
		user_4_b.grid(row=1, column=4, padx=10)
		user_4_lb = tk.Label(home_w, text=users_infos["users"][3]).grid(row=2, column=4)
		
	if users_infos["count"] == 5:
		user_5_b = tk.Button(home_w, image=user_i, height=150, width=150)
		user_5_b.image = user_i
		user_5_b.grid(row=1, column=5, padx=10)
		user_5_lb = tk.Label(home_w, text=users_infos["users"][4]).grid(row=2, column=5)		