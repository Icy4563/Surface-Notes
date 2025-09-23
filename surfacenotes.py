from PIL import ImageGrab, ImageFilter, ImageEnhance
shot = ImageGrab.grab()
from kivymd.app import MDApp
from kivy.metrics import sp
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.graphics.texture import Texture
from kivymd.uix.fitimage import FitImage
from kivy.core.text import LabelBase
from datetime import date
import time
import os
from kivymd.icon_definitions import md_icons
import sys
from string import Template
import glob
from kivy.clock import Clock

illegal_names = ["CON", "PRN", "AUX", "NUL", "COM1", 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

illegal_chars = ['<', '>', ':', '''"''', '/', '|'
                 '?', '*', "\\"]

currenttext = ""
name = None
engaged = False

KV = """

ScreenManager:
    EditorScreen:

<EditorScreen@MDScreen>:
    name: "EditorScreen"
    md_bg_color: 0, 0, 0, 0

    MDFloatLayout:
        id: layout

    MDScrollView:
        do_scroll_x: False
        do_scroll_y: True

        MDBoxLayout:
            adaptive_height: True

            MDLabel:
                text: "start typing, type '//help' for commands"
                font_style: 'IBM'
                role: "small"
                id: textbox
                size_hint_y: None
                height: self.texture_size[1]
                pos_hint: {'center_x': 0.5,'center_y': 0.5}
                theme_text_color: "Custom"
                text_color: "gray"
                valign: "top"
                halign: "left"
                text_size: (self.width, None)
                padding: "5sp", "5sp", 0, 0

    MDFloatLayout:

        MDLabel:
            text: ""
            font_style: 'IBM'
            role: "medium"
            id: notificationbox
            size_hint: None, None
            width: dp(275)
            text_size: self.width, None
            pos_hint: {'center_x': 0.865,'center_y': 0.815}
            theme_text_color: "Custom"
            text_color: 0.5424, 0.5706, 0.5837, 1
            halign: "center"
            valign: "center"
            padding: dp(10), dp(10)
            opacity: 0
            
            on_text:
                self.opacity = 0.0
                from kivy.animation import Animation
                animations = (
                Animation(opacity=1.375, duration=0.65)
                + Animation(duration=1.15)
                + Animation(opacity=0, duration=0.65, t="out_quad")
                )

                animations.start(self)
            on_texture_size:
                self.height = self.texture_size[1] + dp(6)
                notificationbg.size = (self.width + dp(20), self.height + dp(20))

        MDCard:
            style: "outlined"
            pos_hint: {'center_x': 0.865,'center_y': 0.815}
            theme_bg_color: "Custom"
            id: notificationbg
            size_hint: None, None
            md_bg_color: 0.4224, 0.449, 0.4636, 0.375
            radius: [dp(18), dp(18), dp(18), dp(18)]
            opacity: notificationbox.opacity
            size: notificationbox.size

        MDLabel:
            text: ""
            font_style: "IBM"
            role: "small"
            theme_text_color: "Custom"
            text_color: "white"
            size_hint: 0.3, 0.3
            halign: "center"
            valign: "center"
            opacity: 0.0
            pos_hint: {'center_x': 0.9765,'center_y': 0.99}
            id: time_label


                    
"""

def getMyFilePaths(relativePath):
    try:
        temp = sys._MEIPASS
    except:
        temp = os.path.abspath(".")

    return os.path.join(temp, relativePath)

def scanForFiles():
    extension = "*.txt"

    txt_files = glob.glob(extension)

    str_list = ""
    for n in txt_files:
        str_list += "\n"
        str_list += n

    return str_list

def getBlur(pilImage, **kwargs):
    pilImage = pilImage.filter(ImageFilter.GaussianBlur(6))
    darken = ImageEnhance.Brightness(pilImage)
    pilImage = darken.enhance(0.4)

    img = pilImage.convert("RGBA")
    w, h = img.size
    data = img.tobytes()

    kivyTexture = Texture.create(size=(w, h))
    kivyTexture.blit_buffer(data, colorfmt="rgba", bufferfmt="ubyte")

    kivyTexture.flip_vertical()
    newimg = FitImage(texture=kivyTexture, **kwargs)
    return newimg


class NotesApp(MDApp):

    def clock_function(self, dt):
        global engaged
        def run_clock():
            self.kv.get_screen("EditorScreen").ids.time_label.opacity = 0.9
            time_storage = time.strftime("%H:%M")
            self.kv.get_screen("EditorScreen").ids.time_label.text = str(time_storage)

        def clock_disabled():
            self.kv.get_screen("EditorScreen").ids.time_label.opacity = 0.0

        if engaged:
            run_clock()
        else:
            clock_disabled()

    def build(self):
        global shot
        LabelBase.register(name="IBM", fn_regular=getMyFilePaths("IBMPlexMono.ttf"))

        self.theme_cls.font_styles["IBM"] = {
            "large": {
                "line-height": 1.26,
                "font-name": "IBM",
                "font-size": sp(57),
            },
            "medium": {
                "line-height": 1.42,
                "font-name": "IBM",
                "font-size": sp(30),
            },
            "small": {
                "line-height": .9,
                "font-name": "IBM",
                "font-size": sp(20),
            },
        }

        Window.fullscreen = 'auto'
        self.kv = Builder.load_string(KV)
        self.shot = shot
        shot = getBlur(shot)

        self.kv.get_screen("EditorScreen").ids.layout.add_widget(shot)
        Window.bind(on_key_down=self.keyHandler)

        Clock.schedule_interval(self.clock_function, 1)
        return self.kv

    def check_name(self, nameIO):
        global illegal_chars, illegal_names
        windowsIlegalFile = False
        windowsIlegalCharacter = False

        #check for general windows illegal file names
        if any(var in nameIO.upper() for var in illegal_names):
            windowsIlegalFile = True
        else:
            #if no windows illegal file names are detected, check for illegal characters
            windowsIlegalFile = False

            if any(var in nameIO.upper() for var in illegal_chars):
                windowsIlegalCharacter = True

        if windowsIlegalFile or windowsIlegalCharacter:
            return "forbidden name or character, please edit your name and try again"
        
        else:
            return "ok"

    def save_name(self):
        global name, currenttext
        print("saving name")

        base = currenttext.find("//name=") + 7
        end = len(currenttext)

        name = currenttext[base:end]
        name = name[:-1]

        namespace = len(name) + 8
        currenttext = currenttext[:-namespace]

        if not self.check_name(name) == "ok":
            msg = self.check_name(name)
            name = None
            notification = Template("$message")
            notification = notification.substitute(message=msg)

        elif self.check_name(name) == "ok":
            msg = name
            notification = Template("name set to $message")
            notification = notification.substitute(message=msg)

        self.kv.get_screen("EditorScreen").ids.notificationbox.text = notification

    def keyHandler(self, window, key, scancode, codepoint, modifier):
        global currenttext, name, engaged
        self.kv.get_screen("EditorScreen").ids.textbox.text_color = "white"
        if isinstance(codepoint, str):
                if key == 301:
                     codepoint = ""
                if key == 304:
                     codepoint = ""
                if key == 309:
                    codepoint = ""
                if modifier == ['shift']:
                    if key == 47:
                          codepoint = "?"
                    elif key == 59:
                          codepoint = ":"
                    elif key == 49:
                          codepoint = "!"
                    elif key == 50:
                          codepoint = "@"
                    elif key == 51:
                          codepoint = "#"
                    elif key == 56:
                          codepoint = "*"
                    elif key == 57:
                          codepoint = "("
                    elif key == 48:
                          codepoint = ")"

                    else:
                        codepoint = codepoint.upper()
                elif modifier == ['capslock']:
                    codepoint = codepoint.upper()
                currenttext += codepoint

        if isinstance(key, int):
             if key == 8:
                currenttext = currenttext[:-1]

        if isinstance(key, int):
            if key == 13:
                currenttext += "\n"

                if not currenttext.find("//name=") == -1:
                    self.save_name()

                if not currenttext.find("//clock") == -1:
                    currenttext = currenttext[:-8]
                    if engaged:
                        engaged = False
                    else:
                        engaged = True

                if not currenttext.find("//scan") == -1:
                    currenttext = currenttext[:-7]
                    currenttext += scanForFiles()

                if not currenttext.find("//save") == -1:
                    if not name:
                        print("saving")
                        currenttext = currenttext[:-7]

                        with open("SurfaceNotes.txt", "a") as f:
                            currentdate = date.today()
                            currenttime = time.strftime("%H:%M")
                            timestuff = f"================{currentdate}, {currenttime}================\n\n"
                            f.write(timestuff)
                            f.write(currenttext)
                            f.close()

                        self.kv.get_screen("EditorScreen").ids.notificationbox.text = "saved succesfully"

                    else:
                        print("saving")
                        currenttext = currenttext[:-7]
                        pseudoname = f"{name}.txt"

                        with open(pseudoname, "a") as f:
                            currentdate = date.today()
                            currenttime = time.strftime("%H:%M")
                            timestuff = f"================{currentdate}, {currenttime}================\n\n"
                            f.write(timestuff)
                            f.write(currenttext)
                            f.close()

                        notification1 = Template("saved succesfully as $namename")
                        notification1 = notification1.substitute(namename=pseudoname)
                        self.kv.get_screen("EditorScreen").ids.notificationbox.text = notification1

                elif not currenttext.find("//overwrite") == -1:
                    if not name:
                        print("saving")
                        currenttext = currenttext[:-12]

                        with open("SurfaceNotes.txt", "w") as f:
                            currentdate = date.today()
                            currenttime = time.strftime("%H:%M")
                            timestuff = f"================{currentdate}, {currenttime}================\n\n"
                            f.write(timestuff)
                            f.write(currenttext)
                            f.close()

                        self.kv.get_screen("EditorScreen").ids.notificationbox.text = "overwritten succesfully"

                    else:
                        continueWriting = True
                        print("saving")
                        currenttext = currenttext[:-12]
                        currenttext = currenttext.splitlines()
                        try:
                            if not currenttext[0].find("================") == -1:
                                del currenttext[0]
                                currenttext = "\n".join(currenttext)
                            else:
                                currenttext = "\n".join(currenttext)
                        except IndexError:
                            self.kv.get_screen("EditorScreen").ids.notificationbox.text = "can't overwrite with an empty note"
                            continueWriting = False

                        if continueWriting:

                            pseudoname = f"{name}.txt"

                            with open(pseudoname, "w") as f:
                                currentdate = date.today()
                                currenttime = time.strftime("%H:%M")
                                timestuff = f"================{currentdate}, {currenttime}================\n\n"
                                f.write(timestuff)
                                f.write(currenttext)
                                f.close()

                            notification2 = Template("overwritten succesfully as $namename")
                            notification2 = notification2.substitute(namename=pseudoname)

                            self.kv.get_screen("EditorScreen").ids.notificationbox.text = notification2

                elif not currenttext.find("//open") == -1:
                    if not name:
                        print("opening")
                        currenttext = currenttext[:-6]

                        try:
                            with open("SurfaceNotes.txt") as f:
                                currenttext = f.read()
                                f.close()
                        except FileNotFoundError:
                            self.kv.get_screen("EditorScreen").ids.notificationbox.text = f"no notes saved to default file"

                    else:
                        print("opening")
                        currenttext = currenttext[:-6]
                        pseudoname = f"{name}.txt"

                        try:
                            with open(pseudoname) as f:
                                currenttext = f.read()
                                f.close()
                        except FileNotFoundError:
                            notification3 = Template("no notes saved to $namename")
                            notification3 = notification3.substitute(namename=pseudoname)

                            self.kv.get_screen("EditorScreen").ids.notificationbox.text = notification3

                elif not currenttext.find("//clear") == -1:
                    currenttext = ""

        if len(currenttext) >= 0:
            if len(currenttext) == 0:
                self.kv.get_screen("EditorScreen").ids.textbox.text = '''start typing, type '//help' for commands'''
                self.kv.get_screen("EditorScreen").ids.textbox.text_color = "gray"

            else:
                currenttext = str(currenttext)
                self.kv.get_screen("EditorScreen").ids.textbox.text = currenttext

        if isinstance(currenttext, str):
            if not currenttext.find("//help") == -1:
                currenthelptext = ">type '//help' to access this menu\n\n>type '//save' to save your notes. It will save to 'SurfaceNotes.txt' in the same folder as this app. Any new notes will be saved in the same file\n\n>type '//open' to open and read the saved notes.\n\n>Note: use '//overwrite' to overwrite the default save file instead of continuing to it\n\n>Note: use '//name=' to name your file. You need to do this before saving or opening. You can also use this command to open a specific file. Names cannot contain '.txt' or spaces\n\n>Note: press 'esc' to exit Surface Notes"
                self.kv.get_screen("EditorScreen").ids.textbox.text = currenthelptext
            else:
                pass
        else:
            pass

NotesApp().run()
