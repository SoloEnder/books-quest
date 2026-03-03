class BooksShelfExistsError(Exception):
    def __init__(self, shelf_id: str):
        self.shelf_id = shelf_id
        super().__init__(f"Book shelf with the ID {shelf_id} already exists !")


class BooksShelfNotFoundError(Exception):
    def __init__(self, shelf_id: str):
        self.shelf_id = shelf_id
        super().__init__(
            f"Book shelf with ID {shelf_id} dosen't exists ! Has been it deleted ?"
        )


class BookNotFoundError(Exception):
    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(
            f"Book with ID {book_id} dosen't exists ! Has been it deleted ?"
        )


class BookExistsError(Exception):
    def __init__(self, book_id: str):
        self.book_id = book_id
        super().__init__(f"Book with ID {book_id} arleady exists in this sequence !")


class PageNotFoundError(Exception):
    def __init__(self, page_name: str):
        self.page_name = page_name
        super().__init__(f"Page '{page_name}' does't exists !")
