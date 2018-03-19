import pandas as pd

from pathlib import Path
from bs4 import BeautifulSoup as bs4

from config import fb_dir, fb_raw_dir, fb_clean_dir


class FBRaw(object):
    """
    Reads the raw chat files, extracts data from the raw files and
    creates a datafrafre from the extracted data.
    """

    def read_raw_data(self, file):
        """
        Reads the raw HTML files from the facebook data dump.
        """
        self.file = file
        with open(file, "r", encoding="utf8") as f:
            soup = bs4(f, "html.parser")
        print("\tData read!")
        return soup

    def clean_reply(self, reply):
        """
        Utility function. Cleans the BS4 elements, extracting the text.
        """
        if reply.string is None:
            if reply.find() is None:
                reply = ""
            else:
                reply = reply.find()
        else:
            reply = reply.string.strip()
        return reply

    def clean_user(self, username):
        """
        Utility function. Cleans the BS4 elements, extracting the text.
        """
        if username.string is None:
            username = "Facebook User"
        else:
            username = username.string.strip()
        return username

    def extract_data(self, lines):
        """
        Extracts the username, timestamp, replies from the raw data.
        """
        data = {}
        data["PERSON"] = lines.title.string[18:]

        thread = lines.body.find("div", class_="thread")

        timestamps = thread.find_all("span", class_="meta")
        timestamps = [timestamp.string.strip() for timestamp in timestamps]
        data["TIMESTAMPS"] = timestamps

        replies = thread.find_all('p', recursive=False)
        # print(replies)
        # print(replies[0])
        if replies[0].find() and replies[0].find().get("class", [""])[0] == "warning":
            replies = replies[1:]

        replies = list(map(self.clean_reply, replies))
        data["TEXT"] = replies

        users = thread.find_all("span", class_="user")
        users = list(map(self.clean_user, users))
        data["FROM"] = users

        print("\tData extracted!")
        return data

    def to_dataframe(self, data):
        """
        Turns into a datafrmame structure.
        """
        df_dict = {
            "DATETIME": data["TIMESTAMPS"],
            "FROM": data["FROM"],
            "TEXT": data["TEXT"]
        }
        df = pd.DataFrame(df_dict)
        df = df.dropna(how="all")
        # df.TEXT = df.TEXT.str.strip()
        df["PERSON"] = data["PERSON"]

        df.DATETIME = pd.to_datetime(df.DATETIME)

        print("\tDataframe made!")
        return df


class TSFB(FBRaw):
    """
    Handles the time formatting of the data.
    """
    time_dict = {}

    def time_division_dict(self, group_sizes):
        """
        Utility function
        """
        time_dict = {}
        for group_size in group_sizes:
            interval = pd.Timedelta(60, "s") / group_size
            reply_time = interval / 2

            times = []
            for i in range(group_size):
                times.append(reply_time)
                reply_time += interval
            time_dict[group_size] = times
        return time_dict

    def time_division(self, group_sizes):
        """
        Utility function.
        """
        times = []
        for group_size in group_sizes:
            group_times = self.time_dict[group_size]
            times += group_times
        return times

    def handling_time(self, df):
        """
        FB HTML files don't have second component in the timestamps.
        It checks the count of replies within a minute, distributes it into
        equal intervals and then assigns the time to each reply.
        """
        dt_grps = df.groupby(["DATETIME"])
        dt_grp_sizes = dt_grps.size()
        self.time_dict = self.time_division_dict(dt_grp_sizes.unique())
        time_deltas = self.time_division(dt_grp_sizes)

        df.DATETIME = df.DATETIME + time_deltas
        print("\tTime handled.")
        return df

    def add_datetime(self, df):
        """
        Makes a Datetime column from the timestamp column.
        """
        df["DATETIME"] = df.DATE.str.cat(df.TIME, sep=" ")
        df.DATETIME = pd.to_datetime(df.DATETIME)
        print("\tDatetime added.")
        return df


class FB(TSFB):
    """
    Wrapper class on the WhatsAppRaw and TSWhatsApp classes.
    """

    def __init__(self):
        """
        Initializes the FB data directory paths.
        """
        self.fb_dir = fb_dir
        self.fb_raw = fb_raw_dir
        self.fb_clean = fb_clean_dir
        self.file = ""

    def save_data(self, df):
        """
        Saves the individual chat files as clean CSVs.
        """
        clean_file = (self.fb_clean / self.file.name).with_suffix(".csv")
        df = df.drop_duplicates()
        df.to_csv(clean_file, index=False)
        print("\tSaved:", clean_file)

    def combine(self):
        """
        Combines all the individual chat files into 1
        """
        dfs = []
        for file in sorted(self.fb_clean.glob("*")):
            df = pd.read_csv(file)
            df["PLATFORM"] = "FB"
            dfs.append(df)

        all_chats = pd.concat(dfs,  ignore_index=True)
        all_chats = all_chats.drop_duplicates()

        all_chats_file = self.fb_dir / "all_chats.csv"
        all_chats.to_csv(all_chats_file, index=False)
        print("\nCombined all FB chats.")


if __name__ == "__main__":
    fb = FB()

    for file in fb.fb_raw.glob("*"):
        print(file)
        raw_data = fb.read_raw_data(file)
        line_split = fb.extract_data(raw_data)
        filedf = fb.to_dataframe(line_split)
        filedf = fb.handling_time(filedf)
        fb.save_data(filedf)

    fb.combine()
