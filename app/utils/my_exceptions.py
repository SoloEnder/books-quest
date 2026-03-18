class BooksShelfExistsError(Exception):
    def __init__(self, shelf_id: str):
        self.shelf_id = shelf_id
        self.msg = f"Book shelf with the ID {shelf_id} already exists !"
        super().__init__(self.msg)

    def __str__(self):
        return self.msg


class BooksShelfNotFoundError(Exception):
    def __init__(self, shelf_id: str):
        self.shelf_id = shelf_id
        self.msg = (
            f"Book shelf with ID {shelf_id} dosen't exists ! Has been it deleted ?"
        )
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg


class BookNotFoundError(Exception):
    def __init__(self, book_id: str):
        self.book_id = book_id
        self.msg = f"Book with ID {book_id} dosen't exists ! Has been it deleted ?"
        super().__init__()

    def __str__(self) -> str:
        return self.msg


class BookExistsError(Exception):
    def __init__(self, book_id: str):
        self.book_id = book_id
        self.msg = f"Book with ID {book_id} arleady exists in this sequence !"
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg


class PageNotFoundError(Exception):
    def __init__(self, page_name: str):
        self.page_name = page_name
        self.msg = f"Page '{page_name}' does't exists !" if not msg else msg
        super().__init__(self.msg)

    def __str__(self) -> str:
        return self.msg
