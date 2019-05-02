# blame chomes@
import argparse
from otmods import ot

change_settings = ot.OverTime()
# Argparse functions
parser = argparse.ArgumentParser()
parser.add_argument("--changename", help="Use this to change your short name")
parser.add_argument("--changemanager", help="Use this to change your managers username")
parser.add_argument("--changesite", help="Use this to change your site location")
parser.add_argument("--exportcsv", action="store_true", help="Exports a csv file for you to view")
args = parser.parse_args()
if args.changename:
    change_settings.quick_sn(args.changename)
elif args.changemanager:
    change_settings.quick_manman(args.changemanager)
elif args.changesite:
    change_settings.quick_site(args.changesite)
elif args.exportcsv:
    change_settings.cot_tocsv()


# Function for starting programme
def main():
    overt = ot.OverTime()
    overt.startup()
    overt.monthly_check()
    overt.checker()


if __name__ == "__main__":
    main()
