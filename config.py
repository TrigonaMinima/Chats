# Set the value you see in 'Form Data'
form_data = {
    "__a": "",
    "__dyn": "",
    "__req": "",
    "__rev": "",
    "__user": "",
    "client": "",
    "fb_dtsg": "",
    "ttstamp": ""
}

headers = {
    # Set the value you see in 'Request Headers'
    "cookie": "",
    # You don't have to modify these, but feel free to.
    "accept": "*/*",
    "accept-encoding": "gzip,deflate",
    "accept-language": "en-US,en;q=0.8",
    "cache-control": "no-cache",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://www.facebook.com",
    "pragma": "no-cache",
    "referer": "https://www.facebook.com/messages/zuck",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.122 Safari/537.36"
}

csv_header = ["date", "time", "name", "cat", "data"]

# Other constants
whatsapp_data_dir = "./WhatsApp/clean_data/"
fb_data_dir = "./FB/clean_data/"
fb_dir = "./FB"
user_ids = "./FB/ids.csv"
user_ids_final = "./FB/meta/ids.csv"
