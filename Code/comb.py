import pandas as pd
import os

from config import fb_dir, wp_dir, data_dir


def combine(data_dir):
    csvs = sorted(os.listdir(data_dir))
    csv_data = pd.read_csv(data_dir + csvs[0])
    print(csvs[0])

    for csv in csvs[1:]:
        print(csv)
        new_d = pd.read_csv(data_dir + csv)
        csv_data = pd.concat([csv_data, new_d], ignore_index=True)

    return csv_data.drop_duplicates()


def upload(data):
    pass


if __name__ == "__main__":
    wp_file = wp_dir / "all_chats.csv"
    all_wp = pd.read_csv(wp_file)
    print("WhatsApp data read!")

    fb_file = fb_dir / "all_chats.csv"
    all_fb = pd.read_csv(fb_file)
    print("Facebook data read!")

    all_file = data_dir / "all_chats.csv"
    all_chats = pd.concat([all_wp, all_fb], ignore_index=True)
    all_chats.to_csv(all_file, index=False)
    print("Final data saved!")

    upload(all_chats)
    print("Final data uploaded!")
