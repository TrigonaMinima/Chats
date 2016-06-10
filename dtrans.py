import os
import pandas as pd
import re

data_dir = "./WhatsApp/timestamps/"
csvs = sorted(os.listdir(data_dir))
count_times = {}


def times_transform(group):
    count = len(group)

    if count > 1:
        if not count_times.get(count, False):
            interval = pd.Timedelta(60, "s") / count
            sum_in = interval / 2

            times = []
            for i in range(count):
                times.append(sum_in)
                sum_in += interval
            count_times[count] = times

            group["new_time"] += times
        else:
            group["new_time"] += count_times[count]

    return group


def full_year_dates(timestamp):
    timestamp = timestamp.split("/")
    if len(timestamp[2]) != 4:
        timestamp[2] = "20" + timestamp[2]

    return "/".join(timestamp)


def clean_dataframe(df, filename):
    df.date = df.date.apply(full_year_dates)
    df.time = df.time.apply(lambda t: t.strip()).apply(
        lambda t: pd.Timestamp(t))
    df.name = df.name.apply(lambda t: t.strip())
    df["new_time"] = df.time

    return df


for csv in csvs:
    print(csv)
    dfs = []
    csv_data = pd.read_csv(data_dir + csv, header=None,
                           names=["date", "time", "name", "data"])
    dfs.append(csv_data)

    cdf = clean_dataframe(csv_data, csvs[0])
    dfs.append(cdf)

    new_d = cdf.groupby(["date", "time"]).transform(times_transform)
    new_d["date"] = cdf.date
    new_d.rename(columns={'new_time': 'time'}, inplace=True)
    new_d.time = new_d.time.apply(lambda x: x.strftime("%I:%M:%S %p"))

    cat = re.sub(r"[\(-.].*", "", csv).strip()
    new_d["cat"] = pd.Series([cat] * len(new_d))

    new_d.to_csv("./WhatsApp/clean_data/" + csv, index=False)

    dfs.append(new_d)
    del dfs
