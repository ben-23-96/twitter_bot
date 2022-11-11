from datetime import datetime, timedelta
from db import session, Log
import sys


class EventLogger:
    def __init__(self) -> None:
        pass

    def add_log_entry(self, entry, is_error=False):

        now = datetime.now()
        details = sys._getframe(1)
        function = details.f_code.co_name
        filename = details.f_code.co_filename
        line = details.f_lineno
        location_string = f"file: {filename}, function: {function}, line: {line}"
        print(now)
        print(location_string)
        if is_error:
            print('ERROR')
        print(entry)
        print('\n')
        self.add_log_entry_to_datbase(
            entry=entry, time=now, location=location_string, is_error=is_error)

    def add_log_entry_to_datbase(self, entry, time, location, is_error=False):

        try:
            new_log_entry = Log(
                message=entry, location=location, time=time, is_error=is_error)
            session.add(new_log_entry)
            session.commit()
        except:
            type_of_message = type(entry).__name__
            length_of_message = len(entry)
            new_log_entry = Log(
                message=f'error writing log message to database, type: {type_of_message}, length: {length_of_message}', time=time)
            session.add(new_log_entry)
            session.commit()

    def read_all_log_entries(self):
        log_entries = session.query(Log).all()
        for entry in log_entries:
            print(entry.time)
            print(entry.location)
            if entry.is_error:
                print('ERROR')
            print(entry.message)
            print('\n')

    def read_error_log_entries(self):
        errors = session.query(Log).filter(Log.is_error).all()
        for error in errors:
            print(error.time)
            print(error.location)
            print(error.message)
            print('\n')

    def delete_old_log_entries(self):
        two_days_ago = datetime.now() - timedelta(2)
        session.query(Log).filter(Log.time < two_days_ago).delete()
        session.commit()
