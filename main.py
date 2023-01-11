from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import Config
from kivy.properties import ObjectProperty
from kivymd.app import MDApp


class LoginWindow(Screen):
    def change(self):
        sm.current = "register"


class RegisterWindow(Screen):
    email = ObjectProperty(None)
    username = ObjectProperty(None)
    password = ObjectProperty(None)
    repeatedPassword = ObjectProperty(None)

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.username.text = ""
        self.repeatedPassword.text = ""

    def onClick(self):
        print(self.email.text, self.username.text, self.password.text, self.repeatedPassword.text)

    def backToLogin(self):
        self.reset()
        # sm.current = "login"


class WindowManager(ScreenManager):
    pass


sm = WindowManager()


class MyApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"

        Builder.load_file('views.kv')

        sm.add_widget(LoginWindow(name="login"))
        sm.add_widget(RegisterWindow(name="register"))

        sm.current = "login"
        return sm


if __name__ == '__main__':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'resizable', False)
    Config.write()
    MyApp().run()
