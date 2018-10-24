Slack bot that reminds to update Rally tasks. Generates slack message for people listed in people.csv file with the list of open Rally tickets assigned to him.
Uses query criteria for filtering tickets:
criteria Owner.UserName = {owner} AND STATE >= "Submitted" AND STATE != "Closed" AND Iteration.StartDate <= today AND Iteration.EndDate >= today.
Sends message directly to every user. Can be used to notify team members to make changes in Rally before daily standup.
To include new person to the mailing list add him to people.csv file.

Run Script
===========

To run script you need to have Python 2 installed. Then do the following:

* `pip install -r requirements.txt`
* Copy .env-sample to .env (it's git-ignored) and fill values for keys in .env
* Run scripts `python <script name>`
