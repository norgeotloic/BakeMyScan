from sktch import *

if __name__ == "__main__":

    #Parse and check the arguments
    parser = create_sketchfab_parser("Process all models from a Sketchfab collection to lowpoly")
    parser.add_argument("-o", "--output",     dest="output",     type=str, required=True,  help="Baking folder")
    parser.add_argument("-t", "--target",     dest="target",     type=int, default=1500,   help="Target number of faces")
    parser.add_argument("-r", "--resolution", dest="resolution", type=int, default=1024,   help="Baked textures resolution")
    args   = parse_sketchfab_args(parser, sys.argv[1:])
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

    with tempfile.TemporaryDirectory() as _tmpdir:

        #Download the models to tmpdir
        login_to_sketchfab(browser, args.sketchfab_user, args.sketchfab_pass)
        for m in models:
            download_sketchfab_model(browser, m["url"])
        browser.close()

        #Extract the archives
        extract_all_archives(_tmpdir)

        #Bake all the files in the output directory
        os.system("python3.5 scripts/bakeAll.py -i " + _tmpdir + " -o " + args.output + " -p assets -t " + str(args.target) + " -r " + str(args.resolution))

    #Import everything to a new blender file
    os.system("blender --python scripts/importAll.py -- -i " + args.output + " -r 5")
