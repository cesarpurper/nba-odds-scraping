# nba-odds-scraping

This project is a simple scraper to scrape initial and end NBA odds from the website https://www.scoresandodds.com/

## Next steps

- refactoring the code that gets data from the table to better handle the game table behaviours
- studying more about the game details tab and parse data from the detail request as well(in the details tab is possible to get info about formation, minutes played, full line movements, etc)

## How to run it

The spider receives two parameters as arguments
- initial_date = the initial date the spider will start scraping
- end_date = the date the spider will end scraping

and example command line would be 

```
scrapy crawl nbaoddsspider -a start_date=01/01/2022 -a end_date=16/06/2022 -o output.csv
```
