import argparse
from translation.TranslationManager import run_translation

def main(version):
    print("Translate ARC " + version)
    run_translation(version)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--arc-version", required=True,
                         help="ARC Version, e.g. v1.4.1")
    args = parser.parse_args()
    main(args.arc_version)