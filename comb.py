import pandas as pd
import os

from config import fb_data_dir, whatsapp_data_dir


def combine(data_dir):
    csvs = sorted(os.listdir(data_dir))
    csv_data = pd.read_csv(data_dir + csvs[0])
    print(csvs[0])

    for csv in csvs[1:]:
        print(csv)
        new_d = pd.read_csv(data_dir + csv)
        csv_data = pd.concat([csv_data, new_d], ignore_index=True)

    return csv_data.drop_duplicates()


if __name__ == "__main__":
    data = combine(fb_data_dir)
    data.to_csv("./FB/all_chats.csv", index=False)

    data2 = combine(whatsapp_data_dir)
    data2.to_csv("./WhatsApp/all_chats.csv", index=False)

    data = pd.concat([data, data2], ignore_index=True)
    del data["data"]
    data.to_csv("final_all_chats.csv", index=False)

    data[data.name == "Shivam Rana"].to_csv("final_my_chats.csv", index=False)
