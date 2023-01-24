import json
import operator
from bs4 import BeautifulSoup
import requests
from database_handler.initialize_database import Database
from database_handler.offers import Offers as OffersResource

# funkcja scraper() zwraca gotowa listę obiektów Toy(opis obiektu Toy niżej) znalezionych na stronie Ceneo po wpisaniu danej frazie
# name_toy<string> - nazwa zabawki która chcemy wyszukać
# mode<int> - określa w jakich sklepach wyszukujemy zabawek
#   mode 0 -> szukaj wszystko
#   mode 1 -> szukaj tylko alegro
#   mode 2 -> szukaj wszystko tylko nie allegro
# sort_by_num_shops<bool> - określa metode sortowania wyników
# sort_by_num_shops = True -> sortowanie po ilosci sklepow
# sort_by_num_shops = False -> od najniższej ceny.

def scraper(name_toy, mode, sort_by_num_shops, page=1):
    name = name_toy.replace(" ", "+")
    page = page
    mode = mode
    sort_by_num_shops = sort_by_num_shops
    toy_list = []
    if mode == 0 or mode == 2:
        cenneo_url = f"https://www.ceneo.pl/Dla_dziecka;szukaj-{name}"
        resp = requests.get(cenneo_url)
        print(resp)
        soup = BeautifulSoup(resp.text, 'html.parser')
        toy_cards = soup.find_all('div',
                                  class_="cat-prod-row js_category-list-item js_clickHashData js_man-track-event")
    elif mode == 1:
        cenneo_url = f"https://www.ceneo.pl/Dla_dziecka;szukaj-{name};20136-0v.htm"
        resp = requests.get(cenneo_url)
        print(resp)
        soup = BeautifulSoup(resp.text, 'html.parser')
        toy_cards = soup.find_all('div',
                                  class_="cat-prod-row js_category-list-item js_clickHashData js_man-track-event js_substitute")

    for item in toy_cards:
        toy_name = item.get('data-productname')
        toy_id = item.get('data-pid')
        toy_price = float(item.get('data-productminprice'))
        toy_manufacturer = item.get('data-brand')
        toy_photo_url = item.find('img').get("data-original")

        if toy_photo_url == None:
            toy_photo_url = item.find('img').get("src")

        toy = Toy(name=toy_name, id=toy_id, min_price=toy_price, manufacturer=toy_manufacturer, shop_num=0,
                  photo_url=toy_photo_url)
        toy.getShopInfo(mode)
        if toy.shop_num != 0:
            toy_list.append(toy)
    if sort_by_num_shops:
        toy_list = sorted(toy_list, key=operator.attrgetter("shop_num"), reverse=True)
    else:
        toy_list = sorted(toy_list, key=operator.attrgetter("min_price"))

    return toy_list


# klasa "Shop" pozwwala na przetrzymywanie informacji o sklepach w kótrych możliwy jest zakup danej zabawki
# Informacje jakie zawiera to:
# -id sklepu<string>
# -nawa sklepu<string>
# -url pod którym możliwe jest zakupienie produktu<string>
# -cena za jaką możemy kupić zabawkę w tym sklepie<string>
# -id oferty<string>
# -metody dostawy produktu a także cena dostawy<list>

class Shop:
    def __init__(self, id, name, price, shop_url, offer_id):
        self.id = id
        self.name = name
        self.price = price
        self.shop_url = 'ceneo.pl' + shop_url
        self.offer_id = offer_id
        self.deliver_method = []

    def __str__(self):
        return f'name: {self.name}, ' \
               f'id: {self.id}, ' \
               f'price: {self.price}, ' \
               f'url: {self.shop_url} '

# klasa "Toy" pozwwala na przetrzymywanie informacji o danej zabawce która znajduje się w bazie Ceneo
# Informacje jakie zawiera to:
# -id produktu w serwisie Ceneo
# -nazwa zabawki<string>
# -minimalna cena zabawki<string>
# -producent<string>
# -liczba sklepów w których można zakupić taką zabawkę<int>
# -lista obiektów "Shop" które zawierają informacje o sklepach w których można zakupić zabawkę<list>
# -url obrazka przedstawiający zabawke<string>

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

# funkcja getShopInfo() wypelnia shop_list w objekcie Toy. Dodaje do niej obiekty Shop zawierające informacje o sklepach
# w których możemy kupić daną zabawkę.
# Przyjmuje ona argument mode który odpowiada za filtrowanie sklepów
# mode 0 -> szukaj wszystko
# mode 1 -> szukaj tylko alegro
# mode 2 -> szukaj wszystko tylko nie allegro

    def getShopInfo(self, mode):
        product_url = f"https://www.ceneo.pl/{self.id}"
        resp = requests.get(product_url)
        product_soup = BeautifulSoup(resp.text, 'html.parser')
        shops_cards = product_soup.find_all('li', class_="product-offers__list__item js_productOfferGroupItem")
        shop_list = []
        for shop_card in shops_cards:
            shop_info = shop_card.find('div',
                                       class_="product-offer__container clickable-offer js_offer-container-click js_product-offer")
            if shop_info != None:
                shop_name = shop_info.get('data-shopurl')
                shop_id = shop_info.get('data-shop')
                shop_url = shop_info.get('data-click-url')
                shop_price = shop_info.get('data-price')
                offer_id = shop_info.get('data-offerid')
                if mode == 1:
                    if shop_name == 'allegro.pl':
                        shop = Shop(name=shop_name, id=shop_id, price=shop_price, shop_url=shop_url, offer_id=offer_id)
                        shop_list.append(shop)
                        self.shop_num += 1
                elif mode == 2:
                    if shop_name != 'allegro.pl':
                        shop = Shop(name=shop_name, id=shop_id, price=shop_price, shop_url=shop_url, offer_id=offer_id)
                        shop_list.append(shop)
                        self.shop_num += 1
                else:
                    shop = Shop(name=shop_name, id=shop_id, price=shop_price, shop_url=shop_url, offer_id=offer_id)
                    shop_list.append(shop)
                    self.shop_num += 1
        self.shop_list = sorted(shop_list, key=operator.attrgetter('price'))

        try:
            error = False
            deliveryURL = "https://www.ceneo.pl/Product/GetOfferDetails?data=" + \
                          self.shop_list[0].shop_url.split("?e=")[1]

        except:
            error = True
        if error == False:
            json_data = requests.get(deliveryURL).text
            parsed = json.loads(json_data)
            deliver_html = parsed["ProductDetailsAdditionalPartial"]
            delivery_soup = BeautifulSoup(deliver_html, 'html.parser')
            deliveries = delivery_soup.find_all(
                "li",
                class_="product-offer-details__additional__delivery-costs__list__item",
            )

            for deliver in deliveries:
                for item in deliver.find_all("li"):
                    productPrice = item.get_text()
                    deliveryInfo = productPrice.replace('\n', '').split("zł")
                    if len(deliveryInfo) > 1:
                        line = []
                        line.append(float(deliveryInfo[0].replace(",", ".")))
                        line.append(deliveryInfo[1])
                        self.shop_list[0].deliver_method.append(line)




# if __name__ == "__main__":
#     db = Database()
#     db.create_tables()
#
#     toylist = scraper("chudy", mode=0, sort_by_num_shops=True)
#     for toy in toylist:
#         print(toy)
#         for shop in toy.shop_list:
#             print(shop)
#             OffersResource(db).add_offer(shop.offer_id, toy.name, shop.price, shop.shop_url, shop.name,
#                                          toy.manufacturer, toy.photo_url)
#         print("############_________###############")
#
#     db.close_connection()

if __name__ == "__main__":
    toylist = scraper("chudy", mode=2, sort_by_num_shops=True)
    for toy in toylist:
        print(toy)
        for shop in toy.shop_list:
            print(shop)
        print("############_________###############")
