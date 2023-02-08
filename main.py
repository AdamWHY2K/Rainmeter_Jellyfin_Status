import logging
import requests
import re
import sys
from time import sleep

class User():
    def __init__(self, UserId, UserName, CurrentPlaying, Client, Transcoding, RuntimeTicks, PositionTicks) -> None:
        self.id = UserId
        self.name = UserName
        self.playing = CurrentPlaying
        self.client = Client
        self.total_time = RuntimeTicks
        self.current_time = PositionTicks
        if Transcoding == "Transcode":
            self.transcode = "(T)"
        else:
            self.transcode = "(D)"
        if CurrentPlaying != None:
            convert_ticks = round((self.total_time - self.current_time) * 1/10000000 / 60, 2)
            minutes = str(int(convert_ticks))
            seconds = str(int(convert_ticks % 1 * 60))
            if int(seconds) < 10:
                seconds = "0" + seconds
            self.minutes_left = minutes + " min, " + seconds + " sec"
            self.alt_minutes_left = minutes + ":" + seconds
            self.percentage_done = round((self.current_time / self.total_time) * 100, 2)
        else:
            self.minutes_left = 0
            self.percentage_done = 0

        self.badchars = ["‐", "’", "¡", "¢", "£", "¤", "¥", "¦", "§", "¨", "©", "ª", "«", "¬", "®", "¯", "°", "±", "²", "³", "´", "µ", "¶","·", "¸", "¹", "º", "»", "¼", "½", "¾", "¿", "À", "Á", "Â", "Ã", "Ä", "Å", "Æ", "Ç", "È", "É", "Ê", "Ë", "Ì", "Í", "Î", "Ï", "Ð", "Ñ", "Ò", "Ó", "Ô", "Õ", "Ö", "×", "Ø", "Ù", "Ú", "Û", "Ü", "Ý", "Þ", "ß", "à", "á", "â", "ã", "ä", "å", "æ", "ç", "è", "é", "ê", "ë", "ì", "í", "î", "ï", "ð", "ñ", "ò", "ó", "ô", "õ", "ö", "÷", "ø", "ù", "ú", "û", "ü", "ý", "þ", "ÿ", "ƒ", "Α", "Β", "Γ", "Δ", "Ε", "Ζ", "Η", "Θ", "Ι", "Κ", "Λ", "Μ", "Ν", "Ξ", "Ο", "Π", "Ρ", "Σ", "Τ", "Υ", "Φ", "Χ", "Ψ", "Ω", "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", "ν", "ξ", "ο", "π", "ρ", "ς", "σ", "τ", "υ", "φ", "χ", "ψ", "ω", "ϑ", "ϒ", "ϖ", "•", "…", "′", "″", "‾", "⁄", "℘", "ℑ", "ℜ", "™", "ℵ", "←", "↑", "→", "↓", "↔", "↵", "⇐", "⇑", "⇒", "⇓", "⇔", "∀", "∂", "∃", "∅", "∇", "∈", "∉", "∋", "∏", "∑", "−", "∗", "√", "∝", "∞", "∠", "∧", "∨", "∩", "∪", "∫", "∴", "∼", "≅", "≈", "≠", "≡", "≤", "≥", "⊂", "⊃", "⊄", "⊆", "⊇", "⊕", "⊗"] 
        #Rainmeter throws a fit when these characters are in a string... theres gotta be a better way of detecting badchars than this :/
        self.output = "<name>" + self.name + "<name>" + "<playing>" + str(self.playing) + "<playing>" + "<client>" + self.client + "<client>" + "<transcode>" + self.transcode + "<transcode>" + "<minutes_left>" + str(self.minutes_left) + "<minutes_left>" + "<percentage_done>" + str(self.percentage_done) + "<percentage_done>" + "JFS_EOL_SIG"
        for i in self.badchars:
            if i in self.output:
                self.output = self.output.replace(i, "")
        print(self.output)

class App():
    def __init__(self, ip, api) -> None:
        logging.basicConfig(
            filename='JF_Status.log',
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y/%m/%d %I:%M:%S %p',
            filemode = 'w')
        logging.info("STARTING JF_Status")
        self.ip = ip
        self.api = api
        self.sessions = []
        self.users = {}
        JF_Status_github = requests.get("https://api.github.com/repos/AdamWHY2K/Rainmeter_Jellyfin_Stats/releases")
        self.current_version = "1.0.0"
        try:
            self.latest_version = JF_Status_github.json()[0]["tag_name"][1:]
            self.changelog = JF_Status_github.json()[0]["body"]
            self.download_link = JF_Status_github.json()[0]["assets"][0]["browser_download_url"]
        except KeyError:
            logging.warning("GitHub API limit exceeded, couldn't check for updates.")
            self.latest_version = "0"
            self.changelog = "Not Found"
            self.download_link = ""

    def connect(self):
        url = "http://" + self.ip + "/Sessions"
        key = {"api_key": self.api}
        return requests.get(url, key).json()

    def get_sessions(self):
        for i in self.connect():
            self.sessions.append(i)
            
    def create_users(self):
        for i in self.sessions:
            try:
                self.users[i["UserId"]] = User(i["UserId"], i["UserName"], re.split("([^\/\\\]+)$", i["NowPlayingItem"]["Path"])[1], i["Client"], i["PlayState"]["PlayMethod"], i["NowPlayingItem"]["RunTimeTicks"], i["PlayState"]["PositionTicks"])
            except KeyError:
                self.users[i["UserId"]] = User(i["UserId"], i["UserName"], None, i["Client"], None, None, None)

if __name__ == "__main__":
    try:
        myApp = App(sys.argv[1], sys.argv[2])
        myApp.get_sessions()
        myApp.create_users()
    except IndexError:
        pass