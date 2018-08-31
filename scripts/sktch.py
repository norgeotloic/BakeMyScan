import sys
import os
import argparse
import imghdr
import argparse
import zipfile
import tempfile

#Arguments parsing
def create_sketchfab_parser(desc):
    #Create an arguments parser
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("-u", "--url",    dest="url",            type=str, required=True, help="Model or collection url")
    parser.add_argument("-m", "--mail",   dest="sketchfab_user", type=str, help="Sketchfab e-mail adress")
    parser.add_argument("-p", "--pass",   dest="sketchfab_pass", type=str, help="Sketchfab password")
    return parser
def parse_sketchfab_args(parser, argv):
    #Parse the arguments
    args = parser.parse_args(argv)
    if args.sketchfab_user is None:
        args.sketchfab_user = input('Sketchfab e-mail: ')
    if args.sketchfab_pass is None:
        args.sketchfab_pass = input('Sketchfab password: ')
    return args

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
def login_to_sketchfab(browser, user, pwd):
    #Login to sketchfab
    browser.get("http://sketchfab.com/login")
    browser.find_element_by_id("email").send_keys(user)
    browser.find_element_by_id("password").send_keys(pwd)
    browser.find_element_by_css_selector(".form-button").click()
    try:
        WebDriverWait(browser, 10).until(EC.title_contains("Profile"))
    finally:
        pass
def get_collection_uid(browser, url):
    browser.get(url)
    elt = browser.find_element_by_css_selector(".collection-header")
    uid = elt.get_attribute("data-collection-uid")
    return uid
def download_sketchfab_model(browser, url):
    browser.get(url)
    browser.find_element_by_css_selector('.c-model-actions__button.--download').click()
    try:
        WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".button-source")))
    finally:
        pass
    browser.find_element_by_css_selector('.button-source').click()

#Functions to recursively extract archives in a directory
def list_archives(_directory):
    files = []
    for root, directories, filenames in os.walk(_directory):
        for directory in directories:
            pass
        for filename in filenames:
            if filename[0]!=".":
                files.append(os.path.join(root, filename).strip())
    files = [ f for f in files if sum( [ x[0]=="." for x in f.split("/")[1:] ] ) == 0 ]
    archives = [ f for f in files if f.lower().endswith(".zip") or f.lower().endswith(".7z") or f.lower().endswith(".rar") ]
    return archives
def unzip_archive(_archive, keep=False):
    _unzip_to = os.path.abspath(_archive)[:-4]
    if _archive.endswith(".zip") or _archive.endswith(".ZIP"):
        zip_ref = zipfile.ZipFile(_archive, 'r')
        zip_ref.extractall(_unzip_to)
        zip_ref.close()
    elif _archive.endswith(".7z") or _archive.endswith(".7Z"):
        os.system("7zr x '" + _archive + "' -o" + os.path.dirname(_unzip_to) + " > /dev/null 2>&1")
    elif _archive.endswith(".rar") or _archive.endswith(".RAR"):
        os.system("unrar e '" + _archive + "' " + _unzip_to + "/ > /dev/null 2>&1" )
    else:
        print("The archive " + _archive + " is not in a known format!, aborting")
        sys.exit(1)
    if not keep:
        os.remove(_archive)
def extract_all_archives(_directory, keep=False):
    compteur = 0
    done = []
    while len([a for a in list_archives(_directory) if a not in done]) > 0:
        archives = [a for a in list_archives(_directory) if a not in done]
        for a in archives:
            if a not in done:
                print("Unzipping " + a)
                unzip_archive(a, keep)
                done.append(a)
        compteur+=1
        if compteur > 10:
            print("More than 10 recursions, exiting!")
            sys.exit()
