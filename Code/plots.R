# Loads libraries and data
source("load.R")


# Creating the scatter plot
start <- as.POSIXct("00:00 am", format="%H:%M %p")
end <- start + as.difftime(24, unit="hours")
interval <- 120
breaks <- seq(from=start, by=interval * 60, to=end)
labels <- format(breaks, "%I:%M %p")

jpeg("mychats.jpeg", width = 7, height = 4, units = "in", res = 300)
g <- ggplot(myd, aes(x=date, y=time)) +
  geom_point(size=0.05, colour='brown') +
  theme_bw() +
  scale_y_datetime(breaks = breaks, labels = labels) +
  theme(legend.position="none") +
  xlab("") +
  ylab("") +
  theme(panel.grid.minor = element_blank())
print(g)
dev.off()
graphics.off()
print("'myshats.jpeg' is saved.")


# Daily msg count plot
jpeg("daily.jpeg", width = 12, height = 4, units = "in", res = 300)
x = min(mydaily_d$date) + as.difftime(1, units="days")
y = max(mydaily_d$freq)

g <- ggplot(mydaily_d, aes(x=date, y=freq)) +
  geom_bar(stat="identity", fill="#E69F00") +
  theme_bw() +
  scale_y_continuous(breaks=seq(0, 500, 100)) +
  xlab("") +
  ylab("") +
  annotate("text", label = "Daily sent messages", x = x, y = y, size = 5, colour = "grey50", hjust=0, vjust=1) +
  theme(panel.grid.minor = element_blank())
print(g)
dev.off()
graphics.off()
print("'daily.jpeg' is saved.")


# Get mean unique friends per month
jpeg("friends.jpeg", width = 12, height = 4, units = "in", res = 300)
x = min(myunique$date) + as.difftime(1, units="days")
y = max(myunique$freq)

g <- ggplot(myunique, aes(date, freq)) +
  geom_line(colour="orange2") +
  geom_area(fill="orange", alpha=0.5) +
  theme_bw() +
  xlab("") +
  ylab("") +
  annotate("text", label = "Mean unique friends per month", x = x, y = y, size = 5, colour = "grey50", hjust=0, vjust=1) +
  scale_y_continuous(breaks=seq(0, round(max(myunique$freq)) + 1, 2)) +
  theme(panel.grid.minor = element_blank())
print(g)
dev.off()
graphics.off()
print("'friends.jpeg' is saved.")


# Incoming and outgoing msgs (monthly)
jpeg("monthly.jpeg", width = 12, height = 4, units = "in", res = 300)
x = min(othersdaily$date) + as.difftime(1, units="days")
y = max(othersdaily$freq)

g <- ggplot(othersdaily, aes(x=date, y=freq)) +
  geom_area(fill='orange1', alpha=0.5) +
  geom_line(colour='orange2') +
  geom_area(data=mydaily, aes(x=date, y=freq), alpha=0.5, fill="orange1") +
  geom_line(data=mydaily, aes(x=date, y=freq), colour='orange2') +
  theme_bw() +
  labs(x="", y="") +
  annotate("text", label = "Monthly incoming and outgoing avg messages", x = x, y = y, size = 5, colour = "grey50", hjust=0, vjust=1)
print(g)
dev.off()
graphics.off()
print("'monthly.jpeg' is saved.")
