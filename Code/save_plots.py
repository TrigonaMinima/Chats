import datetime
import numpy as np
import pandas as pd

from pathlib import Path
from collections import Counter
from scipy.stats import chisquare
from scipy.special import factorial

# For pLotting purposes
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from wordcloud import WordCloud
from pandas.plotting import parallel_coordinates


my_name = "Shiavm Rana"

# Plot directory
plot_dir = Path("../Plots")

# Data Loading
file_path = Path("../data/all_chats.csv")
data = pd.read_csv(file_path)

# Filtering out the null text rows
data = data.loc[~data.TEXT.isnull(), :]

# Converion of datetime str to python datetime object
data["DATETIME"] = data["DATETIME"].astype('datetime64[s]')

# Columns from DATETIME field
# data["DATE"] = data.DATETIME.dt.date.astype('datetime64') - wasn't
# helping with plotting
data["DATE"] = pd.to_datetime(data.DATETIME.dt.date)
data["TIME"] = pd.to_datetime(data.DATETIME.dt.time, format='%H:%M:%S')
data["YEAR"] = data.DATETIME.dt.year
data["MONTH"] = data.DATETIME.dt.month
data["MONTHYR"] = data.YEAR.astype(str).str.cat(
    data.MONTH.astype(str).str.zfill(2), sep="-")
data["HOUR"] = data.DATETIME.dt.hour
data["DAY"] = data.DATETIME.dt.weekday_name.str[:3]
data["DATEHRMIN"] = data.DATETIME.dt.strftime("%d%m%Y%H%M")

# Text length
data["TLEN"] = data.TEXT.str.len()

# Standardizing the names.
# You will need to prepare this dict for your puroses
# Key is the "name to standardize" and the value if the "standard name".
frnd_dict = {
}

for frnd in frnd_dict:
    data.loc[data.FROM == frnd, "FROM"] = frnd_dict[frnd]
    data.loc[data.PERSON == frnd, "PERSON"] = frnd_dict[frnd]

# Adding names where we had the string "Facebook User"
# You'll need to make a list of names where the FROM field is "Facebook User"
for frnd in []:
    data.loc[(data.PERSON == frnd) & (
        data.FROM == "Facebook User"), "FROM"] = frnd

# Adding group flag
# This might not handle all the cases. For the reamining ones you'll need to
# find out the pattern yourself.
groups = data.groupby("PERSON", as_index=False).agg(
    {"FROM": ["nunique", lambda x: 1 if (x == my_name).any() else 0]})

cond1 = (groups["FROM"]["nunique"] > 2) & (groups["FROM"]["<lambda>"] == 1)
cond2 = (groups["FROM"]["nunique"] > 1) & (groups["FROM"]["<lambda>"] == 0)
groups = groups[cond1 | cond2].PERSON.values
data["GRPFLG"] = data.PERSON.apply(lambda x: 1 if x in groups else 0)

# Facebook groupnames where not name was set contains the
# string " and "
cond1 = data.PERSON.astype(str).apply(
    lambda x: True if " and " in x.lower() else False)
data.loc[cond1 | cond2, "GRPFLG"] = 1

# Adding time difference between replies
data = data.sort_values(["PERSON", "DATETIME"]).reset_index(drop=True)
data["TDIFF"] = data['DATETIME'].diff() / np.timedelta64(1, 's')
data.loc[(data.PERSON != data.PERSON.shift(1)), 'TDIFF'] = np.nan

# Adding time difference For the user NaN :(
cond = (data.TDIFF.isnull()) & (data.PERSON.isnull())
data.loc[cond, "TDIFF"] = data.loc[
    cond, "DATETIME"].diff() / np.timedelta64(1, 's')

# New pings per day - threshold of 8 hrs
time_threshold = 8 * 60 * 60
cond1 = data.TDIFF > time_threshold
cond2 = data.TDIFF.isnull()
data.loc[:, "STARTS"] = (cond1 | cond2).astype(int)
data.loc[:, "ENDS"] = data.STARTS.shift(-1)
data.loc[data.STARTS == 1, "TDIFF"] = np.nan


sent_messages = data[data.FROM == my_name]
recv_messages = data[data.FROM != my_name]
non_group_data = data[data.GRPFLG == 0]


#
# Daily Plot
#
# There are very few texts before 2012 which were distorting the plot.
# So, filtered those rows out.
filter_data = data[data.DATE > '2012-01-01']

# Plotting the scater plot
fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(
    15, 8), gridspec_kw={'height_ratios': [6, 1]})
ax.plot_date(
    filter_data.DATE,
    filter_data.TIME,
    ms=0.8,
    color="#f39c12"
)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.yaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))

# Formatting the tick labels right
start = datetime.datetime(1900, 1, 1, 0)
time_ticks = [start + datetime.timedelta(hours=i * 2) for i in range(13)]
time_ticks = time_ticks[8:] + time_ticks[:8]
time_labels = [i.strftime("%I:%M %p") for i in time_ticks]

ax.set_yticks(time_ticks)
ax.set_yticklabels(time_labels)
ax.grid(b=True, which='major', linestyle='-', alpha=0.2)  # color='b',

# Start and end of College
ax.axvspan("2012-07-15", "2016-05-16", facecolor='#f5cba7', alpha=0.5)
ax.text(
    "2014-06-01", datetime.datetime(1900, 1, 2, 0, 29),
    "College Life",
    ha="center", va="center",
    size=12,
)

# Professional life
ax.axvspan("2016-06-26", "2017-02-28", facecolor='#a9dfbf', alpha=0.5)
ax.axvspan("2017-03-06", "2018-03-06", facecolor='#a9dfbf', alpha=0.5)
ax.text(
    "2017-06-01", datetime.datetime(1900, 1, 2, 0, 29),
    "Professional Life",
    ha="center", va="center",
    size=12,
)


all_dates = pd.DataFrame(index=pd.date_range("2011-09-24", "2018-07-01"))
temp = data.groupby("DATE").agg({"TEXT": "count", "TLEN": "count"})
temp = all_dates.join(temp)

# https://stackoverflow.com/a/45349235/2650427
dnum = mdates.date2num(temp.index.to_pydatetime())
start = dnum[0] - (dnum[1] - dnum[0]) / 2.
stop = dnum[-1] + (dnum[1] - dnum[0]) / 2.
extent = [start, stop, -0.5, 0.5]

# fig, ax = plt.subplots(figsize=(15, 1))
im = ax2.imshow(
    temp.T,
    aspect="auto",
    extent=extent,
    cmap=sns.cubehelix_palette(light=1, as_cmap=True)
    # cmap=sns.dark_palette("palegreen", as_cmap=True, reverse=True)
)
ax2.xaxis.set_major_locator(mdates.YearLocator())
# ax2.xaxis.set_minor_locator(mdates.MonthLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax2.set_yticks([])
ax2.set_yticklabels([])

filepath = plot_dir / "daily_timestamp.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Hour plot and Weekday plot
#
hour_wise = data.groupby("HOUR", as_index=False).agg(
    {"TEXT": "count"}).sort_values(by="HOUR")
hour_wise_sent = sent_messages.groupby("HOUR", as_index=False).agg(
    {"TEXT": "count"}).sort_values(by="HOUR")
hour_wise_recv = recv_messages.groupby("HOUR", as_index=False).agg(
    {"TEXT": "count"}).sort_values(by="HOUR")

fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(15, 2.5))

hour_wise.plot(x="HOUR", y="TEXT", kind="area",
               ax=ax1, color="#f4d03f", alpha=0.6)
ax1.legend().set_visible(False)
ax1.set_title("Hour wise total count", loc="left")


day_dict = pd.DataFrame({"ORDER": [1, 2, 3, 4, 5, 6, 7]}, index=[
                        "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
year_df = data.DAY.value_counts()
year_df = pd.concat([year_df, day_dict], axis=1).sort_values(by="ORDER")
del year_df["ORDER"]

year_df.plot(kind="bar", ax=ax2, color="#82e0aa", edgecolor="#1e8449")
ax2.set_title("Day of the week wise total count", loc="left")
ax2.legend().set_visible(False)
plt.xticks(rotation=0)

filepath = plot_dir / "hour_weekday.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Yearly
#
fig, ax = plt.subplots(figsize=(15, 3))

yearly = data.groupby("YEAR").agg(
    {"TEXT": "count"}).rename(columns={"TEXT": "TOTAL"})
yearly = yearly.join(sent_messages.groupby("YEAR").agg(
    {"TEXT": "count"})).rename(columns={"TEXT": "SENT"})
yearly = yearly.join(recv_messages.groupby("YEAR").agg(
    {"TEXT": "count"})).rename(columns={"TEXT": "RECV"})

yearly.plot(y="TOTAL", ax=ax, kind="area", color="#f6ddcc", alpha=0.9)
yearly.plot(y="RECV", ax=ax, kind="area", color="#dc7633", alpha=0.4)
yearly.plot(y="SENT", ax=ax, kind="area", color="#a04000", alpha=0.4)

ax.set_title("Yearly distribution of texts", loc="left")
ax.set_xlabel("")

filepath = plot_dir / "yearly.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Monthly
#
fig, ax = plt.subplots(figsize=(15, 3))

monthly = data.groupby("MONTHYR").agg(
    {"TEXT": "count"}).rename(columns={"TEXT": "TOTAL"})
monthly = monthly.join(sent_messages.groupby("MONTHYR").agg(
    {"TEXT": "count"})).rename(columns={"TEXT": "SENT"})
monthly = monthly.join(recv_messages.groupby("MONTHYR").agg(
    {"TEXT": "count"})).rename(columns={"TEXT": "RECV"})
monthly.index = pd.to_datetime(monthly.index, format="%Y-%m")

monthly.plot(y="TOTAL", ax=ax, kind="area", color="#aed6f1", alpha=0.9)
monthly.plot(y="RECV", ax=ax, kind="area", color="#3498db", alpha=0.4)
monthly.plot(y="SENT", ax=ax, kind="area", color="#2e86c1", alpha=0.4)

ax.set_title("Monthly text distribution", loc="left")
ax.set_xlabel("")
plt.xticks(rotation=0, ha="center")

filepath = plot_dir / "monthly.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Yearly-Hourly
#
years = sorted(data.YEAR.unique())[::-1][:-2]

nrows = 3
ncols = 3
fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                         figsize=(12, 6), sharex=True, sharey=True)

for i, year in enumerate(years):
    year_df = non_group_data[non_group_data.YEAR == year]
    hour_wise = year_df.groupby("HOUR", as_index=False).agg(
        {"TEXT": "count"}).sort_values(by="HOUR")

    ax = plt.subplot(nrows, ncols, i + 1)
    hour_wise.plot(x="HOUR", y="TEXT", kind="area",
                   ax=ax, color="#2ecc71", alpha=0.6)
    ax.legend().set_visible(False)
    plt.title(year)
    plt.xlabel("")

while i + 1 < nrows * ncols:
    fig.delaxes(plt.subplot(nrows, ncols, i + 2))
    i += 1

fig.tight_layout()

filepath = plot_dir / "yearly_hourly.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Cumulative
#
daily_cum = data[
    data.DATE >= "2012-01-01"].groupby("DATE").agg({"TEXT": "count"}).cumsum(axis=0)
in_daily_cum = recv_messages[
    recv_messages.DATE >= "2012-01-01"].groupby("DATE").agg({"TEXT": "count"}).cumsum(axis=0)
out_daily_cum = sent_messages[
    sent_messages.DATE >= "2012-01-01"].groupby("DATE").agg({"TEXT": "count"}).cumsum(axis=0)

fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 4.5))

daily_cum.plot(ax=ax)
in_daily_cum.plot(ax=ax)
out_daily_cum.plot(ax=ax)
ax.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax.legend(["TOTAL", "INCOMING", "OUTGOING"])
ax.set_xlabel("")

# Start and end of College
ax.axvspan("2012-07-15", "2016-05-16", facecolor='#f5cba7', alpha=0.5)
ax.text(
    "2014-06-01", 300000,
    "College Days",
    ha="center", va="center",
    size=12,
    alpha=0.6
)

# Professional life
ax.axvspan("2016-06-26", "2017-02-28", facecolor='#a9dfbf', alpha=0.5)
ax.axvspan("2017-03-06", "2018-03-06", facecolor='#a9dfbf', alpha=0.5)
ax.text(
    "2017-06-01", 300000,
    "Professional Life",
    ha="center", va="center",
    size=12,
    alpha=0.6
)
ax.set_title("Cumulative reply count", loc="left")
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0d'))
plt.xticks(rotation=0, ha="center")
plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha="center")


daily_cum = data[
    data.DATE >= "2012-01-01"].groupby("DATE").agg({"TLEN": "sum"}).cumsum(axis=0)
in_daily_cum = recv_messages[
    recv_messages.DATE >= "2012-01-01"].groupby("DATE").agg({"TLEN": "sum"}).cumsum(axis=0)
out_daily_cum = sent_messages[
    sent_messages.DATE >= "2012-01-01"].groupby("DATE").agg({"TLEN": "sum"}).cumsum(axis=0)

daily_cum.plot(ax=ax2)
in_daily_cum.plot(ax=ax2)
out_daily_cum.plot(ax=ax2)
ax2.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax2.legend(["TOTAL", "INCOMING", "OUTGOING"])
ax2.set_xlabel("")

# Start and end of College
ax2.axvspan("2012-07-15", "2016-05-16", facecolor='#f5cba7', alpha=0.5)
ax2.text(
    "2014-06-01", 9200000,
    "College Days",
    ha="center", va="center",
    size=12,
    alpha=0.6
)

# Professional life
ax2.axvspan("2016-06-26", "2017-02-28", facecolor='#a9dfbf', alpha=0.5)
ax2.axvspan("2017-03-06", "2018-03-06", facecolor='#a9dfbf', alpha=0.5)
ax2.text(
    "2017-06-01", 9200000,
    "Professional Life",
    ha="center", va="center",
    size=12,
    alpha=0.6
)
ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%0.0d'))
ax2.set_title("Cumulative reply size", loc="left")
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0, ha="center")

filepath = plot_dir / "cumulative.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Monthly avg friends
#
fig, ax = plt.subplots(figsize=(15, 4))

monthyrs = pd.DataFrame(index=np.unique(
    pd.date_range("2011-01", "2018-03").strftime("%Y-%m")))
monthly = pd.DataFrame(non_group_data[non_group_data.FROM != my_name]
                       .groupby("MONTHYR")
                       .apply(lambda x: round(x.groupby("DATE").PERSON.nunique().sum() / x.DATE.unique().shape[0])))
monthly = monthyrs.join(monthly)
monthly.index = pd.to_datetime(monthly.index, format="%Y-%m")
monthly = monthly.replace(np.nan, 0)

monthly.plot(y=0, kind="area", ax=ax, color="#e74c3c", alpha=0.5)
plt.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax.legend().set_visible(False)
ax.set_title("Monthly avg of unique friends", loc="left")


# Start and end of College
ax.axvspan("2012-07-15", "2016-05-16", facecolor='#fdedec', alpha=0.4)
ax.text(
    "2014-06-01", 9,
    "College Days",
    ha="center", va="center",
    size=12,
)

# Professional life
ax.axvspan("2016-06-26", "2018-03-06", facecolor='#fdedec', alpha=0.4)
ax.text(
    "2017-05-01", 9,
    "Professional Life",
    ha="center", va="center",
    size=12,
)

filepath = plot_dir / "monthly_avg_friends.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Name masking
#
data["PERSON_ORIG"] = data.PERSON

# the masking dict.
# key is "name to be masked" and value is the "mask value"
masks = {
}
for mask in masks:
    data.loc[(data.PERSON == mask), "PERSON"] = masks[mask]

sent_messages = data[data.FROM == my_name]
recv_messages = data[data.FROM != my_name]
non_group_data = data[data.GRPFLG == 0]


# Data Prep
top_n = pd.DataFrame({"PERSON": non_group_data.PERSON.unique()})

# Total unique days
top_n_total_days = non_group_data.groupby("PERSON", as_index=False)\
    .agg({"DATE": "nunique"}).rename(columns={"DATE": "UNIQ_DAYS"})\
    .sort_values(by="UNIQ_DAYS", ascending=False)
top_n = top_n.merge(top_n_total_days, on="PERSON")

# Total text count (mine and friend's)
top_n_total = non_group_data.groupby("PERSON", as_index=False)\
    .agg({"TEXT": "count"}).rename(columns={"TEXT": "TCNT"})\
    .sort_values(by="TCNT", ascending=False)
top_n = top_n.merge(top_n_total, on="PERSON")

# Total text count of friend
top_n_in = non_group_data[non_group_data.FROM != my_name]\
    .groupby("PERSON", as_index=False)\
    .agg({"TEXT": "count"}).rename(columns={"TEXT": "TCNT_FRIEND"})\
    .sort_values(by="TCNT_FRIEND", ascending=False)
top_n = top_n.merge(top_n_in, on="PERSON")

# Total text length (mine and friend's)
top_n_total_len = non_group_data.groupby("PERSON", as_index=False)\
    .agg({"TLEN": pd.np.sum})\
    .sort_values(by="TLEN", ascending=False)
top_n = top_n.merge(top_n_total_len, on="PERSON")

# Total lenght of text of friend's replies
top_n_in_len = non_group_data[non_group_data.FROM != my_name]\
    .groupby("PERSON", as_index=False)\
    .agg({"TLEN": pd.np.sum}).rename(columns={"TLEN": "TLEN_FRIEND"})\
    .sort_values(by="TLEN_FRIEND", ascending=False)
top_n = top_n.merge(top_n_in_len, on="PERSON")

# Mean length of text per reply (averagine over total reply count)
top_n_mean_len = non_group_data.groupby("PERSON", as_index=False)\
    .agg({"TLEN": "mean"}).rename(columns={"TLEN": "MLEN"})\
    .sort_values(by="MLEN", ascending=False)
top_n = top_n.merge(top_n_mean_len, on="PERSON")

# Mean length of text per reply (averaging over friend's reply count)
top_n_in_mean_len = non_group_data[non_group_data.FROM != my_name]\
    .groupby("PERSON", as_index=False)\
    .agg({"TLEN": "mean"}).rename(columns={"TLEN": "MLEN_FRIEND"})\
    .sort_values(by="MLEN_FRIEND", ascending=False)
top_n = top_n.merge(top_n_in_mean_len, on="PERSON")

# Mean length of text per reply (averaging over my reply count)
top_n_out_mean_len = non_group_data[non_group_data.FROM == my_name]\
    .groupby("PERSON", as_index=False)\
    .agg({"TLEN": "mean"}).rename(columns={"TLEN": "MLEN_ME"})\
    .sort_values(by="MLEN_ME", ascending=False)
top_n = top_n.merge(top_n_out_mean_len, on="PERSON")

# My rate of replying per minute
my_reply_rate = non_group_data[non_group_data.FROM == my_name]\
    .groupby("PERSON").apply(lambda x: x.TEXT.shape[0] / len(x.DATEHRMIN.unique()))\
    .reset_index(level=0).rename(columns={0: "MYRRT"})
top_n = top_n.merge(my_reply_rate, on="PERSON")

# Friend's rate of replying per minute
frnd_reply_rate = non_group_data[non_group_data.FROM != my_name]\
    .groupby("PERSON").apply(lambda x: x.TEXT.shape[0] / len(x.DATEHRMIN.unique()))\
    .reset_index(level=0).rename(columns={0: "FRNDRRT"})
top_n = top_n.merge(frnd_reply_rate, on="PERSON")

# Mean length of text per unique day
mean_text_per_day = non_group_data.groupby("PERSON")\
    .apply(lambda x: x.TLEN.sum() / x.DATE.unique().shape[0])\
    .reset_index(level=0).rename(columns={0: "MLENDAY"})
top_n = top_n.merge(mean_text_per_day, on="PERSON")

# Mean length of text of friend per unique day
friend_mean_text_per_day = non_group_data[non_group_data.FROM != my_name]\
    .groupby("PERSON").apply(lambda x: x.TLEN.sum() / x.DATE.unique().shape[0])\
    .reset_index(level=0).rename(columns={0: "MLENDAY_FRIEND"})
top_n = top_n.merge(friend_mean_text_per_day, on="PERSON")

# Mean length of text of friend per unique day
my_mean_text_per_day = non_group_data[non_group_data.FROM == my_name]\
    .groupby("PERSON").apply(lambda x: x.TLEN.sum() / x.DATE.unique().shape[0])\
    .reset_index(level=0).rename(columns={0: "MLENDAY_ME"})
top_n = top_n.merge(my_mean_text_per_day, on="PERSON")

# Mean count of text per unique day
mean_cnt_per_day = non_group_data.groupby("PERSON")\
    .apply(lambda x: x.TEXT.shape[0] / x.DATE.unique().shape[0])\
    .reset_index(level=0).rename(columns={0: "TCNTDAY"})
top_n = top_n.merge(mean_cnt_per_day, on="PERSON")

# Mean count of text of friend per unique day
friend_cnt_text_per_day = non_group_data[non_group_data.FROM != my_name]\
    .groupby("PERSON").apply(lambda x: x.TEXT.shape[0] / x.DATE.unique().shape[0])\
    .reset_index(level=0).rename(columns={0: "TCNTDAY_FRIEND"})
top_n = top_n.merge(friend_cnt_text_per_day, on="PERSON")

# Mean count of text of friend per unique day
my_mean_cnt_per_day = non_group_data[non_group_data.FROM == my_name]\
    .groupby("PERSON").apply(lambda x: x.TEXT.shape[0] / x.DATE.unique().shape[0])\
    .reset_index(level=0).rename(columns={0: "TCNTDAY_ME"})
top_n = top_n.merge(my_mean_cnt_per_day, on="PERSON")

# Mean replpy delay
mean_reply_delay = non_group_data.groupby("PERSON").agg({"TDIFF": "mean"})\
    .reset_index(level=0)
top_n = top_n.merge(mean_reply_delay, on="PERSON")

# WP texts
wp_count = non_group_data.groupby("PERSON").agg({"PLATFORM": lambda x: (x == "WP").sum()})\
    .reset_index(level=0).rename(columns={"PLATFORM": "WP"})
top_n = top_n.merge(wp_count, on="PERSON")

# FB texts
fb_count = non_group_data.groupby("PERSON").agg({"PLATFORM": lambda x: (x == "FB").sum()})\
    .reset_index(level=0).rename(columns={"PLATFORM": "FB"})
top_n = top_n.merge(fb_count, on="PERSON")


#
# Top n friends by total unique days
#
n = 20
temp = top_n.loc[:, ["PERSON", "UNIQ_DAYS"]].sort_values(
    by="UNIQ_DAYS", ascending=False).head(n)

fig, ax = plt.subplots(figsize=(15, 4))
temp.plot(x="PERSON", y="UNIQ_DAYS", kind="bar", ax=ax,
          color="#f7dc6f", edgecolor='#f39c12', alpha=0.6)
ax.axhline(y=365, color="#dc7633", linewidth=0.5)
ax.text(n - 1.7, 365 + 10, "365 days", alpha=0.6)

ax.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax.set_title(f"Top {n} friends by total unique days", loc="left")
ax.set_xlabel("")
plt.sca(ax)
plt.xticks(rotation=35)
ax.legend().set_visible(False)

filepath = plot_dir / "top_n_unique_days.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n friends by conversations
#
n = 20
conv_starts = non_group_data.groupby("PERSON").STARTS.sum()
conv_starts_me = non_group_data[
    non_group_data.FROM == my_name].groupby("PERSON").STARTS.sum()
conv_starts_others = non_group_data[
    non_group_data.FROM != my_name].groupby("PERSON").STARTS.sum()

temp = pd.concat([conv_starts, conv_starts_me, conv_starts_others], axis=1)
temp.columns = ["CONVERSATIONS", "CONV_STRT_ME", "CONV_STRT_FRND"]
temp = temp.sort_values("CONVERSATIONS", ascending=False).head(n)

fig, ax = plt.subplots(figsize=(15, 5))
temp[["CONV_STRT_FRND", "CONV_STRT_ME"]].plot(
    kind="bar", ax=ax, color=["#f39c12", "#fdebd0"],
    edgecolor='#f39c12', label="Started by me", stacked=True
)

for i, (j, k) in enumerate(zip(temp.CONV_STRT_FRND, temp.CONVERSATIONS)):
    ax.text(i, j - 25, f"{round(j*100/k)}%", ha="center", va="center", color="#943126")

for i, (j, k) in enumerate(zip(temp.CONV_STRT_ME, temp.CONVERSATIONS)):
    if i in [9, 10, 12, 15, 16, 19]:
        ax.text(i, k + 20, f"{round(j*100/k)}%", ha="center", va="center", color="#943126")
    else:
        ax.text(i, k - 25, f"{round(j*100/k)}%", ha="center", va="center", color="#943126")

ax.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax.set_title(f"Top {n} friends by conversations", loc="left")
ax.set_xlabel("")
plt.sca(ax)
plt.xticks(rotation=35)
ax.legend(["Started by friend", "Started by me"])


filepath = plot_dir / "top_n_conversations.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n friends by texts
#
n = 20
temp = top_n.loc[:, ["PERSON", "TCNT", "TCNT_FRIEND"]
                 ].sort_values(by="TCNT", ascending=False).head(n)

fig, (ax, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(15, 11))
temp.plot(x="PERSON", y="TCNT", kind="bar", ax=ax, color="#aed6f1",
          edgecolor='#3498db', label="Outgoing", alpha=0.4)
temp.plot(x="PERSON", y="TCNT_FRIEND", kind="bar", ax=ax,
          color="#3498db", edgecolor='#3498db', label="Incoming")

for i, (j, k) in enumerate(zip(temp.TCNT_FRIEND, temp.TCNT)):
    ax.text(i, j - 1500, f"{round(j*100/k)}%", ha="center", va="center", color="#212f3d")

for i, (j, k) in enumerate(zip(temp.TCNT_FRIEND, temp.TCNT)):
    if i in list(range(11, n)):
        ax.text(i, k + 1500, f"{round((k-j)*100/k)}%", ha="center", va="center", color="#154360")
    else:
        ax.text(i, k - 1500, f"{round((k-j)*100/k)}%", ha="center", va="center", color="#154360")

ax.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax.set_title(f"Top {n} friends by texts (incoming and outgoing)", loc="left")
plt.sca(ax)
plt.xticks(rotation=35)
ax.set_xlabel("")
ax.legend()


n = 20
temp = top_n.loc[:, ["PERSON", "TLEN", "TLEN_FRIEND"]
                 ].sort_values(by="TLEN", ascending=False).head(n)

temp.plot(x="PERSON", y="TLEN", kind="bar", ax=ax2, color="#aed6f1",
          edgecolor='#3498db', label="Outgoing", alpha=0.4)
temp.plot(x="PERSON", y="TLEN_FRIEND", kind="bar", ax=ax2,
          color="#3498db", edgecolor='#3498db', label="Incoming")

for i, (j, k) in enumerate(zip(temp.TLEN_FRIEND, temp.TLEN)):
    ax2.text(i, j - 37000, f"{round(j*100/k)}%", ha="center", va="center", color="#212f3d")

for i, (j, k) in enumerate(zip(temp.TLEN_FRIEND, temp.TLEN)):
    if i in list(range(11, n)):
        ax2.text(i, k + 37000, f"{round((k-j)*100/k)}%", ha="center", va="center", color="#154360")
    else:
        ax2.text(i, k - 37000, f"{round((k-j)*100/k)}%", ha="center", va="center", color="#154360")

ax2.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax2.set_title(f"Top {n} friends by text length (incoming and outgoing)", loc="left")
ax2.set_xlabel("")
plt.sca(ax2)
plt.xticks(rotation=35)
ax2.legend()

fig.subplots_adjust(hspace=0.25)

filepath = plot_dir / "top_n_texts.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n friends by mean text length
#
n = 20
top_n_friends = top_n.sort_values(by="TCNT", ascending=False).PERSON.values[:n]
temp = top_n.loc[:, ["PERSON", "MLEN_FRIEND", "MLEN_ME"]]
cond = temp.PERSON.apply(lambda x: True if x in top_n_friends else False)
temp = temp.loc[cond].head(n).sort_values(by="MLEN_FRIEND", ascending=False)
temp.index = temp.PERSON

fig, ax = plt.subplots(figsize=(15, 4))
temp.loc[:, ["MLEN_FRIEND", "MLEN_ME"]].plot.bar(
    ax=ax, color=["#52be80", "#f5b041"], alpha=0.6, edgecolor=[])

ax.grid(b=True, which='major', linestyle='-', alpha=0.2)
ax.set_title(f"Top {n} friends by mean text length", loc="left")
ax.set_xlabel("")
plt.sca(ax)
plt.xticks(rotation=35)
ax.legend(["FRIEND", "MYSELF"])

filepath = plot_dir / "top_n_mean_text_length.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n friends yearly
#
yearly_parallel = non_group_data.pivot_table(
    index="PERSON", columns="YEAR", values="TEXT", aggfunc="count").reset_index(level=0)

# mask names list you want to display in the plot
friends = []
temp = yearly_parallel.loc[yearly_parallel.PERSON.isin(
    friends), ["PERSON"] + list(range(2012, 2019))]

color_sequence = [
    '#1f77b4', '#dbdb8d', '#ff7f0e', '#27ae60', '#9edae5',
    '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
    '#8c564b', '#c49c94', '#ffbb78', '#f7b6d2', '#7f7f7f',
    '#c7c7c7', '#bcbd22', '#aec7e8', '#2ca02c', '#e377c2'
]

fig, ax = plt.subplots(figsize=(15, 6))
parallel_coordinates(temp, "PERSON", ax=ax, lw=2.5,
                     color=color_sequence[:len(friends)])

ax.spines['top'].set_visible(True)
ax.spines['bottom'].set_visible(False)
ax.spines['right'].set_visible(True)
ax.spines['left'].set_visible(False)
ax.set_title("Text count based yearly ranking", loc="left")


filepath = plot_dir / "top_n_yearly_length.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n friends yearly 2
#
yearly_parallel = non_group_data.pivot_table(
    index="PERSON", columns="YEAR", values="DATE", aggfunc="nunique").reset_index(level=0)

# mask names list you want to display in the plot
friends = []
temp = yearly_parallel.loc[yearly_parallel.PERSON.isin(
    friends), ["PERSON"] + list(range(2012, 2019))]

fig, ax = plt.subplots(figsize=(15, 6))
parallel_coordinates(temp, "PERSON", ax=ax, lw=2.5,
                     color=color_sequence[:len(friends)])

ax.spines['top'].set_visible(True)
ax.spines['bottom'].set_visible(False)
ax.spines['right'].set_visible(True)
ax.spines['left'].set_visible(False)
ax.set_title("Unique days based yearly ranking", loc="left")
# ax.legend().set_visible(False)

filepath = plot_dir / "top_n_yearly_uniq_days.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n friends yearly 2
#
yearly_parallel1 = non_group_data.pivot_table(
    index="PERSON", columns="YEAR", values="TLEN", aggfunc="sum")
yearly_parallel2 = non_group_data.pivot_table(
    index="PERSON", columns="YEAR", values="DATE", aggfunc="nunique")
yearly_parallel = (yearly_parallel1 / yearly_parallel2).reset_index(level=0)

# mask names list you want to display in the plot
friends = []
temp = yearly_parallel.loc[yearly_parallel.PERSON.isin(
    friends), ["PERSON"] + list(range(2012, 2019))]


fig, ax = plt.subplots(figsize=(15, 6))
parallel_coordinates(temp, "PERSON", ax=ax, lw=2.5,
                     color=color_sequence[:len(friends)])

ax.spines['top'].set_visible(True)
ax.spines['bottom'].set_visible(False)
ax.spines['right'].set_visible(True)
ax.spines['left'].set_visible(False)
ax.set_title("Avg text length per unique day based yearly ranking", loc="left")
# ax.legend().set_visible(False)

filepath = plot_dir / "top_n_yearly_avg_len_uniq_days.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n normalized
#
cols = [
    'PERSON',
    'TCNT',
    #     'TCNT_FRIEND',
    'TLEN',
    #     'TLEN_FRIEND',
    "WP", "FB",
    "MYRRT", "FRNDRRT",
    'UNIQ_DAYS',
    #     'MLEN_FRIEND',
    #     'MLEN_ME',
    "TDIFF",
    "TCNTDAY",
    'MLENDAY',
    #     "TCNTDAY_FRIEND",
    #     'MLENDAY_FRIEND',
    #     "TCNTDAY_ME",
    #     'MLENDAY_ME',
]
# mask names list you want to display in the plot
friends = []
temp = top_n.loc[top_n.PERSON.isin(friends), cols].sort_values(
    by="TCNT", ascending=False)
temp.loc[:, temp.columns[1:]] = (temp.loc[:, temp.columns[
                                 1:]] - temp.loc[:, temp.columns[1:]].mean()) / temp.loc[:, temp.columns[1:]].std()

color_sequence = [
    '#1f77b4', '#dbdb8d', '#ff7f0e', '#27ae60', '#9edae5',
    '#98df8a', '#d62728', '#ff9896', '#9467bd', '#c5b0d5',
    '#8c564b', '#c49c94', '#ffbb78', '#f7b6d2', '#7f7f7f',
    '#c7c7c7', '#bcbd22', '#aec7e8', '#2ca02c', '#e377c2'
]

fig, ax = plt.subplots(figsize=(15, 5))
parallel_coordinates(temp, "PERSON", ax=ax, lw=2.5,
                     color=color_sequence[:len(friends)])

ax.set_xticklabels(
    ["Total texts\nsent/received",
     # "Total texts\nsentby\nfriend",
     "Total length\nof text\nsent/received",
     # "Total length\nof text\nsent by friend",
     "WhatsApp", "Facebook",
     "My reply\nrate (texts\nper min)", "Friend's reply\nrate (texts\nper min)",
     "No. of\nunique days\nof conversations",
     # "Mean length of\ntext sent\nby friend",
     # "Mean length\nof text\nI sent",
     "Avg delay\nbetween\nreplies",
     "Total texts\nper unique\nday (sent\n/received)",
     'Mean text\nlength per\nunique day',
     # "Total texts\nper unique\ndays sent\nby friend",
     # 'Mean text\nlength of\nfriend per\nunique day',
     # "Total texts\nper unique\ndays sent\nby me",
     # 'Mean text\nlength I\nsent per\nunique day',
     ]
)

ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.set_title("Normalized relative ranking", loc="left")
ax.legend().set_visible(False)

for pos, disptext in zip(temp.MLENDAY, temp.PERSON):
    if disptext == "Duffer":
        pos -= 0.05
    elif disptext == "Noor":
        pos += 0.05
    ax.text(9 + 0.04, pos, disptext)

fig.subplots_adjust(left=.06, right=.75, bottom=.02, top=.94)
plt.grid(True, 'major', 'y', ls='--', lw=.5, c='k', alpha=.3)

filepath = plot_dir / "top_n_normalized.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n heatmap
#
n = 20
all_dates = pd.DataFrame(index=pd.date_range(
    "2012-01-01", non_group_data.DATE.max()))

daily_stacked_count = non_group_data.pivot_table(
    index="DATE", columns="PERSON", values="TEXT", aggfunc="count")
daily_stacked_count = all_dates.join(daily_stacked_count)
top_n_friends = top_n.sort_values(by="TCNT", ascending=False).PERSON.values[:n]
daily_stacked_count = daily_stacked_count[top_n_friends]

daily_stacked_tlen = non_group_data.pivot_table(
    index="DATE", columns="PERSON", values="TLEN", aggfunc="sum")
daily_stacked_tlen = all_dates.join(daily_stacked_tlen)
top_n_friends = top_n.sort_values(by="TCNT", ascending=False).PERSON.values[:n]
daily_stacked_tlen = daily_stacked_tlen[top_n_friends]


temp = daily_stacked_count.copy(deep=True)

# https://stackoverflow.com/a/45349235/2650427
dnum = mdates.date2num(temp.index.to_pydatetime())
start = dnum[0] - (dnum[1] - dnum[0]) / 2.
stop = dnum[-1] + (dnum[1] - dnum[0]) / 2.
extent = [start, stop, -0.5, len(temp.columns) - 0.5]

fig, ax = plt.subplots(figsize=(15, 5))
im = ax.imshow(
    temp.T,
    vmax=500,
    aspect="auto", extent=extent,
    cmap=sns.dark_palette("palegreen", as_cmap=True, reverse=True)
)
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_minor_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.set_yticks(range(len(temp.columns)))
ax.set_yticklabels(temp.columns.values[::-1])
# ax.set_title("Text count heatmap")
fig.colorbar(im)


filepath = plot_dir / "top_n_heatmap.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)


#
# Top n cumulative
#
n = 10
top_n_friends = top_n.sort_values(by="TCNT", ascending=False).PERSON.values[:n]
len(top_n_friends)

nrows = 5
ncols = 4
fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                         figsize=(14, 14), sharex=True, sharey=True)

for i, frnd in enumerate(top_n_friends):
    frnd_df = non_group_data[non_group_data.PERSON == frnd]
    frnd_df_cum = frnd_df.groupby("DATE").agg({"TEXT": "count"}).cumsum(axis=0)
    frnd_df_cum_sent = frnd_df[frnd_df.FROM == my_name].groupby(
        "DATE").agg({"TEXT": "count"}).cumsum(axis=0)
    frnd_df_cum_recv = frnd_df[frnd_df.FROM != my_name].groupby(
        "DATE").agg({"TEXT": "count"}).cumsum(axis=0)

    ax = plt.subplot(nrows, ncols, i + 1)
    frnd_df_cum.plot(ax=ax)
    frnd_df_cum_recv.plot(ax=ax)
    frnd_df_cum_sent.plot(ax=ax)

    plt.grid(b=True, which='major', linestyle='-', alpha=0.2)
    plt.xlim(datetime.datetime(2012, 1, 1), non_group_data.DATE.max())
    plt.title(frnd)
    plt.legend(["TOTAL", frnd, my_name])
    plt.xlabel("")

while i + 1 < nrows * ncols:
    fig.delaxes(plt.subplot(nrows, ncols, i + 2))
    i += 1

# fig.suptitle("Cumulative message count")
fig.tight_layout()

filepath = plot_dir / "top_n_cumulative.jpeg"
fig.savefig(filepath.as_posix(), bbox_inches='tight')
plt.close(fig)
print("Saved the plot", filepath)
