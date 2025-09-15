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

currenttext = ""

KV = """

ScreenManager:
    EditorScreen:

<EditorScreen@MDScreen>:
    name: "EditorScreen"
    md_bg_color: 0, 0, 0, 0

    MDFloatLayout:
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


"""
def getMyFilePaths(relativePath):
    try:
        temp = sys._MEIPASS
    except:
        temp = os.path.abspath(".")

    return os.path.join(temp, relativePath)


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
                "font-size": sp(45),
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

        return self.kv
    
    def keyHandler(self, window, key, scancode, codepoint, modifier):
        global currenttext
        self.kv.get_screen("EditorScreen").ids.textbox.text_color = "white"
        print("key", key)
        if isinstance(codepoint, str):
                if key == 301:
                     codepoint = ""
                if key == 304:
                     codepoint = ""
                if modifier == ['shift']:
                    print("shifting")
                    if key == 47:
                          codepoint = "?"
                    elif key == 32:
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
                    print("shifting")
                    codepoint = codepoint.upper()
                currenttext += codepoint

        if isinstance(key, int):
             if key == 8:
                currenttext = currenttext[:-1]
                print("removed", currenttext)

        if isinstance(key, int):
             if key == 13:
                  currenttext += "\n"

        if len(currenttext) >= 0:
            currenttext = str(currenttext)
            self.kv.get_screen("EditorScreen").ids.textbox.text = currenttext

        if not currenttext.find("//save") == -1:
            print("saving")
            currenttext = currenttext[:-6]

            with open("SurfaceNotes.txt", "a") as f:
                 currentdate = date.today()
                 currenttime = time.strftime("%H:%M")
                 timestuff = f"================{currentdate}, {currenttime}================\n\n"
                 f.write(timestuff)
                 f.write(currenttext)
                 f.close()

        elif not currenttext.find("//overwrite") == -1:
            print("saving")
            currenttext = currenttext[:-12]

            with open("SurfaceNotes.txt", "w") as f:
                 currentdate = date.today()
                 currenttime = time.strftime("%H:%M")
                 timestuff = f"================{currentdate}, {currenttime}================\n\n"
                 f.write(timestuff)
                 f.write(currenttext)
                 f.close()

        elif not currenttext.find("//open") == -1:
            print("opening")
            currenttext = currenttext[:-6]

            with open("SurfaceNotes.txt") as f:
                 currenttext = f.read()
                 f.close()

        elif not currenttext.find("//help") == -1:
            print("opening")
            currenthelptext = ">type '//help' to access this menu\n\n>type '//save' to save your notes. It will save to 'SurfaceNotes.txt' in the same folder as this app. Any new notes will be saved in the same file\n\n>type '//open' to open and read the saved notes.\n\n>Note: use '//overwrite' to overwrite the save file instead of continuing to it"
            self.kv.get_screen("EditorScreen").ids.textbox.text = currenthelptext
            currenttext = ""

        else:
            pass

NotesApp().run()