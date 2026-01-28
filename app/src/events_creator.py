
import logging

logger = logging.getLogger(__name__)

def create_event(events_handler):
    """
    Create all the events

    Args:
    events_handler: an instance of event_sentinel.EventsHandler class
    """
    # Books Events
    logger.info("Creating books event...")
    events_handler.create_event(event_name="System.Books.BookDeletionRequest", book_id=None)
    events_handler.create_event("System.Books.ShelfCreationRequest", shelf_name=None, shelf_books=None, shelf_id=None)
    events_handler.create_event(
            event_name="System.Books.BookCreationRequest", 
            title=None, 
            authors=None, 
            edition=None,
            isbn=None, 
            summary=None,
            start_read_date=None,
            end_read_date=None,
            status=None,tot_pages=None,
            alr_read_pages=None,
            books_shelfs=None,
            series=None,
            internal_id=None
            )
    events_handler.create_event("System.Books.BookEditionRequest", book_id=None, new_book=None)
    events_handler.create_event("System.Books.CreateBaseShelf")
    events_handler.create_event("System.Books.ShelfUpdated",  shelf=None)
    events_handler.create_event("System.Books.SaveShelfsData", filepath=None)
    events_handler.create_event("System.Books.LoadShelfsData", filepath=None)
    events_handler.create_event("System.Books.ShelfCreated", shelf=None)

    # Ui Events
    logger.info("Creating ui events")
    events_handler.create_event("System.Ui.ShelfFrameCreationRequest", shelf=None)
    events_handler.create_event("System.Ui.ShelfFrameCreated", shelf_fr=None)
    events_handler.create_event("System.Ui.BookLocationCreationRequest", book_object=None)