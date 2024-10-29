import os
import sys
import time
from selenium.webdriver import Firefox, Chrome, Edge
from selenium.webdriver.remote.webdriver import WebDriver

from functions import download_to_dir, get_shortcut, get_image_link

browsers: dict[str, type[WebDriver]] = {
    'firefox': Firefox,
    'chrome': Chrome,
    'edge': Edge
}
browser_options = list(browsers.keys())


def main(argv: list[str], argc: int):
    if argc != 3:
        print("invalid args")
        print("arg0: shortcuts directory")
        print("arg1: steam icons directory")
        print(f"arg2: browser type options={browser_options}")

        return
    homedir = argv[0]
    steam_icon_dir = argv[1]
    browser = argv[2].lower()
    assert os.path.isdir(homedir) and os.path.isdir(steam_icon_dir), "invalid paths"
    assert browser in browsers.keys(), f"invalid browser, options={browser_options}"


    print("Script Started")
    print(f"Opening {browser}")
    with browsers[browser]() as webdriver:
        print(f"Opened {browser}")
        for filename in os.listdir(homedir):
            g = get_shortcut(filename, homedir)
            if not g:
                continue
            print(f"Found Game({g}) in directory")
            link = get_image_link(webdriver, g.steam_id)
            if not link:
                print(f"Error {g} has no link")
                continue
            print(f"Got link={link}")
            download_to_dir(link, steam_icon_dir)
            print(f"Downloaded icon\n")
            time.sleep(2)
        print(f"Closing {browser}")
    print("Script Finished")



if __name__ == "__main__":
    args = sys.argv[1:]
    main(args, len(args))