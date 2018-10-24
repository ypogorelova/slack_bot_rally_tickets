"""
Generates slack message for people listed in people.csv file with the list of Rally
tickets assigned to him.
Uses query criteria for filtering tickets:
creteria Owner.UserName = {owner} AND STATE >= "Submitted" AND STATE != "Closed"
AND Iteration.StartDate <= today AND Iteration.EndDate >= today.
"""

# !/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import slack_hook
import people
import logging
from dotenv import Dotenv
from pyral import Rally

dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))  # replace by your correct path
os.environ.update(dotenv)
SERVER = os.environ.get('RALLY_SERVER')
USER = os.environ.get('RALLY_USER')
PASSWORD = os.environ.get('RALLY_PASSWORD')
PROJECTS = ''

rally = Rally(server=SERVER, user=USER, password=PASSWORD)


def queryRally(issue_type, state_start, state_end, owner=None):
    state_parameter = 'ScheduleState' if issue_type == 'User Story' else 'STATE'
    fields = "FormattedID,State,Name,LastUpdateDate,Owner.UserName"
    userQuery = 'Owner.UserName = {}'.format(owner)
    stateStartQuery = '{} >= {}'.format(state_parameter, state_start)
    stateEndQuery = '{} != {}'.format(state_parameter, state_end)
    iterSDQuery = 'Iteration.StartDate <= today'
    iterEDQuery = 'Iteration.EndDate >= today'

    criterion = '{} AND {} AND {} AND {} AND {}'.format(userQuery, stateStartQuery,
                                                        stateEndQuery, iterSDQuery, iterEDQuery)
    logging.debug("creteria {} for issue {}".format(criterion, issue_type))

    response = rally.get(entity=issue_type, fetch=fields, query=criterion,
                         order="LastUpdateDate Desc", pagesize=200, limit=400)
    return response if response.resultCount > 0 else None


def format_attachment(issue, project_id, issue_type):
    if issue_type == 'userstory':
        state = "Is not Accepted"
    else:
        state = issue.State
    return {
        'text': "ID: {}\n State: {}\nLastUpdated: {}".format(
            issue.FormattedID,
            state,
            issue.LastUpdateDate
        ),
        'title': issue.Name,
        'title_link': "https://rally1.rallydev.com/#/{}/"
                      "detail/{}/{}".format(project_id, issue_type, issue.oid)
    }


def send_messages(filename):
    p = people.People(filename)
    users = p.get_users()
    for user in users:
        rally_user = user.rally
        crm_proj = rally.getProject(name=PROJECTS)
        tasks = queryRally(
            issue_type='Task', owner=rally_user, state_start='Defined', state_end='Completed'
        )
        logging.info("Tasks {}".format(tasks))
        defects = queryRally(
            issue_type='Defect', owner=rally_user, state_start='Submitted', state_end='Closed'
        )
        logging.info("Defects {}".format(defects))
        user_stories = queryRally(
            issue_type='User Story', owner=rally_user, state_start='Defined', state_end='Accepted'
        )
        logging.info("User Stories {}".format(user_stories))

        attachments = []
        if tasks:
            for task in tasks:
                attachment = format_attachment(task, crm_proj.oid, 'task')
                attachments.append(attachment)

        if defects:
            for defect in defects:
                attachments.append(format_attachment(defect, crm_proj.oid, 'defect'))

        if user_stories:
            for user_story in user_stories:
                attachments.append(format_attachment(user_story, crm_proj.oid, 'userstory'))

        slack_hook.send_slack_notification(user.slack, attachments)

if __name__ == "__main__":
    # UTC timezone
    logging.basicConfig(level=logging.DEBUG, filename="logfile", filemode="a+",
                        format="%(asctime)-15s %(levelname)-8s %(message)s")
    send_messages('people.csv')
