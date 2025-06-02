import os, json
from tkinter.messagebox import*

base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "data")
save_path = os.path.join(data_dir, "tree_data.json")

def load_tree_data(table, lang, fichier=save_path):
    l_sl = lang["save_load"]
    
    if not os.path.exists(fichier):
        return

    try:
        
        with open(fichier, "r", encoding="utf-8") as f:
            data = json.load(f)
            
    except Exception:
        
        showerror(title="Load Error", message=l_sl["load_error.msg"])
        
    else:
        
        for item in data:
            table.insert('', 'end', values=item["values"])

def save_tree_data(table, lang, fichier="data/tree_data.json"):
    l_sl = lang["save_load"]
    data = []
    
    for item in table.get_children():
        values = table.item(item)["values"]
        data.append({"values": values})
        
    with open(fichier, "w", encoding="utf-8") as f:
        json.dump(data, f)
 
    showinfo(title="Save", message=l_sl["save_info.msg"])
    
if __name__=="__main__":
	print("Please run 'main.py'\nVeuillez lancer le fichier 'main.py'")
