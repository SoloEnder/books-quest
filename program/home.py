import json
import tkinter as tk
from users_manager import show_users_icons, add_user_cmd

#charger le fichier "user_infos.json"

with open("program/data/users_infos.json", "r") as f:
	users_infos = json.load(f)

# Home Window

home_w = tk.Tk()
home_w.title("Home")

# Pack Users icons

show_users_icons(home_w)
add_user_cmd(home_w)
home_w.mainloop()