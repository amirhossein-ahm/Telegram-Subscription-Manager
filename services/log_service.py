import traceback

from models import Log, db_session


class LogService:

    def write(self, level: str, message: str):

        with db_session() as db:
            entry = Log(level=level.upper(), message=message[:5000])

            try:
                db.add(entry)
                db.commit()

            except Exception as exc:

                print(f"Failed to write log: {exc}")

                db.rollback()

    def info(self, message: str):

        self.write("INFO", message)

    def warning(self, message: str):

        self.write("WARNING", message)

    def error(self, message: str):

        self.write("ERROR", message)

    def exception(self, exc: Exception):

        self.write("ERROR", f"{type(exc).__name__}: {str(exc)}")

        self.write("ERROR", traceback.format_exc())

    def get_logs(self, limit: int = 500):

        with db_session() as db:
            return db.query(Log).order_by(Log.id.desc()).limit(limit).all()

    def clear_logs(self):

        with db_session() as db:
            db.query(Log).delete()

            db.commit()


log_service = LogService()
