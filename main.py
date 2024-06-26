import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from database import DataBase
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from plyer import filechooser
import webbrowser
import shutil
import subprocess 

class CreateAccountWindow(Screen):
    namee = ObjectProperty(None)
    email = ObjectProperty(None)
    password = ObjectProperty(None)


    def login(self):
        self.reset()
        sm.current = "login"

    def reset(self):
        self.email.text = ""
        self.password.text = ""
        self.namee.text = ""

    def setup(self):
        sm.current = "setup"

    def submit(self):
        if self.namee.text != "" and self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password != "":
                db.add_user(self.email.text, self.password.text, self.namee.text)

                self.reset()

                sm.current = "login"
            else:
                invalidForm()
        else:
            invalidForm()


class LoginWindow(Screen):
    email = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.email.text, self.password.text):
            MainWindow.current = self.email.text
            self.reset()
            sm.current = "main"
            try:
                subprocess.Popen(['python', 'quickstart1.py'])  # Adjust this command based on your environment
            except Exception as e:
                print(f"Error running quickstart1.py: {e}")
        else:
            invalidLogin()

    def createBtn(self):
        self.reset()
        sm.current = "create"

    def reset(self):
        self.email.text = ""
        self.password.text = ""


class MainWindow(Screen):
    n = ObjectProperty(None)
    created = ObjectProperty(None)
    email = ObjectProperty(None)
    current = ""

    def logOut(self):
        sm.current = "login"

    def on_enter(self, *args):
        password, name, created = db.get_user(self.current)
        self.n.text = "Account Name: " + name
        self.email.text = "Email: " + self.current
        self.created.text = "Created On: " + created


class WindowManager(ScreenManager):
    pass
class CreateAccount(Screen):
    pass

class SetupInstruction(Screen):
    file_path = ObjectProperty(None)
    def open_chrome(self):
        webbrowser.open('https://console.cloud.google.com/apis/library/gmail.googleapis.com?project=ai-assistant-426202')

    def download_file(self):
        webbrowser.open('https://drive.google.com/file/d/1Yt64rk-hNogr1CCezDSL1vJuRh_cw7t-/view?usp=sharing')

    def upload_file(self):
        filechooser.open_file(on_selection=self.selected)

    def selected(self, selection):
        if selection:
            self.file_path = selection[0]  # Save the selected file path
            print(f"Selected file: {self.file_path}")

            # Define the destination directory and filename

            destination_dir = r'F:\DuoLink'
            destination_file = 'credentials.json'
            destination_path = os.path.join(destination_dir, destination_file)

            try:
                shutil.copy(self.file_path, destination_path)
                print(f"File saved to: {destination_path}")

                popup = Popup(title='File Selected',
                              content=Label(text=f'File saved to: {destination_path}'),
                              size_hint=(None, None), size=(400, 400))
                popup.open()

            except Exception as e:
                print(f"Error saving file: {e}")
                popup = Popup(title='Error',
                              content=Label(text=f'Error saving file: {e}'),
                              size_hint=(None, None), size=(400, 400))
                popup.open()

    def submit(self):
        if self.name.text != "" and self.email.text != "" and self.email.text.count("@") == 1 and self.email.text.count(".") > 0:
            if self.password != "":
                db.add_user(self.email.text, self.password.text, self.namee.text)
                self.reset()

                sm.current = "login"
            else:
                invalidForm()
        else:
            invalidForm()

    def create(self):
        print("Create button pressed")
        self.manager.current = 'create'

def invalidLogin():
    pop = Popup(title='Invalid Login',
                  content=Label(text='Invalid username or password.'),
                  size_hint=(None, None), size=(400, 400))
    pop.open()


def invalidForm():
    pop = Popup(title='Invalid Form',
                  content=Label(text='Please fill in all inputs with valid information.'),
                  size_hint=(None, None), size=(400, 400))

    pop.open()


kv = Builder.load_file("my.kv")

sm = WindowManager()
db = DataBase("users.txt")

screens = [LoginWindow(name="login"), CreateAccountWindow(name="create"), MainWindow(name="main"), SetupInstruction(name="setup")]
for screen in screens:
    sm.add_widget(screen)

sm.current = "login"


class MyMainApp(App):
    def build(self):
        return sm


if __name__ == "__main__":
    MyMainApp().run()