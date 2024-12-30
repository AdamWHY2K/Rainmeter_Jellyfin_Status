import logging
import requests
import re
import sys
from time import sleep
from wmi import WMI
from pymsgbox import confirm
import webbrowser
import updater


class User():
    def __init__(self, UserId, UserName, CurrentPlaying, Client, Transcoding, RuntimeTicks, PositionTicks, IsPaused, DeviceName):
        self.id = UserId
        self.name = "<name>" + UserName + "<name>"
        self.client = "<client>" + Client + "<client>"
        self.device_name = "<device_name>" + DeviceName + "<device_name>"
        self.total_time = RuntimeTicks
        self.current_time = PositionTicks

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

        self.output = self.name + self.playing + self.client + self.transcode + self.minutes_left + self.alt_minutes_left + self.percentage_done + self.play_status + self.device_name + "JFS_EOL_SIG"

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
        self.number_of_sessions = ""

    def connect(self):
        try:
            logging.info("Connecting to server")
            url = "http://" + self.ip + "/Sessions"
            params = {"api_key": self.api, "&activeWithinSeconds": "600"}
            server = requests.get(url, params).json()
            return server
        except requests.exceptions.ConnectionError:
            logging.error("\t\t\t Can't connect to server @ " + url)
            logging.info("Retrying in 5 minutes.")
            self.write_error()
            sleep(300)
            self.connect()
        except ValueError:
            logging.error("\t\t\t JSON recieved from the API is invalid.")
            logging.info("Retrying in 5 minutes.")
            self.write_error()
            sleep(300)
            self.connect()


    def write_error(self):
        with open("py_out.txt", "wb") as f:
            f.write("<number_of_sessions>1<number_of_sessions><name>ERROR<name><playing>SERVER OFFLINE<playing><client>NOTHING<client><play_status>[X]<play_status><device_name>NOTHING<device_name>JFS_EOL_SIG".encode("ascii", errors='replace'))

    def get_sessions(self):
        try:
            for i in self.connect():
                self.sessions.append(i)
        except TypeError:
            pass
            
    def create_users(self):
        logging.info("Creating users")
        for i in self.sessions:
            try:
                if i["UserId"] in self.users: #Check for duplicate
                    logging.warning("User: " + i["UserName"] + " has multiple sessions")
                    if self.users[i["UserId"]].play_status == "<play_status>[X]<play_status>": #If current entry is in an idle state, replace with new entry
                        self.users[i["UserId"]] = User(i["UserId"], i["UserName"], re.split("([^\/\\\]+)$", i["NowPlayingItem"]["Path"])[1], i["Client"], i["PlayState"]["PlayMethod"], i["NowPlayingItem"]["RunTimeTicks"], i["PlayState"]["PositionTicks"], i["PlayState"]["IsPaused"], i["DeviceName"])
                    else: #If current entry isn't in an idle state, don't overwrite it
                        pass
                else: #Still create an entry if there isn't a duplicate
                    self.users[i["UserId"]] = User(i["UserId"], i["UserName"], re.split("([^\/\\\]+)$", i["NowPlayingItem"]["Path"])[1], i["Client"], i["PlayState"]["PlayMethod"], i["NowPlayingItem"]["RunTimeTicks"], i["PlayState"]["PositionTicks"], i["PlayState"]["IsPaused"], i["DeviceName"])
            except KeyError:
                self.users[i["UserId"]] = User(i["UserId"], i["UserName"], None, i["Client"], None, None, None, None, i["DeviceName"])
            if i == self.sessions[-1]: #If last entry in sessions
                self.number_of_sessions = "<number_of_sessions>" + str(len(self.users)) + "<number_of_sessions>"


    def write_users(self):
        logging.info("Writing to py_out.txt")
        with open("py_out.txt", "wb") as f:
            f.write(self.number_of_sessions.encode("ascii", errors='replace'))
            for i in dict(sorted(self.users.items())): #Sorted so it prints in a consistent order
                f.write(self.users[i].output.encode("ascii", errors='replace')) #Rainmeter really doesn't like chars that aren't in the basic 128 ascii range, incompatible chars will be replaced with a ?

def check_for_multiple_processes():
    count_processes = 0
    for i in WMI().Win32_Process(name="Jellyfin_Status.exe"):
        count_processes += 1
    if count_processes > 2:
        logging.debug("Exiting due to program already running.")
        raise SystemExit

if __name__ == "__main__":
    check_for_multiple_processes()
    updater.check_for_updates("Jellyfin_Status", "https://api.github.com/repos/AdamWHY2K/Rainmeter_Jellyfin_Status/releases", "1.0.7")
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
