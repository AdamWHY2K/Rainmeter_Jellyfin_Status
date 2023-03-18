import logging
import requests
import re
import sys
from time import sleep
from wmi import WMI
from pymsgbox import confirm
import webbrowser


class User():
    def __init__(self, UserId, UserName, CurrentPlaying, Client, Transcoding, RuntimeTicks, PositionTicks, IsPaused, DeviceName, NumberOfSessions):
        self.id = UserId
        self.name = "<name>" + UserName + "<name>"
        self.client = "<client>" + Client + "<client>"
        self.device_name = "<device_name>" + DeviceName + "<device_name>"
        self.total_time = RuntimeTicks
        self.current_time = PositionTicks
        self.number_of_sessions = "<number_of_sessions>" + str(NumberOfSessions) + "<number_of_sessions>"
        if CurrentPlaying != None:
            self.playing = "<playing>" + CurrentPlaying + "<playing>"
            if Transcoding == "Transcode":
                self.transcode = "<transcode>(T)<transcode>"
            else:
                self.transcode = "<transcode>(D)<transcode>"
            convert_ticks = round((self.total_time - self.current_time) * 1/10000000 / 60, 2)
            minutes = str(int(convert_ticks))
            seconds = str(int(convert_ticks % 1 * 60))
            if int(seconds) < 10:
                seconds = "0" + seconds
            self.minutes_left = "<minutes_left>" + minutes + " min, " + seconds + " sec<minutes_left>"
            self.alt_minutes_left = "<alt_minutes_left>" + minutes + ":" + seconds + "<alt_minutes_left>"
            self.percentage_done = "<percentage_done>" + str(round((self.current_time / self.total_time) * 100, 2)) + "<percentage_done>"
            if IsPaused:
                self.play_status = "<play_status>[II]<play_status>"
            else:
                self.play_status = "<play_status>[>]<play_status>"
        else:
            self.playing = "<playing>Online<playing>"
            self.transcode = "<transcode><transcode>"
            self.minutes_left = "<minutes_left><minutes_left>"
            self.alt_minutes_left = "<alt_minutes_left><alt_minutes_left>"
            self.percentage_done = "<percentage_done>0<percentage_done>"
            self.play_status = "<play_status>[X]<play_status>"

        self.output = self.name + self.playing + self.client + self.transcode + self.minutes_left + self.alt_minutes_left + self.percentage_done + self.play_status + self.device_name + self.number_of_sessions + "JFS_EOL_SIG"

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
                self.users[i["UserId"]] = User(i["UserId"], i["UserName"], re.split("([^\/\\\]+)$", i["NowPlayingItem"]["Path"])[1], i["Client"], i["PlayState"]["PlayMethod"], i["NowPlayingItem"]["RunTimeTicks"], i["PlayState"]["PositionTicks"], i["PlayState"]["IsPaused"], i["DeviceName"],  len(self.sessions))
            except KeyError:
                self.users[i["UserId"]] = User(i["UserId"], i["UserName"], None, i["Client"], None, None, None, None, i["DeviceName"], len(self.sessions))

    def write_users(self):
        with open("py_out.txt", "wb") as f:
            for i in dict(sorted(self.users.items())): #Sorted so it prints in a consistent order
                f.write(self.users[i].output.encode("ascii", errors='replace')) #Rainmeter really doesn't like chars that aren't in the basic 128 ascii range, incompatible chars will be replaced with a ?

def check_for_updates():
    #Check for updates, doing this outside of the main program so it only checks once per load; instead of every 60 seconds.
    JF_Status_github = requests.get("https://api.github.com/repos/AdamWHY2K/Rainmeter_Jellyfin_Status/releases")
    current_version = "1.0.4"
    try:
        latest_version = JF_Status_github.json()[0]["tag_name"][1:]
        changelog = JF_Status_github.json()[0]["body"]
        download_link = JF_Status_github.json()[0]["assets"][0]["browser_download_url"]
    except KeyError:
        latest_version = "0"
        changelog = "Unable to find changelog"
        download_link = "https://github.com/AdamWHY2K/Rainmeter_Jellyfin_Status"
    
    if current_version < latest_version:
            if confirm(
            f"\tCurrent version: {current_version}\n\t Latest version: {latest_version}\n\n{changelog}\n\nDownload now?",
            "Jellyfin Status - Update available",
            buttons=["OK", "Cancel"]) == "OK":
                webbrowser.open_new_tab(download_link) #Open download link in user's default browser
                logging.debug("Downloading update")
                raise SystemExit
            else:
                pass #Skip update this time, will ask again next time skin is refreshed or Rainmeter starts
    else:
        pass #User has latest version installed

def check_for_multiple_processes():
    count_processes = 0
    for i in WMI().Win32_Process(name="Jellyfin_Status.exe"):
        count_processes += 1
    if count_processes > 2:
        logging.debug("Exiting due to program already running.")
        raise SystemExit

if __name__ == "__main__":
    check_for_multiple_processes()
    check_for_updates()
    while WMI().Win32_Process(name="Rainmeter.exe"): #While the Rainmeter process exists
        try:
            myApp = App(sys.argv[1], sys.argv[2])
            myApp.get_sessions()
            myApp.create_users()
            myApp.write_users()
        except IndexError:
            pass
        except PermissionError: #Occasionally, seemingly arbitrarily, throws PermissionError.. I think maybe it can't write while Rainmeter is using the file
            pass #So just skip and hope that rainmeter is done reading the file by the next execution
        sleep(int(sys.argv[3]))
