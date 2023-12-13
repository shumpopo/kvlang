from kivy.animation import Animation
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.dialog import MDDialog
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.utils import rgba
import datetime
import json
import re
import pyaudio
import pyttsx3
import speech_recognition as sr
import requests
import pyrebase
from firebase import firebase

# Training data-----------------
import numpy as np
from tensorflow import keras
from sklearn.preprocessing import LabelEncoder
import colorama

colorama.init()
from colorama import Fore, Style, Back
import random
import pickle

# Firebase/Pyrebase-----------------------------------------------------------------------------------------------------
firebaseConfig = {
    'apiKey': "AIzaSyC8y4Qv-20aS701U6OeawNySy7VkrmEcEw",
    'databaseURL': "https://aiproject-db-default-rtdb.firebaseio.com/",
    'authDomain': "aiproject-db.firebaseapp.com",
    'projectId': "aiproject-db",
    'storageBucket': "aiproject-db.appspot.com",
    'messagingSenderId': "88380585609",
    'appId': "1:88380585609:web:98a89b3b32afc2b191f858",
    'measurementId': "G-ME9WFNYR6M"
}

Firebase = pyrebase.initialize_app(firebaseConfig)
auth = Firebase.auth()

firebase = firebase.FirebaseApplication('https://aiproject-db-default-rtdb.firebaseio.com/', None)

# Kivy Window-----------------------------------------------------------------------------------------------------------
Window.size = (315, 650)

# Speak Engine----------------------------------------------------------------------------------------------------------
engine = pyttsx3.init()


# Screen display classes------------------------------------------------------------------------------------------------
class Command(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "fonts/PoppinsEL.otf"
    font_size = 14


class Response(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "fonts/PoppinsEL.otf"
    font_size = 14


class User_data(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "fonts/PoppinsEL.otf"
    font_size = 13


class Admin_User_data(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "fonts/PoppinsEL.otf"
    font_size = 13
    pos_hint = {"center_y": .5}

# Outside function method-----------------------------------------------------------------------------------------------
def is_cnx_active():
    while True:
        try:
            requests.head("https://www.google.com/", timeout=1)
            print("The internet connection is active")
            break
        except requests.ConnectionError:
            Snackbar(text="Please check your Internet connection!",
                     snackbar_animation_dir="Top",
                     font_size='12sp',
                     snackbar_x=.1,
                     size_hint_x=.999,
                     size_hint_y=.07,
                     bg_color=(1, 0, 0, 1)
                     ).open()
            break


# Main application------------------------------------------------------------------------------------------------------
class TCUAdvisor(MDApp):
    def build(self):

        self.icon = "assets/TCULogo.jpg"

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.material_style = "M3"

        global screen
        screen = ScreenManager(transition=SlideTransition(duration=.7))
        screen.add_widget(Builder.load_file("kivy/Introduction.kv"))
        screen.add_widget(Builder.load_file("kivy/Login.kv"))
        screen.add_widget(Builder.load_file("kivy/Register.kv"))
        screen.add_widget(Builder.load_file("kivy/Admin_login.kv"))
        screen.add_widget(Builder.load_file("kivy/Admin_Home-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Welcome-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Home-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Notification-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Profile-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Setting-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/About.kv"))
        screen.add_widget(Builder.load_file("kivy/Forgot-password.kv"))
        screen.add_widget(Builder.load_file("kivy/Terms&Condition.kv"))
        screen.add_widget(Builder.load_file("kivy/Terms&Condition1.kv"))

        screen.add_widget(Builder.load_file("kivy/Love_message-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Love_command.kv"))

        screen.add_widget(Builder.load_file("kivy/Academic_message-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Academic_command.kv"))

        screen.add_widget(Builder.load_file("kivy/Family_message-screen.kv"))
        screen.add_widget(Builder.load_file("kivy/Family_command.kv"))
        return screen

    # Voices------------------------------------------------------------------------------------------------------------

    def speak_male(self, text):
        engine.setProperty('rate', 160)
        engine.setProperty('pitch', 100)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)

        engine.say(text)
        engine.runAndWait()

    def speak_female(self, text):
        engine.setProperty('rate', 160)
        engine.setProperty('pitch', 100)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[0].id)

        engine.say(text)
        engine.runAndWait()

    # Love Command & Responses -----------------------------------------------------------------------------------------

    def send_love(self):
        with open("json/love_intents.json") as file:
            data = json.load(file)

        # load trained model
        model = keras.models.load_model('chat_model_love')

        # load tokenizer object
        with open('pickles/love_tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('pickles/love_label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        if screen.get_screen('Love_message-screen').text_input != "":
            inp = screen.get_screen('Love_message-screen').text_input.text

            if len(inp) < 6:
                size = .22
                halign = "center"
            elif len(inp) < 11:
                size = .32
                halign = "center"
            elif len(inp) < 16:
                size = .45
                halign = "center"
            elif len(inp) < 21:
                size = .58
                halign = "center"
            elif len(inp) < 26:
                size = .71
                halign = "center"
            else:
                size = .77
                halign = "left"

            screen.get_screen('Love_message-screen').chat_list.add_widget(
                Command(text=inp, size_hint_x=size, halign=halign))

            result = model.predict(
                keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]), truncating='post',
                                                           maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    if len(inp) < 6:
                        size = .45
                        halign = "left"
                    elif len(inp) < 11:
                        size = .50
                        halign = "left"
                    elif len(inp) < 16:
                        size = .60
                        halign = "left"
                    elif len(inp) < 21:
                        size = .70
                        halign = "left"
                    elif len(inp) < 26:
                        size = .70
                        halign = "left"
                    else:
                        size = .70
                        halign = "justify"
                    screen.get_screen('Love_message-screen').chat_list.add_widget(
                        Response(text=np.random.choice(i['responses']), size_hint_x=size, halign=halign))

                    screen.get_screen('Love_message-screen').text_input.text = ""

    def love_command(self):
        with open("json/love_intents.json") as file:
            data = json.load(file)

        # load trained model
        model = keras.models.load_model('chat_model_love')

        # load tokenizer object
        with open('pickles/love_tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('pickles/love_label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source)
            text = r.listen(source)
        try:
            print("Recognizing...")
            command = r.recognize_google(text, language='kivy-in')

            result = model.predict(
                keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([command]), truncating='post',
                                                           maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    self.speak_male(np.random.choice(i['responses']))

            return

        except Exception as e:
            print(e)

            return "None"

    def send_academic(self):
        with open("json/academic_intents.json") as file:
            data = json.load(file)

        # load trained model
        model = keras.models.load_model('chat_model_academic')

        # load tokenizer object
        with open('pickles/academic_tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('pickles/academic_label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        if screen.get_screen('Academic_message-screen').text_input != "":
            inp = screen.get_screen('Academic_message-screen').text_input.text

            if len(inp) < 6:
                size = .22
                halign = "center"
            elif len(inp) < 11:
                size = .32
                halign = "center"
            elif len(inp) < 16:
                size = .45
                halign = "center"
            elif len(inp) < 21:
                size = .58
                halign = "center"
            elif len(inp) < 26:
                size = .71
                halign = "center"
            else:
                size = .77
                halign = "left"

            screen.get_screen('Academic_message-screen').chat_list.add_widget(
                Command(text=inp, size_hint_x=size, halign=halign))

            result = model.predict(
                keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]), truncating='post',
                                                           maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    screen.get_screen('Academic_message-screen').chat_list.add_widget(
                        Response(text=np.random.choice(i['responses']), size_hint_x=.5, halign="justify"))

                    screen.get_screen('Academic_message-screen').text_input.text = ""

    def command_academic(self):
        with open("json/academic_intents.json") as file:
            data = json.load(file)

        # load trained model
        model = keras.models.load_model('chat_model_academic')

        # load tokenizer object
        with open('pickles/academic_tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('pickles/academic_label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Listening . . .")
            r.pause_threshold = 1
            text = r.listen(source)
        try:
            print("Recognizing. . .")
            command = r.recognize_google(text, language='kivy-in')

            result = model.predict(
                keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([command]), truncating='post',
                                                           maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    self.speak_male(np.random.choice(i['responses']))

            return

        except Exception as e:
            print(e)

            return "None"

    def send_family(self):
        with open("json/family_intents.json") as file:
            data = json.load(file)

        # load trained model
        model = keras.models.load_model('chat_model_family')

        # load tokenizer object
        with open('pickles/family_tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('pickles/family_label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        if screen.get_screen('Family_message-screen').text_input != "":
            inp = screen.get_screen('Family_message-screen').text_input.text

            if len(inp) < 6:
                size = .22
                halign = "center"
            elif len(inp) < 11:
                size = .32
                halign = "center"
            elif len(inp) < 16:
                size = .45
                halign = "center"
            elif len(inp) < 21:
                size = .58
                halign = "center"
            elif len(inp) < 26:
                size = .71
                halign = "center"
            else:
                size = .77
                halign = "left"

            screen.get_screen('Family_message-screen').chat_list.add_widget(
                Command(text=inp, size_hint_x=size, halign=halign))

            result = model.predict(
                keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([inp]), truncating='post',
                                                           maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    screen.get_screen('Family_message-screen').chat_list.add_widget(
                        Response(text=np.random.choice(i['responses']), size_hint_x=.5, halign="justify"))

                    screen.get_screen('Family_message-screen').text_input.text = ""

    def command_family(self):
        with open("json/family_intents.json") as file:
            data = json.load(file)

        # load trained model
        model = keras.models.load_model('chat_model_family')

        # load tokenizer object
        with open('pickles/family_tokenizer.pickle', 'rb') as handle:
            tokenizer = pickle.load(handle)

        # load label encoder object
        with open('pickles/family_label_encoder.pickle', 'rb') as enc:
            lbl_encoder = pickle.load(enc)

        # parameters
        max_len = 20

        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Listening . . .")
            r.pause_threshold = 1
            text = r.listen(source)
        try:
            print("Recognizing. . .")
            command = r.recognize_google(text, language='kivy-in')

            result = model.predict(
                keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([command]), truncating='post',
                                                           maxlen=max_len))
            tag = lbl_encoder.inverse_transform([np.argmax(result)])

            for i in data['intents']:
                if i['tag'] == tag:
                    self.speak_male(np.random.choice(i['responses']))

            return

        except Exception as e:
            print(e)

            return "None"

    # User Registration----------------------------------------------------------------------------------------------------

    def register(self, email, password, confirmpassword, fname, lname, stud_id, year, course, section):
        result = firebase.get('aiproject-db-default-rtdb/Users', '')
        for i in result.keys():
            if any(field == "" for field in
                   [email, password, confirmpassword, fname, lname, stud_id, year, course, section]):
                Snackbar(text="Please fill out all fields!",
                         snackbar_animation_dir="Top",
                         font_size='12sp',
                         snackbar_x=.1,
                         size_hint_x=.999,
                         size_hint_y=.07,
                         bg_color=(1, 0, 0, 1)
                         ).open()
                return

            if len(password) < 6:
                Snackbar(text="Weak Password!",
                         snackbar_animation_dir="Top",
                         font_size='12sp',
                         snackbar_x=.1,
                         size_hint_x=.999,
                         size_hint_y=.07,
                         bg_color=(1, 0, 0, 1)
                         ).open()

            if stud_id == result[i]['Student ID']:
                Snackbar(text="Student ID already used!",
                         snackbar_animation_dir="Top",
                         font_size='12sp',
                         snackbar_x=.1,
                         size_hint_x=.999,
                         size_hint_y=.07,
                         bg_color=(1, 0, 0, 1)
                         ).open()

            else:
                try:
                    if password == confirmpassword:
                        screen = self.root.get_screen('Register')
                        if screen.ids.checkbox.active:
                            auth.create_user_with_email_and_password(email, password)
                            Snackbar(text="Registered Successfully!",
                                     snackbar_animation_dir="Top",
                                     font_size='12sp',
                                     snackbar_x=.1,
                                     size_hint_x=.999,
                                     size_hint_y=.07,
                                     bg_color="#000000"
                                     ).open()

                            data = {
                                'First Name': fname,
                                'Last Name': lname,
                                'Student ID': stud_id,
                                'Year': year,
                                'Course': course,
                                'Section': section,
                                'Email': email,
                                'Password': password
                            }

                            firebase.post('aiproject-db-default-rtdb/Users', data)
                            self.clear_registration_fields()
                            self.root.current = 'Login'
                        else:
                            Snackbar(text="Accept terms & Condition!",
                                     snackbar_animation_dir="Top",
                                     font_size='12sp',
                                     snackbar_x=.1,
                                     size_hint_x=.999,
                                     size_hint_y=.07,
                                     bg_color=(1, 0, 0, 1)
                                     ).open()
                    else:
                        Snackbar(text="Invalid Confirm Password!",
                                 snackbar_animation_dir="Top",
                                 font_size='12sp',
                                 snackbar_x=.1,
                                 size_hint_x=.999,
                                 size_hint_y=.07,
                                 bg_color=(1, 0, 0, 1)
                                 ).open()

                except:
                    Snackbar(text="Email already existed!",
                             snackbar_animation_dir="Top",
                             font_size='12sp',
                             snackbar_x=.1,
                             size_hint_x=.999,
                             size_hint_y=.07,
                             bg_color=(1, 0, 0, 1)
                             ).open()

    # Admin & User Login----------------------------------------------------------------------------------------------------
    def user_login(self, email, password):
        try:
            auth.sign_in_with_email_and_password(email, password)

            self.root.current = 'Welcome-screen'
            self.carousel_autonext()
            self.clear_user_login_fields()

            result = firebase.get('aiproject-db-default-rtdb/Users', '')
            for i in result.keys():

                if email == result[i]['Email']:
                    screen.get_screen('Setting-screen').add_widget(
                        User_data(text=result[i]['First Name'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': 0.76, 'center_y': 0.87}))

                    screen.get_screen('Setting-screen').add_widget(
                        User_data(text=result[i]['Last Name'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': 1.03, 'center_y': 0.87}))

                    screen.get_screen('Profile-screen').add_widget(
                        User_data(text=result[i]['First Name'] + " " + result[i]['Last Name'],
                                  font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': .75, 'center_y': 0.61}))

                    screen.get_screen('Profile-screen').add_widget(
                        User_data(text=result[i]['Student ID'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': .75, 'center_y': 0.51}))

                    screen.get_screen('Profile-screen').add_widget(
                        User_data(text=result[i]['Year'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': .75, 'center_y': 0.41}))

                    screen.get_screen('Profile-screen').add_widget(
                        User_data(text=result[i]['Course'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': .95, 'center_y': 0.41}))

                    screen.get_screen('Profile-screen').add_widget(
                        User_data(text=result[i]['Section'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': .75, 'center_y': 0.31}))

                    screen.get_screen('Profile-screen').add_widget(
                        User_data(text=result[i]['Email'], font_name="fonts/OpenSans-Semibold.ttf",
                                  pos_hint={'center_x': .75, 'center_y': 0.21}))

        except:
            Snackbar(text="Invalid Email or Password!",
                     snackbar_animation_dir="Top",
                     font_size='12sp',
                     snackbar_x=.1,
                     size_hint_x=.999,
                     size_hint_y=.07,
                     bg_color=(1, 0, 0, 1)
                     ).open()
            return

    def admin_login(self, admin_id, admin_password):
        result = firebase.get('aiproject-db-default-rtdb/Admin', '')
        for i in result.keys():
            if result[i]['Admin ID'] == admin_id:
                if result[i]['Admin Password'] == admin_password:
                    self.root.current = 'Adminhome'
                    self.clear_admin_login_fields()
                    return

        for i in result.keys():
            if result[i]['Admin ID'] == admin_id:
                if result[i]['Admin Password'] != admin_password:
                    Snackbar(text="Invalid ID or Password!",
                             snackbar_animation_dir="Top",
                             font_size='12sp',
                             snackbar_x=.1,
                             size_hint_x=.999,
                             size_hint_y=.07,
                             bg_color=(1, 0, 0, 1)
                             ).open()
                    return

        for i in result.keys():
            if result[i]['Admin ID'] != admin_id:
                if result[i]['Admin Password'] == admin_password:
                    Snackbar(text="Invalid ID or Password!",
                             snackbar_animation_dir="Top",
                             font_size='12sp',
                             snackbar_x=.1,
                             size_hint_x=.999,
                             size_hint_y=.07,
                             bg_color=(1, 0, 0, 1)
                             ).open()
                    return

        for i in result.keys():
            if result[i]['Admin ID'] != admin_id:
                if result[i]['Admin Password'] != admin_password:
                    Snackbar(text="Invalid ID or Password!",
                             snackbar_animation_dir="Top",
                             font_size='12sp',
                             snackbar_x=.1,
                             size_hint_x=.999,
                             size_hint_y=.07,
                             bg_color=(1, 0, 0, 1)
                             ).open()
                    return

    # Clearing Inputs-------------------------------------------------------------------------------------------------------
    def clear_registration_fields(self):
        screen = self.root.get_screen('Register')
        screen.ids.stud_id.text = ""
        screen.ids.fname.text = ""
        screen.ids.lname.text = ""
        screen.ids.year.text = ""
        screen.ids.course.text = ""
        screen.ids.section.text = ""
        screen.ids.email.text = ""
        screen.ids.password.text = ""
        screen.ids.confirmpassword.text = ""

    def clear_admin_login_fields(self):
        screen = self.root.get_screen('Admin_login')
        screen.ids.admin_id.text = ""
        screen.ids.admin_password.text = ""

    def clear_user_login_fields(self):
        screen = self.root.get_screen('Login')
        screen.ids.email.text = ""
        screen.ids.password.text = ""

    # Admin & User Logout---------------------------------------------------------------------------------------------------

    def user_logout(self):
        Snackbar(text="Logged out successful!",
                 snackbar_animation_dir="Top",
                 font_size='12sp',
                 snackbar_x=.1,
                 size_hint_x=.999,
                 size_hint_y=.07,
                 bg_color=(1, 0, 0, 1)
                 ).open()

        self.root.current = 'Login'

    def admin_logout(self):
        Snackbar(text="Logged out successful!",
                 snackbar_animation_dir="Top",
                 font_size='12sp',
                 snackbar_x=.1,
                 size_hint_x=.999,
                 size_hint_y=.07,
                 bg_color=(1, 0, 0, 1)
                 ).open()
        self.root.current = 'Admin_login'

    # Display Users profile & Admin Homescreen users---------------------------------------------------------------------------------------------------------------
    def display_all_user(self):
        result = firebase.get('aiproject-db-default-rtdb/Users', '')
        for i in result.keys():
            screen.get_screen('Adminhome').user_list.add_widget(
                Admin_User_data(text="Name:               " + result[i]['First Name'] + " " + result[i]['Last Name'],
                                font_name="fonts/OpenSans-Bold.ttf",
                                pos_hint={"center_x": .52, "center_y": .5}, font_size=14))

            screen.get_screen('Adminhome').user_list.add_widget(
                Admin_User_data(text="Student ID:            " + result[i]['Student ID'],
                                font_name="fonts/OpenSans-Semibold.ttf",
                                pos_hint={"center_x": .52, "center_y": .5}))

            screen.get_screen('Adminhome').user_list.add_widget(
                Admin_User_data(text="Year & Course:     " + result[i]['Year'] + " - " + result[i]['Course'],
                                font_name="fonts/OpenSans-Semibold.ttf",
                                pos_hint={"center_x": .52, "center_y": .5}))

            screen.get_screen('Adminhome').user_list.add_widget(
                Admin_User_data(text="Section:                   " + result[i]['Section'],
                                font_name="fonts/OpenSans-Semibold.ttf",
                                pos_hint={"center_x": .52, "center_y": .5}))

            screen.get_screen('Adminhome').user_list.add_widget(
                Admin_User_data(text="Email:                      " + result[i]['Email'],
                                font_name="fonts/OpenSans-Semibold.ttf",
                                pos_hint={"center_x": .52, "center_y": .5}))

            screen.get_screen('Adminhome').user_list.add_widget(
                Admin_User_data(text="---------------------------------------------------", opacity=.5))

    # other functions--------------------------------------------------------------------------------------------------
    def carousel_autonext(self):
        screen = self.root.get_screen('Welcome-screen')
        carousel = screen.ids.carousel
        Clock.schedule_interval(carousel.load_next, 4)

        screen = self.root.get_screen('Setting-screen')
        carousel_1 = screen.ids.carousel_1
        carousel_1.loop = True
        Clock.schedule_interval(carousel_1.load_next, 3)

    def current_slide(self, index):
        screen = self.root.get_screen('Welcome-screen')
        for i in range(2):
            if index == i:
                screen.ids[f"slide{index}"].color = rgba(255, 0, 0, 255)
            else:
                screen.ids[f"slide{i}"].color = rgba(170, 170, 170, 255)

        screen = self.root.get_screen('Register')
        for i in range(2):
            if index == i:
                screen.ids[f"slide{index}"].color = rgba(255, 0, 0, 255)
            else:
                screen.ids[f"slide{i}"].color = rgba(170, 170, 170, 255)

    def reset_password(self, email):
        try:
            auth.send_password_reset_email(email)
            dialog = MDDialog(title="Email Verification", text="Please check your email address.",
                              pos_hint={"center_x": .5, "center_y": .85})
            dialog.open()
            self.root.current = 'Login'
        except:
            Snackbar(text="Invalid Email!",
                     snackbar_animation_dir="Top",
                     font_size='12sp',
                     snackbar_x=.1,
                     size_hint_x=.999,
                     size_hint_y=.07,
                     bg_color=(1, 0, 0, 1)
                     ).open()

    def next(self):
        screen = self.root.get_screen('Register')
        carousel = screen.ids.carousel
        carousel.load_next(mode="next")


    def on_touch(self, instance):
        pass

    def on_start(self):
        Clock.schedule_once(self.start, 0)

    def start(self, *args):
        self.root.current = "Home-screen"
        is_cnx_active()
        self.display_all_user()


if __name__ == "__main__":
    TCUAdvisor().run()

# -----------------------------------------------------
# screen = self.root.get_screen('Login')
# bg_image = screen.ids.bg_image
# Animation(x=-dp(300), d=30).start(bg_image)
