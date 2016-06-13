Chats
=====


This repository contains the code to get the chat data of facebook chats (individuals as well as groups). There are also some files to convert all the data into csvs and finally, an R file to make static ggplot2 plots.


## Dependencies

pandas (Python)
requests (Python)

ggplot2 (R)
scales (R)


## Usage

In your ``config.py``, fill the form data and the cookie's value in the header. If you dont know how to get those values then, go to the facebook.com/messages and open your browser's dev tools. Click on any friend to view the messages in the window and in the "network" tab click the first request your borwser sent. Copy the form data a cookie in the ``config.py``. You're are set.

Run the files in the following order.

```
# Handling FB data first (1)
python get_fb_user_ids.py
python get_fb_messages.py
python output.py

# Handling WhatsApp data (2)
python structuring.py
bash timestamps.sh
python dtrans.py

# Combining both the data sets into one (3)
python comb.py

# To get the plots (4)
Rscript plots.R
```

(1) This part assumes there's a directory "FB" in the root directory of the project. In that directory it assumes there's a file called ``usernames.txt`` having FB friend name and their username separated by "2 spaces". It'll then create a new file called ``ids.txt`` aslongside usernames file. Copy that new ids file in a directory called "FB/meta" and copy the remaining friends with their ids (the friends who doesn't have usernames directly show the FB ID). In the case of group chats, in the messages window, their url will show the id as "conversation-<some_random_number>". Copy that random number only.

All, the fb chats will get into a directory called "FB/raw_data", where each directory will correspond to a friend. This, raw_data will be converted to individual CSVs by the ``output.py`` in a new directory, "FB/clean_data".

(2) This part assumes you have all the chats in individual text files in a directory called "WhatsApp/raw_data". File ``structuring.py`` will convert those multilined replies (having multiple '\n') into one. New directory will be created "WhatsApp/timestamps" where all the data will be in CSVs. Now, whatsapp timestamps had a little problem with them. There were no seconds part in the reply, but I needed that. So, ``dtrans.py`` takes care of that.

For example, if for 6 replies times were - 3:30 pm what I thought I shoud do is, cumulatively add 10 seconds (60/6 seconds) to each time. So, now times become, 3:30:00 pm, 3:30:10 pm, 3:30:20 pm, 3:30:30 pm, 3:30:40 pm, 3:30:50 pm. But now, there's no gap at the start and a lot of gap at the end. So instead, I made the time start after 5 seconds (10/2). So, the times that ``dtrans.py`` will give are - 3:30:05 pm, 3:30:15 pm, 3:30:25 pm, 3:30:35 pm, 3:30:45 pm, 3:30:55 pm. Now, there's 5 seconds gap at the start and 5 seconds gap at the end.

(3) The combined data will be saved in the individual directories ("FB" and "WhatsApp") and also as a single file in the root directory. There will be 2 csvs in the root - chats that were only sent by me and all the chats.

(4) The ``plots.R`` will save 4 jpegs in the root you can see the images included here to get an idea what will be generated.
