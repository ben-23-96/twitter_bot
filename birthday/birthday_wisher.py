from datetime import datetime, date
from db import session, Birthdays
from sqlalchemy import select


class Birthday:
    def __init__(self):
        """class that can add birthday information to the birthdays table on the datbase and read the table to see if there is a birthday today"""
        pass

    def add_birthday(self, user, date):
        """takes the username of a twitter user and birthday date YYYY-MM-DD as strings as input,
         adds these details to the database"""

        new_birthday = Birthdays(name=user, birthday=date)

        session.add(new_birthday)

        session.commit()

        print('addded')

    def check_birthdays(self):
        """reads the birthdays table and checks the data to see if any of the birthdays match the current date,
        if there are birthdays today returns a list of dictionaires, each dictionary containing the twitter username, 'user',
        and their age, 'age'.
        if there are no birthdays returns a empty list"""

        today = datetime.date(datetime.now())
        birthdays_today = []

        birthdays = session.query(Birthdays).all()

        for birthday in birthdays:
            print(birthday)
            year, month, day = birthday.birthday.split('-')
            bday = date(int(year), int(month), int(day))

            if bday.day == today.day and bday.month == today.month:
                age = round((today - bday).days/365)
                birthdays_today.append(
                    {'user': f'@{birthday.name}', 'age': age})
        return birthdays_today
