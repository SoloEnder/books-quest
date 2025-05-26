import json
import tkinter as tk
from users_manager import pack_users_i

#charger le fichier "user_infos.json"

with open("program/data/users_infos.json", "r") as f:
	users_infos = json.load(f)

# Home Window

home_w = tk.Tk()
home_w.title("Home")

# Pack Users icons

pack_users_i(users_infos, home_w)
home_w.mainloop()