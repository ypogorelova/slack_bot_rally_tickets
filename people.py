"""
Match Rally user to slack user.
"""
import os.path
import csv


class User:
    def __init__(self, slack, rally):
        self.slack = slack
        self.rally = rally


class People:
    def __init__(self, filename):
        self.users = []

        people = csv.DictReader(
            open(
                os.path.join(os.path.dirname(__file__), filename),
                'r'
            )
        )

        for person in people:
            slack = person.get('slack')
            rally = person.get('rally')
            if rally and slack:
                self.users.append(User(slack, rally))

    def get_users(self):
        return self.users
