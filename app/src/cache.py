
        
class Cache:
    
    def __init__(self):
        self._entries = {}
        
    def add_entry(self, name: str, data):
        """
        Add a new entry to this cache.
        
        Args:
            - name : the name attribuated to this entry
            - data : the data attached to this entry
        """
        
        
        if not name in self._entries:
            self._entries[name] = data
            
        else:
            raise EntryExistsError(name)  
            
    def get_data(self, name):
        """
        Add a new entry to this cache.
        
        Args:
            - name : the name attached to the data to get
        """
        
        try:
            return self._entries[name]
        
        except KeyError:
            raise EntryNotFoundError(name)
        
    def clear_entry(self, name: str):
        """
        Removes an entry. Unlike 'clear_data', the entry (name and data) will be removed
        
        Args:
            - name: the name attached to the entry
        """
        
        
        try:
            del self._entries[name]
            
        except KeyError:
            raise EntryNotFoundError(name)
        
    def clear_data(self, name):
        """
        Removes the data of an entry. Unlike clear_entry, only the data are removed, not the entry.
        
        Args:
            - name: the name of the entry
        """
        
        try:
            self._entries[name] = None
            
        except KeyError:
            raise EntryNotFoundError(name)
        
    def set_entry_name(self, old_name, new_name: str):
        """
        Edit the name of an entry
        
        Args:
            - old_name: the name of the entry you want to modify
            - new_name: the new name of the entry
        """
        
        
        try:
            self._entries[new_name] = self._entries[old_name]
            del self._entries[old_name]
            
        except KeyError:
            raise EntryNotFoundError(old_name)
        
    def set_entry_data(self, name, new_data):
        """
        Edit the data of an entry
        
        Args:
            - name: the name of the entry
            - new_data: the new data
        """
        try:
            self._entries[name] = new_data
            
        except KeyError:
            raise EntryNotFoundError(name)
        
    def edit_entry(self, old_name: str, new_name: str|None=None, new_data=None):
        
        if new_data is not None:
            self.set_entry_data(old_name, new_data)
        
        if new_name is not None:
            self.set_entry_name(old_name, new_name)
        
    
#exceptions
class EntryExistsError(Exception):
    
    def __init__(self, entry_name: str):
        """
        Exception usualy raised when attempting to add an entry with an already existant name
        """
        
        self.entry_name = entry_name
        self.msg = f"Entry '{self.entry_name}' already exists in cache !"
        
    def __str__(self):
        return self.msg
        
class EntryNotFoundError(Exception):
    
    def __init__(self, entry_name: str):
        """
        Exception usualy raised when trying to do operation on a entry that is not exists
        """
        self.entry_name = entry_name
        self.msg = f"Entry '{self.entry_name}' not in cache !"
        
    def __str__(self):
        return self.msg
        
        