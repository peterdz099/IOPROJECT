from kivy.core.window import Window
from kivymd.uix.list import OneLineListItem, TwoLineAvatarListItem, ImageLeftWidget, \
    TwoLineListItem
from validate_email_address import validate_email
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
import webscraper
from database_handler.initialize_database import Database
from database_handler.offers import Offers
from database_handler.search_history import SearchHistory
from database_handler.shopping_list import ShoppingList
from database_handler.users import Users
from database_handler.users import is_pwd_correct
import webbrowser
import random
import os
from email.message import EmailMessage
import ssl
import smtplib

# from file_manager import load_file_and_save_to_csv
from file_manager import load_file_and_save_to_csv, save_cart_to_file


def create_details_string(name, price, manu, shops, shop_list):
    s = f"\nNAME: {name} \nPRICE: {price}\nMANUFACTURER: {manu}\nNUMBER OF SHOPS: {shops}\nBEST SHOP: " \
        f"{shop_list[0].name}\nDELIVERY METHOD:\n "

    d = ""
    for delivery_method in shop_list[0].deliver_method:
        d = d + "\t" + delivery_method[1] + " " + str(delivery_method[0]) + " " + "\n"

    return s + d


class VerifyWindow(Screen):
    generated_code = ""
    email_or_username = ""

    @staticmethod
    def set_user(email):
        VerifyWindow.email_or_username = email

    def verify(self):
        if self.ids.code.text == VerifyWindow.generated_code:
            print('success')
            usersResources.verify_user(email=VerifyWindow.email_or_username, username=VerifyWindow.email_or_username)
            sm.current = "login"
            self.reset()
        else:
            self.ids.verify_message.text = "Try again"

    @staticmethod
    def send_email():
        email_sender = "toysapp8@gmail.com"
        email_password = os.environ.get("EMAIL_PASSWORD")

        email_receiver = VerifyWindow.email_or_username

        subject = "Verification Code"

        code = random.randint(100000, 1000000)
        VerifyWindow.generated_code = str(code)
        print(code)

        body = f"""Type your verification code in application\nYour Code: {code}"""

        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = email_receiver
        em['Subject'] = subject
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_password)
            smtp.sendmail(email_sender, email_receiver, em.as_string())

    def reset(self):
        self.ids.code.text = ""
        VerifyWindow.generated_code = None
        VerifyWindow.email_or_username = ""
        sm.current = "login"


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def login(self):

        dictionary = usersResources.select_user(email=self.email.text, username=self.email.text)

        if dictionary and dictionary.get('is_verified') == 1:
            if is_pwd_correct(self.password.text, dictionary.get('password')):
                sm.get_screen("main").set_name(self.email.text, dictionary.get('id'))
                sm.get_screen("main").history(dictionary.get('id'))
                sm.get_screen("main").cart()
                self.reset()
                sm.current = "main"
            else:
                self.ids.login_message.text = "BAD PASSWORD"

        elif dictionary and dictionary.get('is_verified') == 0:
            if is_pwd_correct(self.password.text, dictionary.get('password')):
                sm.get_screen("verify").set_user(dictionary.get('email'))
                sm.get_screen("verify").send_email()
                self.reset()
                sm.current = "verify"
            else:
                self.ids.login_message.text = "BAD PASSWORD"
        else:
            self.ids.login_message.text = "USER NOT FOUND"

    def create_new_account(self):
        self.reset()
        sm.current = "register"

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.ids.login_message.text = "Log in or create new account"

    def without(self):
        self.reset()
        sm.current = "without"


class RegisterWindow(Screen):
    email = ObjectProperty(None)
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    repeatedPassword = ObjectProperty(None)

    def submit(self):

        if self.username.text != "" and self.email.text != "" and self.password.text != "" \
                and self.repeatedPassword.text != "":

            dictionary = usersResources.select_user(username=self.username.text, email=self.email.text)

            check = bool(dictionary)

            if not validate_email(self.email.text):
                self.ids.new_account_message.text = "USE REAL EMAIL"
                self.reset()

            elif self.password.text != self.repeatedPassword.text:
                self.ids.new_account_message.text = "PASSWORDS DON'T MATCH"
                self.reset()
            elif check:
                self.ids.new_account_message.text = "USER ALREADY EXISTS"
            else:
                if self.password.text == self.repeatedPassword.text and validate_email(self.email.text):
                    usersResources.add_user(self.username.text, self.password.text, self.email.text)
                    self.reset()
                    self.ids.new_account_message.text = "Fill the form and click submit button"
                    sm.current = "login"
                    print("OK")
        else:
            self.ids.new_account_message.text = "fill out all the form fields"
            self.reset()

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.username.text = ""
        self.repeatedPassword.text = ""

    def back_to_login(self):
        self.reset()
        sm.current = "login"


class MainWindow(Screen):
    user_id = None
    obj = None
    obj2 = None
    sort_mode = False
    file_mode = 0
    file_sort_mode = False
    allegro_mode = 0
    url_helper = ""
    url_helper2 = ""

    def set_name(self, name, idu):
        self.ids.username.text = "You are logged as: " + name
        MainWindow.user_id = idu

    def clear_findings(self):
        self.ids.scroll.clear_widgets()
        self.ids.screen_manager.current = "screeen1"

    def clear_file_findings(self):
        self.ids.scroll2.clear_widgets()
        self.ids.screen_manager_2.current = "s1"

    def clear_search(self):
        self.ids.find.text = ""

    def clear_history(self):
        self.ids.scroll_history.clear_widgets()

    def clear_basket(self):
        self.ids.scroll_cart.clear_widgets()

    def back_to_login(self):
        self.reset()
        self.ids.nav.switch_tab('screen 1')
        sm.current = "login"

    def reset(self):
        self.clear_findings()
        self.clear_file_findings()
        self.clear_search()
        self.clear_basket()
        self.clear_history()

    def delete_user_cart(self):
        shoppingListResources.delete_shopping_list(MainWindow.user_id)
        self.clear_basket()
        self.cart()

    def history(self, user_id):
        user_history = historyResources.select_search_history(user_id)

        print(user_history)
        if user_history:
            for i in reversed(user_history):
                self.ids.scroll_history.add_widget(TwoLineListItem(text=str(i.get('user_input')),
                                                                   secondary_text=str(i.get('datetime'))))
        else:
            self.ids.scroll_history.add_widget(OneLineListItem(text='           Your search history is empty')),

    def cart(self):
        basket = shoppingListResources.select_shopping_list(MainWindow.user_id)
        if basket:
            for i in range(len(basket)):
                offer = offersResources.select_offer(basket[i].get('offer_id'))
                print(offer)
                self.ids.scroll_cart.add_widget(TwoLineAvatarListItem(
                    ImageLeftWidget(
                        source=f"https:{offer.get('img_url')}"),
                    text=offer.get('toy_name'),
                    secondary_text=f"https://www.ceneo.pl/{offer.get('id')}"))
        else:
            self.ids.scroll_cart.add_widget(OneLineListItem(text="              Your cart list is empty")),

    @staticmethod
    def import_cart_to_file():
        basket = shoppingListResources.select_shopping_list(MainWindow.user_id)
        basket_list = []
        if basket:
            for i in range(len(basket)):
                offer = offersResources.select_offer(basket[i].get('offer_id'))
                offer_data = {'Name': offer.get('toy_name'), 'PRICE': offer.get('price'), 'URL': offer.get('url')}
                basket_list.append(offer_data)
        else:
            print(basket)

        save_cart_to_file(basket_list)

    def search(self):
        print(self.ids.find.text)
        search = self.ids.find.text

        if any(c.isalpha() for c in search):
            toy_list = webscraper.scraper(search, MainWindow.allegro_mode, MainWindow.sort_mode, 1)
            print(toy_list)
            if len(toy_list):
                print(f"wyszukujesz w trybie sortowania {MainWindow.sort_mode}")
                historyResources.add_search_history(MainWindow.user_id, search)
                self.clear_history()
                self.history(MainWindow.user_id)
                self.ids.screen_manager.current = "screeen2"

                for i in range(10 if len(toy_list) > 10 else len(toy_list)):
                    self.ids.scroll.add_widget(TwoLineAvatarListItem(
                        ImageLeftWidget(
                            source=f"https:{toy_list[i].photo_url}"),
                        text=toy_list[i].name,
                        secondary_text=f"https://www.ceneo.pl/{toy_list[i].id}",
                        id=f"{i}",
                        on_release=(lambda x: self.to_product(toy_list[int(x.id)]))
                    ))

                self.ids.set.text = "Findings of: " + self.ids.find.text
            else:
                self.ids.message.text = "This toy doesn't exist"
        else:
            self.ids.find.text = ""
            self.ids.message.text = "Type a name of the toy!"

    def search_from_file(self):
        offer_list = load_file_and_save_to_csv(MainWindow.file_mode, MainWindow.file_sort_mode)

        if len(offer_list):
            self.ids.screen_manager_2.current = "s2"
            for i in range(len(offer_list)):
                if not isinstance(offer_list[i], str):
                    self.ids.scroll2.add_widget(TwoLineAvatarListItem(
                        ImageLeftWidget(
                            source=f"https:{offer_list[i].photo_url}"),
                        text=offer_list[i].name,
                        secondary_text=f"https://www.ceneo.pl/{offer_list[i].id}",
                        id=f"{i}",
                        on_release=(lambda x: self.to_file_product(offer_list[int(x.id)]))
                    ))
                else:
                    self.ids.scroll2.add_widget(OneLineListItem(text=offer_list[i]))
        else:
            self.ids.import_error.text = "Empty file"

    @staticmethod
    def change_mode(mode):
        MainWindow.allegro_mode = mode
        print(MainWindow.allegro_mode)

    @staticmethod
    def change_file_mode(mode):
        MainWindow.file_mode = mode
        print(MainWindow.file_mode)

    @staticmethod
    def change_sort_mode(mode):
        MainWindow.sort_mode = mode
        print(MainWindow.sort_mode)

    @staticmethod
    def change_file_sort_mode(mode):
        MainWindow.file_sort_mode = mode
        print(MainWindow.file_sort_mode)

    def to_product(self, obj):
        print(obj)
        MainWindow.obj = obj
        string = create_details_string(obj.name, obj.min_price, obj.manufacturer, obj.shop_num, obj.shop_list)
        self.ids.screen_manager.current = "screeen3"
        self.ids.details.text = string
        self.ids.screen_manager.transition.direction = "down"
        self.ids.imga.source = f"https:{obj.photo_url}"

    def to_file_product(self, obj):
        MainWindow.obj2 = obj
        string = create_details_string(obj.name, obj.min_price, obj.manufacturer, obj.shop_num, obj.shop_list)
        self.ids.screen_manager_2.current = "s3"
        self.ids.details2.text = string
        self.ids.screen_manager_2.transition.direction = "down"
        self.ids.img2.source = f"https:{obj.photo_url}"

    def add_to_basket(self):
        o = MainWindow.obj
        print(o)
        offersResources.add_offer(o.id, o.name, o.min_price, f"https://www.ceneo.pl/{o.id}", o.shop_list[0].name,
                                  o.manufacturer,
                                  o.photo_url)
        shoppingListResources.add_shopping_list(MainWindow.user_id, o.id)
        self.clear_basket()
        self.cart()

    def add_to_basket_from_file(self):
        o = MainWindow.obj2
        print(o)
        offersResources.add_offer(o.id, o.name, o.min_price, f"https://www.ceneo.pl/{o.id}", o.shop_list[0].name,
                                  o.manufacturer,
                                  o.photo_url)
        shoppingListResources.add_shopping_list(MainWindow.user_id, o.id)
        self.clear_basket()
        self.cart()

    @staticmethod
    def go_to_web():
        webbrowser.open(f"https://www.ceneo.pl/{MainWindow.obj.id}")

    @staticmethod
    def go_to_web2():
        webbrowser.open(f"https://www.ceneo.pl/{MainWindow.obj2.id}")


class WithoutLoginWindow(Screen):
    allegro_mode = 0
    sort_mode = False
    url_helper = ""

    def search(self):
        print(self.ids.find.text)
        s = self.ids.find.text

        if any(c.isalpha() for c in s):

            toy_list = webscraper.scraper(s, WithoutLoginWindow.allegro_mode, WithoutLoginWindow.sort_mode, 1)
            if len(toy_list):
                self.ids.find.text = ""
                self.ids.screen_manager.current = "screeen2"
                for i in range(10 if len(toy_list) > 10 else len(toy_list)):
                    self.ids.scroll.add_widget(TwoLineAvatarListItem(
                        ImageLeftWidget(
                            source=f"https:{toy_list[i].photo_url}"),
                        text=toy_list[i].name,
                        secondary_text=f"https://www.ceneo.pl/{toy_list[i].id}",
                        id=f"{i}",
                        on_release=(lambda x: self.to_product(toy_list[int(x.id)]))
                    ))
                self.ids.set.text = "Findings of: " + self.ids.find.text
            else:
                self.ids.find.text = ""
                self.ids.message.text = "This toy doesn't exist"
        else:
            self.ids.find.text = ""
            self.ids.message.text = "Type a name of the toy!"

    def clear_details(self):
        self.ids.details.text = ""

    def clear(self):
        self.ids.scroll.clear_widgets()
        self.ids.screen_manager.current = "screeen1"

    def to_product(self, obj):
        print(obj)
        WithoutLoginWindow.url_helper = f"https://www.ceneo.pl/{obj.id}"
        string = create_details_string(obj.name, obj.min_price, obj.manufacturer, obj.shop_num, obj.shop_list)
        self.ids.screen_manager.current = "screeen3"
        self.ids.details.text = string
        self.ids.img.source = f"https:{obj.photo_url}"

    @staticmethod
    def change_mode(mode):
        WithoutLoginWindow.allegro_mode = mode

    @staticmethod
    def change_sort_mode(mode):
        WithoutLoginWindow.sort_mode = mode
        print(mode)

    def go_to_web(self):
        webbrowser.open(WithoutLoginWindow.url_helper)


class WindowManager(ScreenManager):
    pass


sm = WindowManager()
db = Database()
usersResources = Users(db)
shoppingListResources = ShoppingList(db)
offersResources = Offers(db)
historyResources = SearchHistory(db)
db.create_tables()


class MyApp(MDApp):
    def build(self):
        Window.borderless = True
        self.theme_cls.theme_style = "Light"

        Builder.load_file('views.kv')
        sm.add_widget(LoginWindow(name="login"))
        sm.add_widget(RegisterWindow(name="register"))

        Builder.load_file('noLogin.kv')
        sm.add_widget(WithoutLoginWindow(name="without"))

        Builder.load_file('mainViews.kv')
        sm.add_widget(MainWindow(name="main"))

        Builder.load_file('verifyWindow.kv')
        sm.add_widget(VerifyWindow(name="verify"))

        sm.current = "login"

        return sm


if __name__ == '__main__':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'resizable', False)
    Config.write()
    MyApp().run()
