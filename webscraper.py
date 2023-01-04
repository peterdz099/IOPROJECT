import operator
import random

from bs4 import BeautifulSoup
import requests
from dataclasses import dataclass

# @dataclass
# class Product:
#     id: str
#     name: str
#     min_price: float
#     manufacturer: str
#     shop_num : int

class Shop:
    def __init__(self, id, name, price, deliver_method=[], deliver_price=[]):
        self.id = id
        self.name = name
        self.price = price
        self.shop_url = ''
        # self.deliver_method = deliver_method
        # self.deliver_price = deliver_price

    def __str__(self):
        return f'name: {self.name}, ' \
               f'id: {self.id}, ' \
               f'price: {self.price}, ' \
               f'deliver_method: {self.deliver_method}, ' \
               f'deliver_price: {self.deliver_price}'

class Toy:
    def __init__(self, id, name, min_price, manufacturer, shop_num):
        self.id = id
        self.name = name
        self.min_price = min_price
        self.manufacturer = manufacturer
        self.shop_num = shop_num
        self.shop_list = []
    def __str__(self):
        return f'name: {self.name}, ' \
               f'id: {self.id}, ' \
               f'min price: {self.min_price}, ' \
               f'manufacturer: {self.manufacturer}, ' \
               f'number of shops: {self.shop_num}'
    def getShopInfo(self):
        product_url = f"https://www.ceneo.pl/{self.id}"
        resp = requests.get(product_url)
        product_soup = BeautifulSoup(resp.text, 'lxml')
        shops_cards = product_soup.find_all('li', class_="product-offers__list__item js_productOfferGroupItem")
        shop_list = []
        self.shop_num = len(shops_cards)
        for shop_card in shops_cards:
            shop_info = shop_card.find('div', class_="product-offer__container clickable-offer js_offer-container-click js_product-offer")
            if shop_info != None:
                shop_name = shop_info.get('data-shopurl')
                shop_id = shop_info.get('data-shop')
                shop = Shop(name=shop_name, id=shop_id, price=None)
                shop_list.append(shop)
        self.shop_list = shop_list
name = "chudy"
page = "1"
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
    toy = Toy(name=toy_name, id=toy_id, min_price=toy_price, manufacturer=toy_manufacturer, shop_num=None)
    toy_list.append(toy)

toy_list = sorted(toy_list, key=operator.attrgetter("min_price"))
# for item in toy_list:
#      print(item)
#
#random_product = toy_list[random.randint(1, len(toy_list)-1)]

for toy in toy_list:
    toy.getShopInfo()
    print(toy)