library(ggplot2)
library(scales)
library(plyr)


# Reading the dataset.
file_path <- "/Almost700/Git/tminima/Mega Project/Chats/data/all_chats.csv"
d <- read.csv(file_path)
d$dt <- as.POSIXct(d$DATETIME)
d$DATE <- as.POSIXct(d$DATETIME, format="%Y-%m-%d")
d$TIME <- as.POSIXct(strftime(d$dt, format="%I:%M:%S %p"), format="%I:%M:%S %p")

# There are very few cases before 2012
d <- subset(d, DATE >= "2012-01-01")


# d$DATE <- as.POSIXct(d$DATE, format="%d/%m/%Y")
# d$TIME <- as.POSIXct(d$TIME, format="%I:%M:%S %p")
# d$TIME <- as.numeric(as.POSIXct(d$TIME, format="%I:%M:%S %p"))
# d$TIME <- strptime(d$TIME, format="%I:%M:%S %p")
# d$TIME[d$TIME == as.POSIXct("12:00:00 am", format="%I:%M:%S %p")] <- as.POSIXct("11:59:00 pm", format="%I:%M:%S %p")


# Getting all the dates not in the dataset.
# dates_present <- format(unique(d$DATE), format="%Y-%m-%d")
# dates_absent <- seq(as.Date("2012-01-01"), as.Date(Sys.Date()), by=1)
# dates_absent <- format(dates_absent, format="%Y-%m-%d")
# dates <- setdiff(dates_absent, dates_present)
# dates <- as.POSIXct(dates, format="%Y-%m-%d")
# dates <- data.frame(date=dates)

# Updating dataset with the dates not present in it.
# d <- merge(d, dates, by="date", all=T)


# My replies only
myd <- subset(d, FROM == "Shivam Rana")
# myd <- subset(d, name == "Shivam Rana" | is.na(time))

# My daily sent messages
mydaily_d <- count(myd, 'DATE')
# mydaily_d$freq[mydaily_d$DATE %in% dates$DATE] <- 0


# My monthly avg friends I replied to
myunique <- count(subset(count(myd, c('date', 'cat')), select=-freq), 'date')
myunique$month <- months(myunique$DATE)
myunique$year <- format(myunique$DATE, format="%Y")
myunique$freq[myunique$DATE %in% dates$DATE] <- 0

myunique <- aggregate(freq ~ month + year, myunique, FUN=mean)
myunique$DATE <- as.POSIXct(paste("1", myunique$month, myunique$year), format="%d %B %Y")

# Incoming and outgoing messages, monthly averages
mydaily <- count(myd, c('date', 'cat'))
mydaily$freq[mydaily$DATE %in% dates$DATE] <- 0
mydaily <- aggregate(freq ~ date, mydaily, FUN=mean)    # Daily avg
mydaily$month <- months(mydaily$DATE)
mydaily$year <- format(mydaily$DATE, format="%Y")
mydaily <- aggregate(freq ~ month + year, mydaily, FUN=mean)  # Monthly Avg
mydaily$DATE <- as.POSIXct(paste("1", mydaily$month, mydaily$year), format="%d %B %Y")

others <- subset(d, name != "Shivam Rana" | is.na(time))
othersdaily <- count(others, c('date', 'cat'))
othersdaily$freq[othersdaily$DATE %in% dates$DATE] <- 0
othersdaily <- aggregate(freq ~ date, othersdaily, FUN=mean)    # Daily avg
othersdaily$month <- months(othersdaily$DATE)
othersdaily$year <- format(othersdaily$DATE, format="%Y")
othersdaily <- aggregate(freq ~ month + year, othersdaily, FUN=mean)  # Monthly avg
othersdaily$DATE <- as.POSIXct(paste("1", othersdaily$month, othersdaily$year), format="%d %B %Y")
