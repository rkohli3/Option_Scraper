# NASDAQ and Barchart Options chain Scraper

The modules in the following repo contain python scripts for scraping options data from
NASDAQ and Barchart sites. Both, NASDAQ and Barchart provide real time data, but do not come without any trade offs.

<p>
<br>
<br>

## Summary
<br>
<br>   
### Barchart
<p>
Barchart uses Ajax, ie it loads all data whenever the site is requested. Therefore, if there are multiple pages to get data from,
one does not have to `request` for those multiple pages each time. However, Barchart has some missing data, which you may/may not
get from NASDAQ.

### NASDAQ
<p>
Unlike Barchart, NASDAQ pages need to be called each time. For eg. if AMZN has multiple pages for its Options chain, then each pages
needs to be called separately. This implies, too mnay request hits.

## Implementation and dependencies

The modules use BeautifulSoup from bs4 module. Very powerful tool for web scraping. To install the dependencies, type the following
commands in terminal

```bash
~Ravi$ pip install tqdm
~Ravi$ pip install bs4
~Ravi$ pip install urllib
```
Once you install the dependencies. Open the folder via terminal (cmd for Windows) and run the file BarChartOptions.py. For example, if the folder is saved in Desktop

```bash
~Ravi$ cd Desktop/FolderName
~Ravi$ python BarChartOptions.py
```
