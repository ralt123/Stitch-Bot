#instal module epicstore-api
from epicstore_api import EpicGamesStoreAPI
from datetime import datetime


def main():
  api = EpicGamesStoreAPI()
  getgames = api.get_free_games()
  freegames = getgames['data']['Catalog']['searchStore']['elements']
  for game in freegames:
    gamename = game['title']
    gameprice = game['price']['totalPrice']['fmtPrice']['originalPrice']
    gamepromotions = game['promotions']['promotionalOffers']
    upcomingpromotions = game['promotions']['upcomingPromotionalOffers']
    if not gamepromotions and upcomingpromotions:
      promotiondata = upcomingpromotions[0]['promotionalOffers'][0]
      startdateis, enddateis = (promotiondata['startDate'][:-1], promotiondata['endDate'][:-1])
      startdate = datetime.fromisoformat(startdateis)
      enddate = datetime.fromisoformat(enddateis)
      print('{} ({}) will become free from {} to {}.'.format(gamename, gameprice, startdate, enddate))
    else:
      print('{} ({}) is currently free.'.format(gamename, gameprice))


if __name__ == '__main__':
    main()
