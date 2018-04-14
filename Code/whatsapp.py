import re
import pandas as pd

from config import wp_dir, wp_raw_dir, wp_clean_dir


# PATTERN: "20/07/16, 8:48 PM - "
ts_person_reg = re.compile(
    '\d{1,2}/\d{1,2}/\d{2,4}, \d?\d:\d\d [APap][Mm] +- +[\w ]+:')
ts_reg = re.compile('\d{1,2}/\d{1,2}/\d{2,4}, \d?\d:\d\d [APap][Mm] +-')
group_reg = "(\d{1,2}/\d{1,2}/\d{2,4}), (\d?\d:\d\d [APap][Mm]) +- +([\w ]+):"


class WhatsAppRaw(object):
    """
    Reads the raw chat files, extracts data from the raw files and
    creates a datafrafre from the extracted data.
    """

    def read_raw_data(self, file):
        """
        Reads the raw chat files.
        """
        self.file = file
        with open(file, "r") as f:
            lines = f.readlines()

        data = []
        for line in lines:
            line = line.strip()
            if re.search(ts_person_reg, line):
                data.append(line)
            elif re.search(ts_reg, line) or not line:
                continue
            else:
                data[-1] = data[-1].strip() + ". " + line
        print("\tRaw data read!")
        return data

    def extract_data(self, lines):
        """
        Transforms the raw data into a structured format.
        """
        data = []
        for line in lines:
            data.append(re.split(group_reg, line)[1:])
        print("\tData read!")
        return data

    def to_dataframe(self, lines):
        """
        Converts into dataframe.
        """
        columns = ["DATE", "TIME", "FROM", "TEXT"]
        df = pd.DataFrame(lines, columns=columns)
        df.TEXT = df.TEXT.str.strip()

        df = df.dropna(how="all")

        person = cat = re.sub(
            r"[\(-.].*", "", self.file.name[:-4]).strip()
        df["PERSON"] = person
        print("\tDataframe made!")
        return df


class TSWhatsApp(WhatsAppRaw):
    """
    Handles the time formatting of the data.
    """
    time_dict = {}

    def time_division_dict(self, group_sizes):
        """
        Utility function.
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
        Whatsapp text files don't have second component in the timestamps.
        It checks the count of replies within a minute, distributes it into
        equal intervals and then assigns the time to each reply.
        """
        dt_grps = df.groupby(["DATE", "TIME"])
        dt_grp_sizes = dt_grps.size()
        self.time_dict = self.time_division_dict(dt_grp_sizes.unique())
        time_deltas = self.time_division(dt_grp_sizes)

        df["TIME"] = pd.to_datetime(df.TIME, format="%I:%M %p") + time_deltas
        df["TIME"] = df.TIME.apply(lambda x: x.strftime("%I:%M:%S %p"))
        print("\tTime handled.")
        return df

    def add_datetime(self, df):
        """
        Makes a Datetime column from date and time columns.
        """
        df["DATETIME"] = df.DATE.str.cat(df.TIME, sep=" ")
        df.DATETIME = pd.to_datetime(
            df.DATETIME, format="%d/%m/%Y %I:%M:%S %p")

        df = df[["DATETIME", "FROM", "TEXT", "PERSON"]]
        print("\tDatetime added.")
        return df

    def complete_years(self, df):
        """
        Completes 2 digit years into 4 digits.
        """
        df.DATE = df.DATE.apply(lambda x: re.sub(r'\/(\d\d)$', "/20\\1", x))
        print("\tYears completed.")
        return df


class WhatsApp(TSWhatsApp):
    """
    Wrapper class on the WhatsAppRaw and TSWhatsApp classes.
    """

    def __init__(self):
        """
        Initializes the whatsapp data directory paths.
        """
        self.wp_dir = wp_dir
        self.wp_raw = wp_raw_dir
        self.wp_clean = wp_clean_dir
        self.file = ""

    def save_data(self, df):
        """
        Saves the individual chat files as clean CSVs.
        """
        clean_file = (self.wp_clean / self.file.name).with_suffix(".csv")
        df = df.drop_duplicates()
        df.to_csv(clean_file, index=False)
        print("\tSaved:", clean_file)

    def combine(self):
        """
        Combines all the individual chat files into 1
        """
        dfs = []
        for file in sorted(self.wp_clean.glob("*")):
            df = pd.read_csv(file)
            df["PLATFORM"] = "WP"
            dfs.append(df)

        all_chats = pd.concat(dfs,  ignore_index=True)
        all_chats = all_chats.drop_duplicates()

        all_chats_file = self.wp_dir / "all_chats.csv"
        all_chats.to_csv(all_chats_file, index=False)
        print("\nCombined all WP chats.")


if __name__ == "__main__":
    wp = WhatsApp()

    for file in wp.wp_raw.glob("*"):
        print(file)
        raw_data = wp.read_raw_data(file)
        line_split = wp.extract_data(raw_data)
        filedf = wp.to_dataframe(line_split)
        filedf = wp.complete_years(filedf)
        filedf = wp.handling_time(filedf)
        filedf = wp.add_datetime(filedf)
        wp.save_data(filedf)

    wp.combine()
