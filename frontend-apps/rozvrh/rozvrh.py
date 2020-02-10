"""rozvrh.py: ..."""
__author__ = "Robert Zentko"
__email__ = "robert.zentko@studenti.umb.sk"

# imports
import sys
import tkinter as tk
from datetime import datetime
from PIL import ImageTk, Image
import requests
import base_app

# settings
WIDTH = 1024  # 832  # 1336
HEIGHT = 768  # 624  # 768

APP_NAME = "rozvrh"
APP_TYPE = "app"

STUDY_PROGRAMMES = ("1nAIn", "2nAIn", "3nAIn")
TIME_UPDATE_INTERVAL = 1000
STUDY_PROGRAMME_UPDATE_INTERVAL = 4000


# APP_ID, NODE_NAME, NICKNAME, APPROBATION, RESPONSE_TOPIC = ()  # process_args(sys.argv, APP_NAME, APP_TYPE)


class CurrentClass(base_app.BaseApp):

    # render main layout
    def render_layout(self):
        # frame
        top_row = tk.Frame(self.window)
        top_row.pack(expand="false", fill="x", side="top")

        # logo UMB
        logo = tk.Label(top_row, image=self.image)
        logo.pack(side="left", fill="none", anchor="w", padx=32, pady=24)

        # clock
        self.clock.set(datetime.now().strftime("%H:%M"))
        time = tk.Label(top_row, textvariable=self.clock, anchor="w", font="{Open Sans} 32 bold", fg="#6e4a31")
        time.pack(side="right", fill="none", anchor="e", padx=32, pady=24)

        # subject
        self.subject.set("Predmet")
        subject = tk.Label(self.window, textvariable=self.subject, anchor="center", font="{Open Sans} 48 bold",
                           fg="#6e4a31", wraplengt=WIDTH - 100)
        subject.pack(side="top", fill="both", expand="true")

    # get current time
    def current_time(self):
        return datetime.now().strftime("%H:%M")

    # set subject
    def set_subject(self, subject):
        self.subject.set(subject)

    # update
    def update(self):
        self.clock.set(self.current_time())
        self.set_subject(STUDY_PROGRAMMES[self.current_programme] + ":\n\n" + self.fetch_subject())
        self.window.after(TIME_UPDATE_INTERVAL, self.update)

    # change current programme
    def change_current_programme(self):
        self.current_programme = 0 if self.current_programme == len(
            STUDY_PROGRAMMES) - 1 else self.current_programme + 1
        self.window.after(STUDY_PROGRAMME_UPDATE_INTERVAL, self.change_current_programme)

    # fetch subject
    def fetch_subject(self):
        response = requests.get(
            url="http://rozvrh.umb.sk/api/current-class/" + STUDY_PROGRAMMES[self.current_programme],
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        return response.json()[0]['subject']

    # run app
    def run(self):
        # init window
        window = tk.Tk()
        window.title("Aktuálny rozvrh - UMB")
        window.geometry(str(WIDTH) + "x" + str(HEIGHT))
        #        self.top = tkinter.Tk()
        #        self.top.wm_attributes('-type', 'splash')       # bez dekoracii
        #        self.top.wm_attributes('-fullscreen','true')
        #        self.top.geometry("{0}x{1}+0+0".format(self.top.winfo_screenwidth()-3, self.top.winfo_screenheight()-3))    # na celu obrazovku
        #        self.top.resizable(False, False)
        #        self.top.update_idletasks()
        #        self.top.overrideredirect(True)
        # fill window with content
        self.window = window
        self.clock = tk.StringVar()
        self.subject = tk.StringVar()
        self.image = ImageTk.PhotoImage(Image.open("assets/umb-logo.png"))
        self.current_programme = len(STUDY_PROGRAMMES) - 1
        self.change_current_programme()
        self.render_layout()

        self.update()

        # work
        self.window.mainloop()

    def stop(self):
        # zastav spracovanie mqtt
        super().stop()
        # zrus okno
        self.window.destroy()


if __name__ == '__main__':
    app = CurrentClass()
    app.process_args(sys.argv)
    app.start()

