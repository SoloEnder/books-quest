class BooksShelfExistsError(Exception):
    def __init__(self, shelf_id: str, msg: str|None=None):
        self.shelf_id = shelf_id
        self.msg = msg or f"Book shelf with the ID {shelf_id} already exists !"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class BooksShelfNotFoundError(Exception):
    def __init__(self, shelf_id: str, msg: str|None=None):
        self.shelf_id = shelf_id
        self.msg = msg or (
            f"Book shelf with ID {shelf_id} dosen't exists ! Has been it deleted ?"
        )
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg


class BookNotFoundError(Exception):
    def __init__(self, book_id: str, container, msg: str|None=None):
        self.book_id = book_id
        self.msg = msg or f"Book with ID {book_id} dosen't exists in {container} ! Has been it deleted ?"
        super().__init__()

    def __str__(self) -> str:
        return self.msg


class BookExistsError(Exception):
    def __init__(self, book_id: str, container_name: str, msg: str|None=None):
        self.book_id = book_id
        self.msg = msg or f"Book with ID {book_id} arleady exists in {container_name} !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg


class PageNotFoundError(Exception):
    def __init__(self, page_name: str, msg: str|None=None):
        self.page_name = page_name
        self.msg = msg or f"Page '{page_name}' doesn't exists !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
    
class PageNotLoadedError(Exception):

    def __init__(self, index, msg: str|None=None):
        """
        Exception usualy raised when trying to do something on a page which is not loaded yet
        
        Args:
        - index: the page virtual index
        """
        self.index = index
        self.msg = msg or f"Page at virtual index '{index} not loaded !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
    
class InvalidDictPathError(Exception):

    def __init__(self, dict_path, msg: str|None=None):
        self.dict_path = dict_path
        self.msg = msg or f"Dict path '{self.dict_path}' isn't a valid dict path !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
    
class RessBasePathNotFound(Exception):
    def __init__(self, dict_path, msg: str|None=None):
        self.dict_path = dict_path
        self.msg = msg or f"Unable to make path with dict path '{self.dict_path}' : no valid _base_ key found !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
    
class InvalidWidgetIndexError(Exception):

    def __init__(self, widget, msg: str|None=None):
        """
        Exception usually raised when the index of a 'InPageWidget' instance is not valid
        """
        self.widget = widget
        self.msg = msg or f"Invalid index for widget '{self.widget}' : {widget.index} !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
