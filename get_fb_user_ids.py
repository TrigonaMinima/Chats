import requests
import time

headers = {
    'Origin': 'http://findmyfbid.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36 Vivaldi/1.1.453.52',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Referer': 'http://findmyfbid.com/',
    'Connection': 'keep-alive',
    'DNT': '1'
}


def fetch(username):
    """ Getting userids from Facebook given usernames. """

    FB_URL = "https://facebook.com/" + username
    response = requests.post("http://findmyfbid.com/",
                             headers=headers, data={"url": FB_URL})

    id_data = response.content.decode("utf8")

    return id_data[id_data.find("<code>") + 6:id_data.find("</code>")]


if __name__ == "__main__":
    with open("FB/usernames.txt", "r") as f:
        usernames = [name.strip("\n").split("  ") for name in f.readlines()]

    if not usernames:
        print("Error: No or empty usernames file in 'FB/'")
        exit()

    ids = open("FB/ids.csv", "a")
    ids.write("id,name\n")

    usernames = dict(usernames)
    for friend in usernames:
        try:
            usernames[friend] = fetch(usernames[friend])
        except:
            time.sleep(30)
            usernames[friend] = fetch(usernames[friend])

        ids.write(usernames[friend] + "," + friend + "\n")
        print(friend, usernames[friend])

    # print(usernames)

    ids.close()

    print("Truncating the usernmes file from directory 'FB/'")
    file = open("FB/usernames.txt", "w")
    file.close()
