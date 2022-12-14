from datetime import datetime, date
from db import session, Birthdays
from logger import EventLogger

log = EventLogger()


class Birthday:
    def __init__(self):
        """class that can add birthday information to the birthdays table on the datbase and read the table to see if there is a birthday today"""
        pass

    def add_birthday(self, user, date):
        """takes the username of a twitter user and birthday date YYYY-MM-DD as strings as input,
         adds these details to the database"""

        log.add_log_entry(
            entry=f'adding birthday for user: {user} on birthday: {date}')
        try:
            new_birthday = Birthdays(name=user, birthday=date)
            session.add(new_birthday)
            session.commit()
        except Exception as e:
            log.add_log_entry(
                entry=f"error adding details to database", is_error=True)
            log.add_log_entry(entry=e, is_error=True)
            return False

        log.add_log_entry(entry='birthday added successfully')
        return True

    def check_birthdays(self):
        """reads the birthdays table and checks the data to see if any of the birthdays match the current date,
        if there are birthdays today returns a list of dictionaires, each dictionary containing the twitter username, 'user',
        and their age, 'age'.
        if there are no birthdays returns a empty list"""
        log.add_log_entry(entry='checking datbase for birthdays')

        today = datetime.date(datetime.now())
        birthdays_today = []

        try:
            # retrieve birthdays from database
            birthdays = session.query(Birthdays).all()
        except Exception as e:
            log.add_log_entry(
                entry='error retrieving birthdays from database', is_error=True)
            log.add_log_entry(entry=e, is_error=True)
            return birthdays_today

        log.add_log_entry(entry='birthdays retrieved from database')

        for birthday in birthdays:
            year, month, day = birthday.birthday.split('-')
            bday = date(int(year), int(month), int(day))

            if bday.day == today.day and bday.month == today.month:  # check if birthday is today
                log.add_log_entry(
                    entry=f'birthday found on {today} for {birthday.name}')
                age = round((today - bday).days/365)
                birthdays_today.append(
                    {'user': f'@{birthday.name}', 'age': age})
        return birthdays_today
