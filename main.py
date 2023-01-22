from kivymd.uix.list import OneLineListItem, ThreeLineAvatarIconListItem, TwoLineAvatarListItem, ImageLeftWidget
from validate_email_address import validate_email
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivymd.app import MDApp

import webscraper
from database_handler.initialize_database import Database
from database_handler.users import Users
from database_handler.users import is_pwd_correct
import random
from file_manager import load_file_and_save_to_csv


allegro_mode=0

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

    @staticmethod
    def send_email():
        code = random.randint(100000, 1000000)
        VerifyWindow.generated_code = str(code)
        print(code)

    def reset(self):
        self.ids.code.text = ""
        VerifyWindow.generated_code = None
        VerifyWindow.email_or_username = ""


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def login(self):

        dictionary = usersResources.select_user(email=self.email.text, username=self.email.text)

        if dictionary:
            if is_pwd_correct(self.password.text, dictionary.get('password')):
                sm.get_screen("main").set_name(self.email.text)
                self.reset()
                sm.current = "main"
            else:
                print("BAD PASSWORD")
        elif dictionary and dictionary.get('is_verified') == 0:
            sm.get_screen("verify").set_user(self.email.text)
            sm.get_screen("verify").send_email()
            self.reset()
            sm.current = "verify"
        else:
            print("NOT USER FOUND")

    def create_new_account(self):
        self.reset()
        sm.current = "register"

    def reset(self):
        self.email.text = ""
        self.password.text = ""

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
                print("THAT EMAIL DOESN'T EXISTS")
                self.reset()

            elif self.password.text != self.repeatedPassword.text:
                print("PASSWORDS DON'T MATCH")
                self.reset()
            elif check:
                print("USER ALREADY EXISTS")
            else:
                if self.password.text == self.repeatedPassword.text and validate_email(self.email.text):
                    usersResources.add_user(self.username.text, self.password.text, self.email.text)
                    self.reset()
                    sm.current = "login"
                    print("OK")
        else:
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

    def set_name(self, name):
        self.ids.username.text = "You are logged as: " + name

    def clear_findings(self, *args):
        self.ids.scroll.clear_widgets()
        self.ids.screen_manager.current = "screeen1"
        pass

    def clear_search(self):
        self.ids.find.text = ""

    def clear_history(self):
        self.ids.scroll_history.clear_widgets()

    def clear_basket(self):
        self.ids.scroll_cart.clear_widgets()

    def back_to_login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.clear_search()
        self.clear_basket()
        self.clear_history()

    def history(self):
        for i in range(30):
            self.ids.scroll_history.add_widget(OneLineListItem(text=f"ssssss: {i}"))

    def cart(self):
        for i in range(30):
            self.ids.scroll_cart.add_widget(OneLineListItem(text=f"ssssss: {i}"))

    def search(self):

        print(self.ids.find.text)
        s = self.ids.find.text

        if any(c.isalpha() for c in s):
            self.ids.screen_manager.current = "screeen2"
            for i in range(4):
                self.ids.scroll.add_widget(ThreeLineAvatarIconListItem(text=self.ids.find.text, secondary_text="Secondary text here", tertiary_text= "fit more text than usual"))
            self.ids.set.text = "Findings of: " + self.ids.find.text
        else:
            "EMPTY"

    def handle_import_button_pressed(self):
        offer_list = load_file_and_save_to_csv()

class WithoutLoginWindow(Screen):

    allegro_mode = 0


    def search(self):
        print(self.ids.find.text)
        s = self.ids.find.text
        toy_list = webscraper.scraper(s, allegro_mode)

        if any(c.isalpha() for c in s):
            self.ids.screen_manager.current = "screeen2"
            for i in range(4):
                self.ids.scroll.add_widget(TwoLineAvatarListItem(
                    ImageLeftWidget(
                        source=f"https:{toy_list[i].photo_url}"),
                    text=toy_list[i].name, secondary_text=f"https://www.ceneo.pl/{toy_list[i].id}",
                    on_release=lambda x: self.to_product(toy_list[i])
                ))
            self.ids.set.text = "Findings of: " + self.ids.find.text
        else:
            self.ids.find.text = ""
            print("EMPTY")

    def clear(self):

        pass
    def to_product(self, num):
        self.ids.screen_manager.current = "screeen3"

class WindowManager(ScreenManager):
    pass


sm = WindowManager()
db = Database()
usersResources = Users(db)
db.create_tables()


class MyApp(MDApp):
    def build(self):
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
