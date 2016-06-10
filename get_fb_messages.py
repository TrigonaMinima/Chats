"""
Backup your entire facebook conversations.
Friend list is read from a config file.
"""

import json
import os
import requests
import sys
import time

from config import form_data, headers, user_ids


# Can be used to download a range of messages
limit = 2000

# Used to find the end of conversation thread
END_MARK = "end_of_history"

FB_URL = "https://www.facebook.com/ajax/mercury/thread_info.php"

ROOT = "FB/raw_data"


def mkdir(f):
    """ Create a directory if it doesn't already exist. """
    if not os.path.exists(f):
        os.makedirs(f)


def fetch(data):
    """ Fetch data from Facebook. """

    offset = [v for k, v in data.items() if 'offset' in k][0]
    limit = [v for k, v in data.items() if 'limit' in k][0]

    print("\t%6d  -  %6d" % (offset, offset + limit))

    try:
        response = requests.post(FB_URL, data=data, headers=headers)
    except:
        time.sleep(10)
        response = requests.post(FB_URL, data=data, headers=headers)

        # Account for 'for (;;);' in the beginning of the text.
    return response.content[9:]


if __name__ == '__main__':

    with open(user_ids, "r") as f:
        friends = [friend.strip("\n").split(",")
                   for friend in f.readlines()[1:]]

    friends = dict(friends)

    for friend_id, friend_name in friends.items():
        print("Retrieving Messages of: %s" % friend_name)

        # Setup data directory
        dirname = os.path.join(ROOT, friend_name.replace(" ", ""))
        mkdir(dirname)

        # These parameters need to be reset everytime
        offset = 0
        timestamp = 0
        data = {"payload": ""}

        # We want it ALL!
        while END_MARK not in data['payload']:
            # Form data for the PMs
            form_data["messages[user_ids][%s][offset]" % friend_id] = offset
            form_data["messages[user_ids][%s][limit]" % friend_id] = limit
            form_data["messages[user_ids][%s][timestamp]" %
                      friend_id] = str(timestamp)

            # Form data for the group chats
            form_data["messages[thread_fbids][%s][offset]" %
                      friend_id] = offset
            form_data["messages[thread_fbids][%s][limit]" % friend_id] = limit
            form_data["messages[thread_fbids][%s][timestamp]" %
                      friend_id] = str(timestamp)

            # print(json.dumps(form_data, indent=2))
            content = fetch(form_data)

            # Handle facebook rate limits
            print(len(content))
            while not content:
                print("Facebook Rate Limit Reached. Retrying after 30 secs")
                time.sleep(30)
                content = fetch(form_data)

            # Build JSON representation
            # print(content)
            data = json.loads(content.decode("utf8"))

            # Dump Data
            filename = "%s.json" % (limit + offset)
            with open(os.path.join(dirname, filename), "w") as op:
                json.dump(data, op, indent=2)

            # Next!
            offset = offset + limit
            timestamp = data['payload']['actions'][0]['timestamp']
            time.sleep(2)

        print("\t-----END-----")

        # Make the form_data usable for the next user
        form_data.pop("messages[user_ids][%s][offset]" % friend_id)
        form_data.pop("messages[user_ids][%s][limit]" % friend_id)
        form_data.pop("messages[user_ids][%s][timestamp]" % friend_id)

        # Make the form_data usable for the next group chat
        form_data.pop("messages[thread_fbids][%s][offset]" % friend_id)
        form_data.pop("messages[thread_fbids][%s][limit]" % friend_id)
        form_data.pop("messages[thread_fbids][%s][timestamp]" % friend_id)
