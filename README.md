## USC CSCI572 HW2 - Web Crawling
#### Name: Aiyu Zhang
#### USD ID: 8524183902

This news crawler is implemented using Scrapy.
CONCURRENT_REQUESTS in setting.py is recorded as the number of threads in the crawl report.

*** 
### NOTIFICATION: CHANGE OF TARGET SITE

Due to being blocked by NY Times (which is my assigned site), I crawled LA Times instead.
***
### USAGE
To run the crawler, first install Scrapy, then open a terminal window in this directory. 
Enter the follow commands in the terminal to run the spider.

To crawl a generic news site with the domain "www.{newssitename}.com":
```
scrapy crawl news -a sitename={newssitename}
```
To crawl NY Times: 
```
scrapy crawl news -a sitename=nytimes
```
To crawl Wall Street Journal: 
```
scrapy crawl news -a sitename=wsj
```
To crawl Fox News: 
```
scrapy crawl news -a sitename=foxnews
```
To crawl USA Today: 
```
scrapy crawl news -a sitename=usatoday
```
To crawl LA Times: 
```
scrapy crawl news -a sitename=latimes
```