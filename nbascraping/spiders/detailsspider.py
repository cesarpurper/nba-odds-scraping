import scrapy
import re
from datetime import datetime

class ScoresAndOddsSpider(scrapy.Spider):
    name = 'detailsspider'
    start_urls = ['https://www.scoresandodds.com/nba?date=2021-10-09']





    def parse(self, response):
        for game in response.css('div.event-card'):

            detailId = game.attrib['id'].split("nba.",1)[1] 
            url = "https://www.scoresandodds.com/nba/events/"+str(detailId)+"/details"

            yield scrapy.Request(url=url, callback=self.parseDetail)
            
            

        next_page = response.css('div.date-picker-next').attrib['data-endpoint']
        if next_page is not None:
            yield response.follow("https://www.scoresandodds.com"+next_page, callback=self.parse)

    def parseDetail(self, response):

        ## team names
        homeTeamName = response.xpath('/html/body/header/div[1]/span[2]/span[2]//text()').extract_first().strip()
        homeTeamShortName = response.xpath('/html/body/header/div[1]/span[2]/span[1]//text()').extract_first().strip()

        awayTeamName = response.xpath('/html/body/header/div[3]/span[1]/span[2]//text()').extract_first().strip()
        awayTeamShortName = response.xpath('/html/body/header/div[3]/span[1]/span[1]//text()').extract_first().strip()

        #date
        #a data esta com um Z no final, por isso tiro o ultimo caractere        
        date = str(datetime.fromisoformat(response.xpath('/html/body/header/div[2]/div/span/@data-value').extract_first()[:-1]))

        #pts
        homeTeamPts = response.xpath('/html/body/header/div[2]/span[1]//text()').extract_first().strip()
        awayTeamPts = response.xpath('/html/body/header/div[2]/span[2]//text()').extract_first().strip()

        #team records
        homeTeamRecord = response.xpath('/html/body/div[1]/div/table/tbody[1]/tr[1]/td[2]/span[2]/span[2]/span//text()').extract_first().strip()
        awayTeamRecord = response.xpath('/html/body/div[1]/div/table/tbody[1]/tr[2]/td[1]/span[2]/span[2]/span//text()').extract_first().strip()
        
        #pointspread closing

        closingPointSpreadTeamFavorite = response.xpath('/html/body/div[2]/div/table/tbody/tr[1]/td[2]/text()').extract_first().strip()
        closingPointSpreadMargin = float(response.xpath('/html/body/div[2]/div/table/tbody/tr[1]/td[2]/span/text()').extract_first().strip())
        
        #caso o time da casa seja o favorito
        if closingPointSpreadTeamFavorite == homeTeamShortName:
            homeTeamPointSpreadClosing = closingPointSpreadMargin
            awayTeamPointSpreadClosing = closingPointSpreadMargin * -1
        else:
            homeTeamPointSpreadClosing = closingPointSpreadMargin * -1
            awayTeamPointSpreadClosing = closingPointSpreadMargin

        #ML closing

        closingMLHomeTeam = response.xpath('/html/body/div[2]/div/table/tbody/tr[1]/td[4]/span/text()').extract_first().strip()
        closingMLAwayTeam = response.xpath('/html/body/div[2]/div/table/tbody/tr[1]/td[5]/span/text()').extract_first().strip()
        
        
        #jogadores
        #starters home

        starter1Home = response.xpath('/html/body/div[5]/div[2]/div[1]/table/tbody/tr[1]/th/text()').extract_first().strip()
        starter2Home = response.xpath('/html/body/div[5]/div[2]/div[1]/table/tbody/tr[2]/th/text()').extract_first().strip()
        starter3Home = response.xpath('/html/body/div[5]/div[2]/div[1]/table/tbody/tr[3]/th/text()').extract_first().strip()
        starter4Home = response.xpath('/html/body/div[5]/div[2]/div[1]/table/tbody/tr[4]/th/text()').extract_first().strip()
        starter5Home = response.xpath('/html/body/div[5]/div[2]/div[1]/table/tbody/tr[5]/th/text()').extract_first().strip()
        #starters away

        starter1Away  = response.xpath('/html/body/div[5]/div[3]/div[1]/table/tbody/tr[1]/th/text()').extract_first().strip()
        starter2Away  = response.xpath('/html/body/div[5]/div[3]/div[1]/table/tbody/tr[2]/th/text()').extract_first().strip()
        starter3Away  = response.xpath('/html/body/div[5]/div[3]/div[1]/table/tbody/tr[3]/th/text()').extract_first().strip()
        starter4Away  = response.xpath('/html/body/div[5]/div[3]/div[1]/table/tbody/tr[4]/th/text()').extract_first().strip()
        starter5Away  = response.xpath('/html/body/div[5]/div[3]/div[1]/table/tbody/tr[5]/th/text()').extract_first().strip()




        yield{
            'location': "home",
            'team': homeTeamName,
            'teamShortName': homeTeamShortName,
            'oppTeam': awayTeamName,
            'oppTeamShortName': awayTeamShortName,
            'date': date,
            'ptsMade': homeTeamPts,
            'PtsSuffered': awayTeamPts,
            'teamRecord': homeTeamRecord,
            'oppTeamRecord': awayTeamRecord,
            'pointSpreadClosing': homeTeamPointSpreadClosing,
            'MLClosing': closingMLHomeTeam,
            'starter1' : starter1Home,
            'starter2' : starter2Home,
            'starter3' : starter3Home,
            'starter4' : starter4Home,
            'starter5' : starter5Home,

        }
        yield{
            'location': "away",
            'team': awayTeamName,
            'teamShortName': awayTeamShortName,
            'oppTeam': homeTeamName,
            'oppTeamShortName': homeTeamShortName,
            'date': date,
            'ptsMade': awayTeamPts,
            'PtsSuffered': homeTeamPts,
            'teamRecord': awayTeamRecord,
            'oppTeamRecord': homeTeamRecord,
            'pointSpreadClosing': awayTeamPointSpreadClosing,
            'MLClosing': closingMLAwayTeam,
            'starter1' : starter1Away,
            'starter2' : starter2Away,
            'starter3' : starter3Away,
            'starter4' : starter4Away,
            'starter5' : starter5Away,
        }

