"""
Script used manage over time, creates a database to save information to and read when needed.
Author: chomes@
Version: 1.3
built using pyinstaller
"""

from datetime import date, datetime
import shelve
import getpass
import csv
import calendar
from pathlib import Path
import shutil
import sys


# Overtime class for the entire DB
class OverTime:
    # Defining static variables
    def __init__(self):
        self.user = getpass.getuser()
        self.db = "otdb-{}.shelve".format(self.user)

    # Creating the DB or opening and starting welcome screen
    def startup(self):
        if Path(self.db).is_file():
            print("Loading DB")
            db = shelve.open(self.db)
            print("Welcome {} !".format(db["User"]["shortname"]))
            db.close()
        else:
            print("DB has not been created yet, lets get some info from you!")
            while True:
                usn = input("The system detects your Domain user is {} is this correct? y/n: "
                            "".format(self.user)).lower()
                if usn == "n":
                    new_user = input("Please type your correct username: ")
                    confirm = input("You have chosen {} is this correct? y/n: ".format(new_user)).lower()
                    if confirm == "y":
                        self.user = new_user
                        break
                    elif confirm == "n":
                        print("Lets try again then!")
                        continue
                elif usn == "y":
                    print("Great! Let's continue")
                    break

            while True:
                name = input("What would you like me to call you when using the db? ")
                confirm = input("You have chosen {} is this correct? y/n: ".format(name)).lower()
                if confirm == "y":
                    print("Great!  Lets continue")
                    break
                elif confirm == "n":
                    print("Ok lets try again!")
                    continue
            print("Almost there! We just need to ask a few more questions just to save this information for later!")
            while True:
                otn = float(input("Please tell me your OT rate when working out of your normal hours: "))
                otb = float(input("Please tell me your OT rate when working in your hours but on bank holidays: "))
                otnb = float(input("Now tell me your OT when covering on bank holidays out of hours: "))
                site = input("What is your primary site? For example when working on tickets your site is LHR54: "
                             "").upper()

                print("You have stated that your normal OT is {}, you're working bank holiday OT is {},".format(otn,
                                                                                                                otb))
                print("your OT when covering on bank holiday is {} and your site is {}.".format(otnb, site))
                confirm = input("Is this correct? y/n: ").lower()
                if confirm == "y":
                    print("Great! one last question and we're done!")
                    break
                elif confirm == "n":
                    print("Ok lets check those figures again")
                    continue
            while True:
                manager = input("Finally, tell me the username of your manager: ").lower()
                confirm = input("You've said that your manager is {} is this correct? y/n: ".format(manager))
                if confirm == "y":
                    print("OK! Let's make this database!")
                    break
                if confirm == "n":
                    print("Ok, lets try this again")
                    continue
            with shelve.open(self.db) as db:
                create_user = {"username": self.user, "shortname": name, "OT": {"normal": otn,
                                                                                "normal_bankhol": otb,
                                                                                "extra_bankhol": otnb},
                               "site": site,
                               "manager": manager}
                db["User"] = create_user
                db["OT"] = {}

            db.close()
            print("DB is created!")
            endscript = input("Do you want to exit now? y/n: ").lower()
            if endscript == "y":
                print("Good bye!")
                sys.exit()
            elif endscript == "n":
                print("Ok lets start doing some OT!")
                self.monthly_check()

    # Will check if you've gone past a month if it does, will compile a list of OT to send to a ticket
    # or send as a csv file to attach to a ticket,
    # will then delete older OT then last month and start counting again
    def checker(self):
        db = shelve.open(self.db)
        if date.today().isoformat() in db["OT"]:
            if db["OT"][date.today().isoformat()]["status"] == "complete":
                print("Looks like you have OT already for today!")
                db.close()
                self.hot_options()
            elif db["OT"][date.today().isoformat()]["status"] == "pending":
                print("You haven't finished your OT, lets go!")
                cot = "pending"
                cday = date.today().isoformat()
                db.close()
                self.not_options(cot, cday)
        else:
            print("You haven't started your OT yet, lets go!")
            cot = "none"
            cday = date.today().isoformat()
            db.close()
            self.not_options(cot, cday)

    # Method for exporting OT into a csv file and purging it.
    def export_tocsv(self):
        total_hours = self.calculate_hours()
        month = date.today().month - 1
        month = calendar.month_name[month]
        check_otrate = self.calculate_otrate()
        if isinstance(check_otrate, list):
            ratehour = self.cal_multi_ratehour(check_otrate)
            ottype = "Rates and hours \n"
            for key, value in ratehour["rates"].items():
                ottype += f"rate: {key} hours {value}"
        else:
            ottype = f"Total hours {total_hours} \n"
            ottype += f"Rate {check_otrate}"
        db = shelve.open(self.db)
        with open("last_month_OT.csv", "w") as csvfile:
            fieldnames = ["date", "hours", "reason", "ot type"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({"month": month, "overtime_type": ottype})
            writer.writeheader()
            for key, value in db["OT"].items():
                writer.writerow({"date": key, "hours": value["hours"],
                                 "reason": value["purpose"], "ot type": value["ot_type"]})
        csvfile.close()
        db.close()
        print("Purging DB of previous OT ")
        self.purge_db()
        sys.exit()

    # Method for saving the current OT to a csv file to view.
    def cot_tocsv(self):
        print("Creating CSV")
        total_hours = self.calculate_hours()
        month = date.today().month - 1
        month = calendar.month_name[month]
        check_otrate = self.calculate_otrate()
        if isinstance(check_otrate, list):
            ratehour = self.cal_multi_ratehour(check_otrate)
            ottype = "Rates and hours \n"
            for key, value in ratehour["rates"].items():
                ottype += f"rate: {key} hours {value}"
        else:
            ottype = f"Total hours {total_hours} \n"
            ottype += f"Rate {check_otrate}"
        db = shelve.open(self.db)
        with open("last_month_OT.csv", "w") as csvfile:
            fieldnames = ["date", "hours", "reason", "ot type"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({"month": month, "overtime_type": ottype})
            writer.writeheader()
            for key, value in db["OT"].items():
                writer.writerow({"date": key, "hours": value["hours"],
                                 "reason": value["purpose"], "ot type": value["ot_type"]})
        csvfile.close()
        db.close()
        print("Your OT will be in a file called current_OT.csv for you to view good bye!")
        sys.exit()

    # Temporary until fix bug to post on encrypted tickets
    def temp_csv(self):
        print("Creating csv")
        db = shelve.open(self.db)
        with open("current_OT.csv", "w") as csvfile:
            fieldnames = ["date", "hours", "reason", "ot type"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for key, value in db["OT"].items():
                writer.writerow({"date": key, "hours": value["hours"], "reason": value["purpose"],
                                 "ot type": value["ot_type"]})

        csvfile.close()
        db.close()

    # Method for calculating total hours.
    def calculate_hours(self):
        db = shelve.open(self.db)
        hour_counter = 0
        for day, info in db["OT"].items():
            hour_counter += info["hours"]
        db.close()
        return hour_counter

    # Method for calculating multiple rates
    def calculate_otrate(self):
        db = shelve.open(self.db)
        multi = []
        adding = []
        for key, value in db["OT"].items():
            if value["ot_type"] not in adding:
                adding.append(value["ot_type"])

        single = adding[0]
        poten = adding[0]
        for counter in adding:
            if counter != single:
                single = counter
                multi.append(counter)
            else:
                single = counter
        db.close()
        if not multi:
            return single
        else:
            if poten not in multi:
                multi.append(poten)
                return multi
            else:
                return multi

    # Method for calculating multi rates and hours
    def cal_multi_ratehour(self, otrates):
        db = shelve.open(self.db)
        rate_n_hours = {"rates": {}}
        for rates in otrates:
            rate_n_hours["rates"].update({rates: 0})

        for key, value in db["OT"].items():
            for rate, hours in rate_n_hours["rates"].items():
                if value["ot_type"] == rate:
                    rate_n_hours["rates"][rate] += value["hours"]

        return rate_n_hours

    # Method for purging dict of previous months OT
    def purge_db(self):
        print("Backing up database if something goes wrong please use that instead")
        shutil.copyfile(self.db, "{}.bk".format(self.db))
        print("Commencing the mighty purge!")
        db = shelve.open(self.db, writeback=True)
        remove = []
        for day in db["OT"].keys():
            temp = datetime.strptime(day, "%Y-%m-%d")
            if date.today().month > temp.month:
                remove.append(day)

        for key in remove:
            del db["OT"][key]

        db.close()
        print("DB has been purged of all previous months items.")

    # Method for checking if the OT has gone over the month, will be done every time the db is opened.
    def monthly_check(self):
        print("Checking DB for a previous months OT if you haven't gone over last month,"
              " we'll take you to the next menu")
        db = shelve.open(self.db)
        for day, hours in db["OT"].items():
            temp = datetime.strptime(day, "%Y-%m-%d")
            if date.today().month > temp.month:
                print("Looks like you're on a new month, we'll get your OT ready for you")
                print("Pulling all previous OT from the database")
                db.close()
                self.export_tocsv()
            else:
                db.close()
                return "Still on the current month, continuing programme"

    # Method for options for people who have OT already
    def hot_options(self):
        print("So you already have OT for the day so here's your list of available options: ")
        choose = input("""
        1) Print out your current OT to csv (THIS WILL NOT PURGE THE DB IT'S FOR VIEWING ONLY!)
        2) Change your user settings
        3) Quit        
        """)
        if choose == "1":
            self.cot_tocsv()
            sys.exit()
        elif choose == "2":
            self.settings()
        elif choose == "3":
            print("Take care!")
            sys.exit()

    # Method for pre-selecting hours for OT
    def preselect(self, time, current_day):
        ot_desc = input("Please give a brief reason for the OT, this can be a ticket or for example covering someone"
                        "this will go in the correspondence of the ticket when the month is over: ")
        ot_type = input("""
        Choose from the following:
        1) Normal OT
        2) Bank holiday OT while on shift
        3) Out of hours bank holiday OT (Working on bank holiday out of your shift pattern)
        """)
        print("Creating OT")
        db = shelve.open(self.db, writeback=True)
        if ot_type == "1":
            ot_type = db["User"]["OT"]["normal"]
        elif ot_type == "2":
            ot_type = db["User"]["OT"]["normal_bankhol"]
        elif ot_type == "3":
            ot_type = db["User"]["OT"]["extra_bankhol"]
        db["OT"].update({current_day: {"hours": time, "purpose": ot_desc, "status": "complete", "ot_type": ot_type}})
        print("Your OT for {} has been recorded in the db have a good day {}!".format(current_day,
                                                                                      db["User"]["shortname"]))
        db.close()
        sys.exit()

    # Method for creating calculator for manual OT
    def calculator(self, action, day):
        if action == "start":
            ot_desc = input(
                "Please give a brief reason for the OT, this can be a ticket or for example covering someone"
                "this will go in the correspondence of the ticket when the month is over: ")
            ot_type = input("""
            Choose from the following:
            1) Normal OT
            2) Bank holiday OT while on shift
            3) Out of hours bank holiday OT (Working on bank holiday out of your shift pattern)
            """)
            db = shelve.open(self.db, writeback=True)
            start_time = datetime.now()
            if ot_type == "1":
                ot_type = db["User"]["OT"]["normal"]
            elif ot_type == "2":
                ot_type = db["User"]["OT"]["normal_bankhol"]
            elif ot_type == "3":
                ot_type = db["User"]["OT"]["extra_bankhol"]
            db["OT"].update({day: {"hours": start_time, "purpose": ot_desc, "status": "pending", "ot_type": ot_type}})
            print("Ok your start time has been recorded {}, start the app again"
                  " when you're ready to stop".format(db["User"]["shortname"]))
            db.close()
            sys.exit()
        elif action == "stop":
            print("Calculating your time")
            end_time = datetime.now()
            db = shelve.open(self.db, writeback=True)
            start_time = db["OT"][day]["hours"]
            ttime = end_time - start_time
            ttime = ttime.seconds / 60
            print("Calculating time in hours and minutes")
            hours = 0
            while True:
                if ttime > 60:
                    hours += 1
                    ttime -= 60
                    continue
                else:
                    break
            ttime = round(ttime)
            final = f"{hours}.{ttime}"
            final = float(final)
            print("Updating database with todays time")
            db["OT"][day]["hours"] = final
            db["OT"][day]["status"] = "complete"
            print("Ok {} your OT has been recorded for the day, your total time is {} hours"
                  "closing the DB have a nice day!".format(db["User"]["shortname"], final))
            db.close()
            sys.exit()

    # Method for changing names
    def quick_sn(self, change_name):
        db = shelve.open(self.db, writeback=True)
        db["User"]["shortname"] = change_name
        print("By the power of Grayskull your new name is.. {} !".format(change_name))
        db.close()
        sys.exit()

    # Method for changing managers username
    def quick_manman(self, change_name):
        db = shelve.open(self.db, writeback=True)
        db["User"]["manager"] = change_name
        print("Your new managers username is {} !".format(change_name))
        db.close()
        sys.exit()

    # Method for changing your site location
    def quick_site(self, change_site):
        db = shelve.open(self.db, writeback=True)
        db["User"]["site"] = change_site
        print("You're now the fresh prince of a dc called {} !".format(change_site))
        db.close()
        sys.exit()

    # Method for settings menu
    def settings(self):
        print("Here's the settings menu")
        print("Please note most of these settings can be changed using arguments with the programme")
        print("After you've changed the settings we'll provide you the argument you need to run in the future"
              "just incase you want to do it the quick and lazy way cause who doesn't love being lazy :)")
        while True:
            picker = input("""Pick a setting to change:
            1) Change your shortname
            2) Change your managers username
            3) Change your site
            4) Export to CSV file
            5) Quit
            """)
            if picker == "1":
                db = shelve.open(self.db, writeback=True)
                change_name = input("Ok {} what do you want to change your name to? ".format(db["User"]["shortname"]))
                conf = input("You've chosen {} is this correct? y/n ".format(change_name)).lower()
                if conf == "y":
                    db["User"]["shortname"] = change_name
                    print("By the power of Grayskull your new name is.. {} !".format(change_name))
                    db.close()
                    print("If you want to change this automatically simply run the programme with the "
                          "following argument: ot --changename NEW_NAME please make sure they're no spaces!")
                    break
                elif conf == "n":
                    print("Ok lets try again")
                    continue
            elif picker == "2":
                db = shelve.open(self.db, writeback=True)
                change_name = input("Ok {} what do you want to "
                                    "change your managers username to to? ".format(db["User"]["shortname"])).lower()
                conf = input("You've chosen {} is this correct? y/n ".format(change_name)).lower()
                if conf == "y":
                    db["User"]["manager"] = change_name
                    print("Your new managers username is {} !".format(change_name))
                    db.close()
                    print("If you want to change this automatically simply run the programme with the "
                          "following argument: ot --changemanager USERNAME please make sure they're no spaces!")
                    break
                elif conf == "n":
                    print("Ok lets try again")
                    continue
            elif picker == "3":
                db = shelve.open(self.db, writeback=True)
                change_site = input("Ok {} what do you want to "
                                    "change your new site to? ".format(db["User"]["shortname"])).upper()
                conf = input("You've chosen {} is this correct? y/n ".format(change_site)).lower()
                if conf == "y":
                    db["User"]["site"] = change_site
                    print("You're now the fresh prince of a dc called {} !".format(change_site))
                    db.close()
                    print("If you want to change this automatically simply run the programme with the "
                          "following argument: ot --changesite SITE please make sure they're no spaces!")
                    break
                elif conf == "n":
                    print("Ok lets try again")
                    continue
            elif picker == "4":
                self.cot_tocsv()
            elif picker == "5":
                print("Take care!")
                sys.exit()

    # Method for no OT options
    def not_options(self, confirm, current_day):
        if confirm == "pending":
            print("So it seems like you already are calculating OT, so here's your current options: ")
            choose = input("""
            1) Finish calculating OT for the day.
            2) Change your user settings.
            3) Quit
            """)
            if choose == "1":
                self.calculator("stop", current_day)
            elif choose == "2":
                self.settings()
            elif choose == "3":
                print("Take care!")
                sys.exit()
        else:
            print("Right lets get your OT sorted out for you")
            print("Now you can either choose to calculate it via stop watch or choose from a pre-selected time")
            print("Just so you know the stop watch rounds up to the closest minute")
            print("So here are your options!")
            choose = input("""
            1) 12 hours OT
            2) 8 hours OT
            3) 4 hours OT
            4) Custom hours
            5) Calculate your OT by timer
            6) Change your user settings
            7) Quit
            """)
            if choose == "1":
                self.preselect(12, current_day)
            elif choose == "2":
                self.preselect(8, current_day)
            elif choose == "3":
                self.preselect(4, current_day)
            elif choose == "4":
                hours = float(input("How many hours do you want to OT? "))
                self.preselect(hours, current_day)
            elif choose == "5":
                self.calculator("start", current_day)
            elif choose == "6":
                self.settings()
            elif choose == "7":
                print("Take care!")
                sys.exit()
