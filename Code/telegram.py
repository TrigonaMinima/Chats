import json
import datetime
import pandas as pd

from pathlib import Path

from config import tg_dir, tg_raw_dir, tg_clean_dir


class TGRaw(object):
    """
    Reads the raw chat files, extracts data from the raw files and
    creates a datafrafre from the extracted data.
    """

    def read_raw_data(self, file):
        """
        Reads the raw HTML files from the facebook data dump.
        """
        self.file = file
        lines = []
        with open(file, "r", encoding="utf8") as f:
            for line in f:
                msg_dict = json.loads(line)
                lines.append(msg_dict)

        print("\tData read!")
        return lines

    def extract_data(self, lines):
        """
        Extracts the username, timestamp, replies from the raw data
        Note that, every column is reversed (using [::-1]), that's because,
        in FB data dumps, the most recent message comes first and I wanted
        to keep it in chronological order.
        """
        data = {
            "DATETIME": [],
            "FROM": [],
            "TEXT": [],
            "PERSON": [],
        }

        for line in lines:
            # print(line)

            dt = datetime.datetime.fromtimestamp(line["date"])
            dt = dt.strftime("%Y-%m-%d %H:%M:%S")
            data["DATETIME"].append(dt)

            try:
                data["TEXT"].append(line["text"])
            except:
                data["TEXT"].append("<media>")

            if line["to"]["peer_type"] == "user":
                fname = line["to"]["first_name"].strip()
                lname = line["to"]["last_name"].strip()
                data["PERSON"].append(f"{fname} {lname}")
            else:
                data["PERSON"].append(line["to"]["title"])

            fname = line["from"]["first_name"].strip()
            lname = line["from"]["last_name"].strip()
            data["FROM"].append(f"{fname} {lname}")

        print("\tData extracted!")
        return data

    def to_dataframe(self, data):
        """
        Turns into a datafrmame structure.
        """
        df = pd.DataFrame(data)
        df = df.dropna(how="all")
        df.DATETIME = pd.to_datetime(df.DATETIME)

        print("\tDataframe made!")
        return df


class TG(TGRaw):
    """
    Wrapper class on the WhatsAppRaw and TSWhatsApp classes.
    """

    def __init__(self):
        """
        Initializes the FB data directory paths.
        """
        self.tg_dir = tg_dir
        self.tg_raw = tg_raw_dir
        self.tg_clean = tg_clean_dir
        self.file = ""

    def save_data(self, df):
        """
        Saves the individual chat files as clean CSVs.
        """
        clean_file = (self.tg_clean / self.file.name).with_suffix(".csv")
        df = df.drop_duplicates()
        df.to_csv(clean_file, index=False)
        print("\tSaved:", clean_file)

    def combine(self):
        """
        Combines all the individual chat files into 1
        """
        dfs = []
        for file in sorted(self.tg_clean.glob("*")):
            df = pd.read_csv(file)
            df["PLATFORM"] = "Telegram"
            dfs.append(df)

        all_chats = pd.concat(dfs,  ignore_index=True)
        all_chats = all_chats.drop_duplicates()

        all_chats_file = self.tg_dir / "all_chats.csv"
        all_chats.to_csv(all_chats_file, index=False)
        print("\nCombined all Telegram chats.")


if __name__ == "__main__":
    tg = TG()

    for file in tg.tg_raw.glob("*"):
        print(file)
        raw_data = tg.read_raw_data(file)
        line_split = tg.extract_data(raw_data)
        filedf = tg.to_dataframe(line_split)
        tg.save_data(filedf)

    tg.combine()
