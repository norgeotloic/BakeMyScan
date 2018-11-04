"""
Download all models from a Sketchfab collection

Usage:
python3.5 downloadSketchfab.py -u URL -o OUTDIR [-m MAIL -p PWD]

For instance:
    python3.5 downloadSketchfab.py -u https://skfb.ly/6yQSW -o /home/loic/tmp
    python3.5 downloadSketchfab.py -u https://skfb.ly/6yQSW -o /home/loic/tmp -m adress@mail.com -p mypassword
"""

import sys
import os
import argparse

#API request
import urllib.request
import json
def make_API_request(adress):
    url          = urllib.request.urlopen(adress)
    content      = url.read()
    encoding     = url.info().get_content_charset('utf-8')
    data         = json.loads(content.decode(encoding))
    return data

#selenium and firefox browsing
from selenium import webdriver
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support    import expected_conditions as EC
def setup_Firefox_profile(download_to):
    #Create a firefox profile to automatically download .zip on the Desktop
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.dir", download_to)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")
    profile.set_preference( "browser.download.manager.showWhenStarting", False )
    return profile
def login_to_sketchfab(browser, user=None, pwd=None):
    #Login to sketchfab
    browser.get("http://sketchfab.com/login")
    if user is not None and pwd is not None:
        browser.find_element_by_id("email").send_keys(user)
        browser.find_element_by_id("password").send_keys(pwd)
        browser.find_element_by_css_selector(".form-button").click()
    try:
        WebDriverWait(browser, 120).until(EC.title_contains("Profile"))
    finally:
        pass
def get_collection_uid(browser, url):
    browser.get(url)
    elt = browser.find_element_by_css_selector(".collection-header")
    uid = elt.get_attribute("data-collection-uid")
    return uid
def download_sketchfab_model(browser, url):
    oldFiles = os.listdir(args.output)
    browser.get(url)
    browser.find_element_by_css_selector('.c-model-actions__button.--download').click()
    try:
        WebDriverWait(browser, 120).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".button-source")))
    finally:
        pass
    browser.find_element_by_css_selector('.button-source').click()
    #Wait until no file is ending in ".part", which means download finished
    finished = False
    while not finished:
        time.sleep(1)
        newFiles = [f for f in os.listdir(args.output) if f.endswith("part")]
        if len(newFiles)==0:
            finished = True

if __name__ == "__main__":

    #Parse and check the arguments
    parser = argparse.ArgumentParser(description="Download a Sketchfab collection")
    parser.add_argument("-u", "--url",        dest="url",            type=str, required=True, help="Collection url")
    parser.add_argument("-o", "--output",     dest="output",         type=str, required=True, help="Output folder (must be empty)")
    parser.add_argument("-m", "--mail",       dest="sketchfab_user", type=str, help="Sketchfab e-mail adress")
    parser.add_argument("-p", "--pass",       dest="sketchfab_pass", type=str, help="Sketchfab password")
    args = parser.parse_args(sys.argv[1:])

    #Check if the output is empty or not
    args.output = os.path.abspath(args.output)
    if os.path.exists(args.output):
        if os.path.isdir(args.output):
            if len(os.listdir(args.output))>0:
                print("%s is not an empty directory, exiting" % args.output)
                sys.exit(1)
        else:
            print(args.output + " is not a directory, exiting")
            sys.exit(2)
    else:
        try:
            os.mkdir(args.output)
        except:
            print("Can't create " + args.output + ", exiting")
            sys.exit()

    #Prompt the user and password
    if args.sketchfab_user is None:
        args.sketchfab_user = input('Sketchfab e-mail: ')
    if "@" not in args.sketchfab_user:
        print("Expected an e-mail, not a username")
        sys.exit(0)
    if args.sketchfab_pass is None:
        args.sketchfab_pass = input('Sketchfab password: ')

    #Create a context for selenium browser
    profile = setup_Firefox_profile(args.output)
    browser = webdriver.Firefox(firefox_profile=profile)

    #Create the list of urls
    urls = []
    with open(os.path.join(args.output, "credits.md"), "w") as f:
        uid = get_collection_uid(browser, args.url)
        PAGES = []
        data = make_API_request("https://api.sketchfab.com/v3/collections/" + uid + "/models")
        PAGES.append(data)
        while data["next"] is not None:
            data = make_API_request(data["next"])
            PAGES.append(data)
        for PAGE in PAGES:
            for r in PAGE['results']:
                if r["isDownloadable"]:
                    urls.append(r["viewerUrl"])
                    f.write( "* [%s](%s) by [%s](%s), licensed under %s\n" % (
                        r["name"],
                        r["viewerUrl"],
                        r["user"]["displayName"],
                        r["user"]["profileUrl"],
                        r["license"]["label"]
                    ))

    #Download the models
    login_to_sketchfab(browser, args.sketchfab_user, args.sketchfab_pass)
    for url in urls:
        print("Downloading %s" % url)
        download_sketchfab_model(browser, url)
    browser.close()
