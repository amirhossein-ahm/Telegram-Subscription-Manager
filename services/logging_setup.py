import logging

from services.log_service import log_service


class DatabaseLogHandler(logging.Handler):

    def emit(self, record):

        try:

            msg = self.format(record)

            log_service.write(record.levelname, msg)

        except Exception:
            pass


def setup_logging():

    root = logging.getLogger()

    root.setLevel(logging.INFO)

    if any(isinstance(handler, DatabaseLogHandler) for handler in root.handlers):
        return

    db_handler = DatabaseLogHandler()

    db_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))

    root.addHandler(db_handler)
