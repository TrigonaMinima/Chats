library(ggplot2)
library(scales)
library(plyr)


# Reading the dataset.
d <- read.csv("final_all_chats.csv")
d$date <- as.POSIXct(d$date, format="%d/%m/%Y")
d$time <- as.POSIXct(d$time, format="%I:%M:%S %p")
d <- subset(d, date > "2012-01-01")

# d$time <- as.numeric(as.POSIXct(d$time, format="%I:%M:%S %p"))
# d$time <- strptime(d$time, format="%I:%M:%S %p")
# d$time[d$time == as.POSIXct("12:00:00 am", format="%I:%M:%S %p")] <- as.POSIXct("11:59:00 pm", format="%I:%M:%S %p")


# Getting all the dates not in the dataset.
dates_present <- format(unique(d$date), format="%Y-%m-%d")
dates_absent <- seq(as.Date("2012-01-01"), as.Date(Sys.Date()), by=1)
dates_absent <- format(dates_absent, format="%Y-%m-%d")
dates <- setdiff(dates_absent, dates_present)
dates <- as.POSIXct(dates, format="%Y-%m-%d")
dates <- data.frame(date=dates)

# Updating dataset with the dates not present in it.
d <- merge(d, dates, by="date", all=T)

# My replies only
myd <- subset(d, name == "Shivam Rana" | is.na(time))

# My daily sent messages
mydaily_d <- count(myd, 'date')
mydaily_d$freq[mydaily_d$date %in% dates$date] <- 0

# My monthly avg friends I replied to
myunique <- count(subset(count(myd, c('date', 'cat')), select=-freq), 'date')
myunique$month <- months(myunique$date)
myunique$year <- format(myunique$date, format="%Y")
myunique$freq[myunique$date %in% dates$date] <- 0

myunique <- aggregate(freq ~ month + year, myunique, FUN=mean)
myunique$date <- as.POSIXct(paste("1", myunique$month, myunique$year), format="%d %B %Y")

# Incoming and outgoing messages, monthly averages
mydaily <- count(myd, c('date', 'cat'))
mydaily$freq[mydaily$date %in% dates$date] <- 0
mydaily <- aggregate(freq ~ date, mydaily, FUN=mean)    # Daily avg
mydaily$month <- months(mydaily$date)
mydaily$year <- format(mydaily$date, format="%Y")
mydaily <- aggregate(freq ~ month + year, mydaily, FUN=mean)  # Monthly Avg
mydaily$date <- as.POSIXct(paste("1", mydaily$month, mydaily$year), format="%d %B %Y")

others <- subset(d, name != "Shivam Rana" | is.na(time))
othersdaily <- count(others, c('date', 'cat'))
othersdaily$freq[othersdaily$date %in% dates$date] <- 0
othersdaily <- aggregate(freq ~ date, othersdaily, FUN=mean)    # Daily avg
othersdaily$month <- months(othersdaily$date)
othersdaily$year <- format(othersdaily$date, format="%Y")
othersdaily <- aggregate(freq ~ month + year, othersdaily, FUN=mean)  # Monthly avg
othersdaily$date <- as.POSIXct(paste("1", othersdaily$month, othersdaily$year), format="%d %B %Y")