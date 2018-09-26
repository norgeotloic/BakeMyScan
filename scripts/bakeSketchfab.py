import sys
import os
import argparse
import imghdr
import argparse
import zipfile
import tempfile

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

if __name__ == "__main__":

    #Parse and check the arguments
    parser = argparse.ArgumentParser(description="Process all models from a Sketchfab collection to lowpoly")
    parser.add_argument("-u", "--url",        dest="url",            type=str, required=True, help="Model or collection url")
    parser.add_argument("-o", "--output",     dest="output",         type=str, required=True, help="Output folder")
    parser.add_argument("-m", "--mail",       dest="sketchfab_user", type=str, help="Sketchfab e-mail adress")
    parser.add_argument("-p", "--pass",       dest="sketchfab_pass", type=str, help="Sketchfab password")
    parser.add_argument("-t", "--target",     dest="target",         type=int, default=1500,    help="Target number of faces")
    parser.add_argument("-r", "--resolution", dest="resolution",     type=int, default=1024,    help="Baked textures resolution")
    parser.add_argument("-s", "--suffix",     dest="suffix",         type=str, default="asset", help="Suffix name")
    parser.add_argument("-d", "--download",   dest="download",       action="store_true", help="Download only")
    args = parser.parse_args(sys.argv[1:])

    #Check if the output is empty or not
    args.output = os.path.abspath(args.output)
    if os.path.exists(args.output):
        if os.path.isdir(args.output):
            print("The directory exists")
            if len(os.listdir(args.output))>0:
                print("Not empty, I'm not going there")
                sys.exit(1)
            else:
                pass
        else:
            print(args.output + " is not a directory, exiting")
            sys.exit(1)
    else:
        try:
            os.mkdir(args.output)
        except:
            print("Can't create " + args.output + ", exiting")
            sys.exit(1)

    if args.sketchfab_user is None:
        args.sketchfab_user = input('Sketchfab e-mail: ')
    if args.sketchfab_pass is None:
        args.sketchfab_pass = input('Sketchfab password: ')

    #Create a context for selenium browser
    profile = setup_Firefox_profile(args.output)
    browser = webdriver.Firefox(firefox_profile=profile)

    isCollection = "collection" in args.url

    urls = []

    if isCollection:
        with open(os.path.join(args.output, "credits.md"), "w") as f:
            uid = get_collection_uid(browser, args.url)
            data = make_API_request("https://api.sketchfab.com/v3/collections/" + uid + "/models")
            for r in data['results'][:2]:
                if r["isDownloadable"]:
                    urls.append(r["viewerUrl"])
                    license = make_API_request(r["uri"])["license"]["label"]
                    f.write( "* [%s](%s) by [%s](%s), licensed under %s\n" % (r["name"], r["viewerUrl"], r["user"]["displayName"], r["user"]["profileUrl"], license) )
    else:
        urls.append(args.url)


    #Download the models
    login_to_sketchfab(browser, args.sketchfab_user, args.sketchfab_pass)
    for url in urls:
        download_sketchfab_model(browser, url)
    browser.close()

    #Extract the archives
    extract_all_archives(args.output)

    if not args.download:

        #Bake all the files in the output directory
        os.system("python3.5 scripts/bakeAll.py -i " + args.output + " -o " + args.output + " -p " + args.suffix + " -t " + str(args.target) + " -r " + str(args.resolution))

        #Import everything to a new blender file
        os.system("blender --python scripts/importAll.py -- -i " + args.output + " -r 5")
