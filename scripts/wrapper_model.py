from sktch import *

if __name__ == "__main__":

    #Parse and check the arguments
    parser = create_sketchfab_parser("Process a Sketchfab model to lowpoly")
    parser.add_argument("-o", "--output",     dest="output",     type=str, required=True,  help="Baking folder")
    parser.add_argument("-t", "--target",     dest="target",     type=int, default=1500,   help="Target number of faces")
    parser.add_argument("-r", "--resolution", dest="resolution", type=int, default=1024,   help="Baked textures resolution")
    args   = parse_sketchfab_args(parser, sys.argv[1:])
    args.output = os.path.abspath(args.output)

    with tempfile.TemporaryDirectory() as _tmpdir:

        #Download the model to tmpdir
        browser = webdriver.Firefox(firefox_profile=setup_Firefox_profile(_tmpdir))
        login_to_sketchfab(browser, args.sketchfab_user, args.sketchfab_pass)
        download_sketchfab_model(browser, args.url)
        browser.close()

        #Extract
        extract_all_archives(_tmpdir)

        #Bake all the files in the output directory
        os.system("python3.5 scripts/bakeAll.py -i " + _tmpdir + " -o " + args.output + " -p assets -t " + str(args.target) + " -r " + str(args.resolution))

    #Import everything to a new blender file
    os.system("blender --python scripts/importAll.py -- -i " + args.output + " -r 1")
