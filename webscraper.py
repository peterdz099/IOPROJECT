import operator
import random

from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass
from database_handler.initialize_database import Database
from database_handler.toys import Toys as ToysResource
from database_handler.offers import Offers as OffersResource


class Shop:
    def __init__(self, id, name, price, shop_url, offer_id):
        self.id = id
        self.name = name
        self.price = price
        self.shop_url = 'ceneo.pl' + shop_url
        self.offer_id = offer_id
        # self.deliver_method = deliver_method
        # self.deliver_price = deliver_price

    def __str__(self):
        return f'name: {self.name}, ' \
               f'id: {self.id}, ' \
               f'price: {self.price}, ' \
               f'url: {self.shop_url} ' \
               f'offer_id: {self.offer_id} '

class Toy:
    def __init__(self, id, name, min_price, manufacturer, shop_num, photo_url):
        self.id = id
        self.name = name
        self.min_price = min_price
        self.manufacturer = manufacturer
        self.shop_num = shop_num
        self.shop_list = []
        self.photo_url = photo_url

    def __str__(self):
        return f'name: {self.name}, ' \
               f'id: {self.id}, ' \
               f'min price: {self.min_price}, ' \
               f'manufacturer: {self.manufacturer}, ' \
               f'number of shops: {self.shop_num}, ' \
               f'img url: {self.photo_url}'

    def getShopInfo(self):
        product_url = f"https://www.ceneo.pl/{self.id}"
        resp = requests.get(product_url)
        product_soup = BeautifulSoup(resp.text, 'lxml')
        shops_cards = product_soup.find_all('li', class_="product-offers__list__item js_productOfferGroupItem")
        shop_list = []
        self.shop_num = len(shops_cards)
        for shop_card in shops_cards:
            shop_info = shop_card.find('div',
                                       class_="product-offer__container clickable-offer js_offer-container-click js_product-offer")
            if shop_info != None:
                shop_name = shop_info.get('data-shopurl')
                shop_id = shop_info.get('data-shop')
                shop_url = shop_info.get('data-click-url')
                shop_price = shop_info.get('data-price')
                offer_id = shop_info.get('data-offerid')
                shop = Shop(name=shop_name, id=shop_id, price=shop_price, shop_url=shop_url, offer_id=offer_id)
                shop_list.append(shop)
        self.shop_list = shop_list


def scraper(name, page=1):
    name = name
    page = page
    cenneo_url = f"https://www.ceneo.pl/Dla_dziecka;szukaj-{name};0020-30-0-0-{page}.htm"
    resp = requests.get(cenneo_url)
    print(resp)
    soup = BeautifulSoup(resp.text, 'lxml')
    toy_cards = soup.find_all('div', class_="cat-prod-row js_category-list-item js_clickHashData js_man-track-event")

    toy_list = []

    for item in toy_cards:
        toy_name = item.get('data-productname')
        toy_id = item.get('data-pid')
        toy_price = float(item.get('data-productminprice'))
        toy_manufacturer = item.get('data-brand')
        toy_photo_url = item.find('img').get('data-original')
        toy = Toy(name=toy_name, id=toy_id, min_price=toy_price, manufacturer=toy_manufacturer, shop_num=None, photo_url=toy_photo_url)
        toy.getShopInfo()
        toy_list.append(toy)

    toy_list = sorted(toy_list, key=operator.attrgetter("min_price"))



    return toy_list


if __name__ == "__main__":
    db = Database()
    db.create_tables()

    toylist = scraper("samochod")
    for toy in toylist:
        print(toy)
        ToysResource(db).add_toy(toy.id, toy.name, toy.min_price, toy.manufacturer, toy.shop_num, toy.photo_url)
        for shop in toy.shop_list:
            print(shop)
            OffersResource(db).add_offer(shop.offer_id, shop.shop_url, toy.id, shop.id, shop.name, shop.price)
        print("############_________###############")

    db.close_connection()
