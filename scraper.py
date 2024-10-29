
import os
import re

from pydantic import BaseModel
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
import bs4


game_regex = re.compile("URL=steam://rungameid/[0-9]+")

class GameShortcut(BaseModel):
    name: str
    steam_id: str

def get_shortcut(filename: str, homedir: str) -> GameShortcut | None:
    if not filename.endswith('.url'):
        return None
    if not os.path.isfile(os.path.join(homedir, filename)):
        return None
    
    with open(os.path.join(homedir, filename)) as f:
        for line in f.readlines():
            if game_regex.match(line):
                steam_id =  line.strip().lstrip('URL=steam://rungameid/')
                name = filename.rstrip('.url')
                return GameShortcut(name=name, steam_id=steam_id)
    return None



def download_to_dir(url: str, dir: str):
    r = requests.get(url)
    fname = get_file_name(r, url)
    imagepath = os.path.join(dir, fname)
    with open(imagepath, "wb") as f:
        f.write(r.content)
    

def get_file_name(r: requests.Response, url: str) -> str:
    fname = ''
    if "Content-Disposition" in r.headers.keys():
        fname = re.findall("filename=(.+)", r.headers["Content-Disposition"])[0]
    else:
        fname = url.split("/")[-1]
    return fname

def get_steamdb_url(steam_id: str):
    return f"https://steamdb.info/app/{steam_id}/info/"


def get_image_link(webdriver: WebDriver, steam_id: str) -> str | None:
    webdriver.get(get_steamdb_url(steam_id))

    table = webdriver.find_element(by=By.ID, value="js-assets-table")
    inner = table.get_attribute("innerHTML")
    if not inner:
        return None
    soup = bs4.BeautifulSoup(inner, "html.parser")
    tbody: bs4.Tag = soup.find("tbody") # type: ignore
    row_list = tbody.findChildren("tr", recursive=False)

    for r in row_list:
        columns = r.findChildren("td", recursive=False)
        if columns[0].text == "clienticon":
            return columns[1].find("a")['href']
