import feedparser

NewsFeed = feedparser.parse("https://feeds.content.dowjones.io/public/rss/mw_topstories")
entry = NewsFeed.entries[1]

for k,v in entry.items():
    print("%s: %s" % (k,v))
