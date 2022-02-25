import json
from datetime import datetime, date


class Birthday:
    def __init__(self):
        """class that can add birthday information to the birthdays.txt file for storage
        and read the file to see if there is a birthday today on the birthdays.json file"""
        pass

    def add_birthday(self, user, date):
        """takes the username of a twitter user and birthday date YYYY-MM-DD as strings as input,
         adds these details as json to the birthdays.json file"""

        with open('birthday/birthdays.json', 'r') as file:
            data = json.load(file)
            try:
                data["birthdays"][user] = date
            except KeyError:
                data = {"birthdays": {}}
            else:
                data["birthdays"][user] = date
        with open('birthday/birthdays.json', 'w') as file:
            json.dump(data, file)

    def check_birthdays(self):
        """reads the birthdays.json file and checks the data to see if any of the birthdays match the current date,
        if there are birthdays today returns a list of dictionaires, each dictionary containing the twitter username, 'user',
        and their age, 'age'.
        if there are no birthdays returns a empty list"""

        today = datetime.date(datetime.now())
        birthdays = []
        with open('birthday/birthdays.json', 'r') as file:
            try:
                data = json.load(file)['birthdays']
            except KeyError:
                return birthdays
            else:
                for user, birthday in data.items():

                    year, month, day = birthday.split('-')
                    bday = date(int(year), int(month), int(day))

                    if bday.day == today.day and bday.month == today.month:
                        age = round((today - bday).days/365)
                        birthdays.append({'user': user, 'age': age})
        return birthdays
