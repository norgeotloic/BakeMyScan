"""
Usage:
python downloadSkecthfabCollection.py -i 3b9b3fa1685c4cb5937cc0e9653bc0f1 -o /home/loic/tmp -u username@gmail.com -p password
"""

from sktch import *

if __name__ == "__main__":

    #Parse and check the arguments
    parser = create_sketchfab_parser("Download all models from a Sketchfab collection")
    parser.add_argument("-o", "--output", dest="output", type=str, required=True,  help="Download folder")
    parser.add_argument("-k", "--keep",   dest="keep",   action='store_true', default=False, help="Keep the .zip files")
    args        = parse_sketchfab_args(parser, sys.argv[1:])
    args.output = os.path.abspath(args.output)

    browser = webdriver.Firefox(firefox_profile=setup_Firefox_profile(args.output))
    uid = get_collection_uid(browser, args.url)

    #Get models and models infos from API call
    models = []
    data = make_API_request("https://api.sketchfab.com/v3/collections/" + uid + "/models")
    for r in data['results'][:2]:
        if r["isDownloadable"]:
            model = {
                "name": r["name"],
                "url": r["viewerUrl"],
                "user_name": r["user"]["displayName"],
                "user_url": r["user"]["profileUrl"],
                "license": make_API_request(r["uri"])["license"]["label"]
            }
            models.append(model)

    #Write the info to credits.md
    with open(os.path.join(args.output, "credits.md"), "w") as f:
        for m in models:
            f.write( "* [%s](%s) by [%s](%s), licensed under %s\n" % (m["name"], m["url"], m["user_name"], m["user_url"], m["license"]) )
        f.write("\n ")

    #Download the models to tmpdir
    login_to_sketchfab(browser, args.sketchfab_user, args.sketchfab_pass)
    for m in models:
        download_sketchfab_model(browser, m["url"])
    browser.close()

    #Extract the archives
    extract_all_archives(_tmpdir)
