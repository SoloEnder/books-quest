import tkinter as tk
import sys, json
sys.path.append("program")
import users_manager

#charger le fichier "user_infos.json"
with open("program/data/users_infos.json", "r") as f:
	users_infos = json.load(f)

w_c = "white"
# Fonctions
def add_user():
	users_manager.add_user(home_w)

# Fenêtre
home_w = tk.Tk()
home_w.title("Home")
# Elements d'interface
select_user_lb = tk.Label(home_w, text="Qui est ce ?").grid(row=0, column=0, padx=50, pady=10)
add_user_i = tk.PhotoImage(file="program/assets/add_player.png")
add_user_b = tk.Button(home_w, image=add_user_i, width=150, height=150, command=add_user).grid(row=1, column=0, pady=10)

user_i = tk.PhotoImage(file="program/assets/user.png")
# Placer les icônes de chaque utilisateur
if users_infos["count"] == 1 or users_infos["count"] > 1:
	user_1_b = tk.Button(home_w, image=user_i, height=150, width=150)
	user_1_b.grid(row=1, column=1, padx=10)
	user_1_lb = tk.Label(home_w, text=users_infos["users"][0]).grid(row=2, column=1)
	
if users_infos["count"] == 2 or users_infos["count"] > 2:
	user_2_b = tk.Button(home_w, image=user_i, height=150, width=150)
	user_2_b.grid(row=1, column=2, padx=10)
	user_2_lb = tk.Label(home_w, text=users_infos["users"][1]).grid(row=2, column=2)
	
if users_infos["count"] == 3 or users_infos["count"] > 3:
	user_3_b = tk.Button(home_w, image=user_i, height=150, width=150)
	user_3_b.grid(row=1, column=3, padx=10)
	user_3_lb = tk.Label(home_w, text=users_infos["users"][2]).grid(row=2, column=3)
	
if users_infos["count"] == 4 or users_infos["count"] > 4:
	user_4_b = tk.Button(home_w, image=user_i, height=150, width=150)
	user_4_b.grid(row=1, column=4, padx=10)
	user_4_lb = tk.Label(home_w, text=users_infos["users"][3]).grid(row=2, column=4)
	
if users_infos["count"] == 5:
	user_5_b = tk.Button(home_w, image=user_i, height=150, width=150)
	user_5_b.grid(row=1, column=5, padx=10)
	user_5_lb = tk.Label(home_w, text=users_infos["users"][4]).grid(row=2, column=5)
	
import tree_manager

home_w.mainloop()