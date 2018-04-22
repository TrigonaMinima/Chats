Chats
=====

This repository contains the code to prepare the data and plots from the chat dumps (Facebook and Whatsapp). The subsequent blog posts are here 

- [Chatting Up](http://trigonaminima.github.io/quantified-self/facebook-data/2016/06/09/Chatting-Up/) (code for this part is not present here anymore, you can check the commit history to get it)
- [Chatting Up - Part II](http://trigonaminima.github.io/quantified-self/facebook-data/data-analysis/2018/04/22/Chatting-Up-Part-II/)


## Dependencies

- Python3.6
- pandas
- numpy
- seaborn
- matplotlib
- wordcloud
- scipy (optional)

## Usage

In your ``config.py``, change your base directory and make all the data directories and change the paths accordingly.

Run the files in the following order.

```
# Cleaning the data
python facebook.py
python whatsapp.py

# Combining both the data sets into one
python comb.py

# To get the plots
python save_plots.py
```

You'll get all the plots saved as jpeg in the ```Plots``` directory.

