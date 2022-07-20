import scrapy
import re
from datetime import datetime
import datetime

class ScoresAndOddsSpider(scrapy.Spider):
    name = 'nbaoddsspider'
    
    


    def start_requests(self):
        #self.start_date is passed as argument when the spider is called
        #the date format is day/month/year 17/12/2022
        seasonStartDate = datetime.datetime.strptime(self.start_date, "%d/%m/%Y")  
        #the page request pattern is 'nba?date=2022-04-06' with the date in american format
        pageUrl = "nba?date="+seasonStartDate.strftime("%Y-%m-%d")
        self.dateToScrape = seasonStartDate
        yield scrapy.Request(f'https://www.scoresandodds.com/{pageUrl}')


    def parse(self, response):

        #this function handle xpath selections wether they have value or not
        #when there is not value it is returned a empty string
        def getTextFromXpath(selector, xPath):
            dataExtracted = selector.xpath(xPath).extract()
            if len(dataExtracted) > 0:
                return dataExtracted[0].strip()
            return ""

        seasonEndDate = datetime.datetime.strptime(self.end_date, "%d/%m/%Y")

        containerDiv = getTextFromXpath(response, "//div[@class='container']")
        print(containerDiv != "")
        if containerDiv != "":
            for game in response.css('div.event-card'):

                
                #the extract function returns a list with all data selected by the xpath string
                #the game final status is the first string in the game table, it is FINAL to matches that are over, and POSTPONED to matches that were postponed
                gameStatus = game.xpath('table/thead/tr/th[1]/span[1]//text()').extract()[0]



                if gameStatus.casefold() != "POSTPONED".casefold():
                    homeTeam = game.css('span.team-name a span::text')[0].get()
                    awayTeam = game.css('span.team-name a span::text')[1].get()

                    homeTeamPts = game.css('td.event-card-score::text')[0].get()
                    awayTeamPts = game.css('td.event-card-score::text')[1].get()

                    homeTeamRecord = game.css('span.team-record::text')[0].get()
                    awayTeamRecord = game.css('span.team-record::text')[1].get()

                    homeTeamML= game.css('span.data-moneyline::text')[0].get()
                    awayTeamML= game.css('span.data-moneyline::text')[1].get()

                    
                    date = self.dateToScrape

                    odds = game.css('span.data-value::text')

                    #the page has a different behaviour depending on how the line moved and wich team is the home and away team
                    #to solve this and get the right data, this if checks if the first line is about team total spread or the regular point spread
                    #if it is team total in the first line of the game table the data would return as 'o228' or 'u228' meaning over/under 228
                    #if it is the regular points spread in the first line the data would return '-4' or '+4' for example
                    if bool(re.search("^[ou].*", odds[0].get().strip())) == False:

                        pointSpreadOpening = getTextFromXpath(game, 'table/tbody/tr[2]/td[3]/div/span//text()')
                        pointSpreadClosing = getTextFromXpath(game, 'table/tbody/tr[2]/td[5]/div/span//text()')
                        #this tries and excepts blocks are not good
                        #TODO refactor this part to better get date from the table and handle different table behaviours
                        try:
                            homeTeamSpreadOpening = float(getTextFromXpath(game, 'table/tbody/tr[1]/td[3]/div/span//text()'))
                            homeTeamSpreadClosing = float(getTextFromXpath(game, 'table/tbody/tr[1]/td[5]/div/span//text()'))

                            awayTeamSpreadOpening = homeTeamSpreadOpening * -1
                            awayTeamSpreadClosing = homeTeamSpreadClosing * -1
                        except:
                            homeTeamSpreadOpening = ""
                            homeTeamSpreadClosing = ""

                            awayTeamSpreadOpening = ""
                            awayTeamSpreadClosing = ""

                    else:       

                        pointSpreadOpening = getTextFromXpath(game, 'table/tbody/tr[1]/td[3]/div/span//text()')
                        pointSpreadClosing = getTextFromXpath(game, 'table/tbody/tr[1]/td[5]/div/span//text()')        

                        try:
                            awayTeamSpreadOpening = getTextFromXpath(game, 'table/tbody/tr[2]/td[3]/div/span//text()')
                            awayTeamSpreadClosing = getTextFromXpath(game, 'table/tbody/tr[2]/td[5]/div/span//text()')
        
                            homeTeamSpreadOpening = awayTeamSpreadOpening * -1
                            homeTeamSpreadClosing = awayTeamSpreadClosing * -1
                        except:
                            homeTeamSpreadOpening = ""
                            homeTeamSpreadClosing = ""

                            awayTeamSpreadOpening = ""
                            awayTeamSpreadClosing = ""

                        





                    
                    #each team is yielded on data row

                    #this yield is about home team data
                    yield{
                        'date': date,
                        'location': "home",
                        'team': homeTeam,
                        'oppTeam': awayTeam,
                        'ptsMade': homeTeamPts,
                        'ptsSuffered': awayTeamPts,
                        'teamRecord': homeTeamRecord,
                        'oppTeamRecord': awayTeamRecord,
                        'pointSpreadOpening': pointSpreadOpening,
                        'pointSpreadClosing': pointSpreadClosing,
                        'spreadOpening': homeTeamSpreadOpening,
                        'spreadClosing': homeTeamSpreadClosing,
                        'teamML': homeTeamML,

                    }
                    
                    #this yield is about away team data
                    yield{
                        'date': date,
                        'location': "away",
                        'team': awayTeam,
                        'oppTeam': homeTeam,
                        'ptsMade': awayTeamPts,
                        'ptsSuffered': homeTeamPts,
                        'teamRecord': awayTeamRecord,
                        'oppTeamRecord': homeTeamRecord,
                        'pointSpreadOpening': pointSpreadOpening,
                        'pointSpreadClosing': pointSpreadClosing,
                        'spreadOpening': awayTeamSpreadOpening,
                        'spreadClosing': awayTeamSpreadClosing,
                        'teamML': awayTeamML,

                    }

        #we update the date we are going tro scrape summing 1 day to de day we just scraped
        self.dateToScrape = self.dateToScrape + datetime.timedelta(days=1)

        next_page = "nba?date="+self.dateToScrape.strftime("%Y-%m-%d")

        #if there is no next page or the date to scrape is greater to the end_date passed as argument, the spider stops
        #otherwise it keeps scraping
        if next_page is not None and self.dateToScrape < seasonEndDate :
            yield response.follow(f'https://www.scoresandodds.com/{next_page}', callback=self.parse)
    
    

