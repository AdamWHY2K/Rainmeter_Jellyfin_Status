import requests
import webbrowser
from pymsgbox import confirm

def check_for_updates(name, api_releases, current_version):
    try:
        github = requests.get(api_releases)
        latest_version = github.json()[0]["tag_name"][1:]
        changelog = github.json()[0]["body"]
        download_link = github.json()[0]["assets"][0]["browser_download_url"]
    except (KeyError, requests.exceptions.ConnectionError):
        latest_version = "0"
        changelog = "Unable to find changelog"
        download_link = "https://github.com/AdamWHY2K?tab=repositories"
    
    if current_version < latest_version:
            if confirm(
            f"\tCurrent version: {current_version}\n\t Latest version: {latest_version}\n\n{changelog}\n\nDownload now?",
            f"{name} - Update available",
            buttons=["OK", "Cancel"]) == "OK":
                webbrowser.open_new_tab(download_link)
                raise SystemExit
            else:
                pass
    else:
        pass #User has latest version installed