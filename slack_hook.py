"""
Forms slack message and post it to slack.
"""
from dotenv import Dotenv
import json
import os
import logging
import requests

dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
os.environ.update(dotenv)
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL')

if not SLACK_WEBHOOK_URL:
    raise RuntimeError('SLACK_WEBHOOK_URL must be present in environment')


def send_slack_notification(username, attachments):
    logging.info("Sending message to {}".format(username))
    logging.info("attachments {}".format(attachments))
    payload = {
        "channel": '@' + username,
        "username": "Rally Bot",
        "icon_emoji": ":rallystinks:",
        "text": "Here is the list of defects/tasks assigned to you in current itteration",
        "attachments": attachments
    }

    response = requests.post(
        SLACK_WEBHOOK_URL,
        data=json.dumps(payload)
    )

    if response.status_code != 200:
        logging.error("Error sending slack message: {}".format(response.text))
