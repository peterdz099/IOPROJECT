from validate_email_address import validate_email
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from database_handler.initialize_database import Database
from database_handler.users import Users
from database_handler.users import is_pwd_correct
from usrHelper import UserHelper


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def login(self):

        dictionary = usersResources.select_user(email=self.email.text, username=self.email.text)

        if dictionary:
            if is_pwd_correct(self.password.text, dictionary.get('password')):
                self.reset()
                sm.current = "main"
            else:
                print("BAD PASSWORD")
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

    def change(self):
        print(self.ids.find.text)
        self.ids.find.text = ''


    def back_to_login(self):
        self.reset()
        sm.current = "login"



class WithoutLoginWindow(Screen):

    def change(self):
        print(self.ids.find.text)
        self.ids.find.text = ''



class WindowManager(ScreenManager):
    pass


sm = WindowManager()
db = Database()
usersResources = Users(db)
db.create_tables()

user = UserHelper("pitok")
#!!!!!!!!!!!!!!!!!!!!!!


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

        sm.current = "main"

        return sm


if __name__ == '__main__':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'resizable', False)
    Config.write()
    MyApp().run()
