# EXTERNAL LIBRARIES (pip installed):
import requests                 # HTTP requests library (better than default one).
from PIL import Image           # Image processing library.
from colorama import init       # ANSI color codes library for Windows Terminal.
init()                          # Initialization of the above.

# INTERNAL LIBRARIES:
import time                     # System time processing.
import os                       # System directory creation.
from pathlib import Path        # System directory/file path.
from sys import exit            # System exit application.
import re                       # Regular Expressions.
import json                     # JSON file processing.
import csv                      # CSV file processing.
import operator                 # List/Dictionary sorting.
import urllib                   # Parent library of...
import urllib.request           # ...default HTTP requests (outdated but works for downloading).
from datetime import datetime   # Datetime <-> Human readable date and time converter.

# GLOBAL VARIABLES - DATABASE STORING OBJECTS:
global scryfallDefaultCardsDB
scryfallDefaultCardsDB = None
global scryfallSetsDB
scryfallSetsDB = None
global scryfallMetaDB
scryfallMetaDB = None
global localDB
localDB = None
global localFiles
localFiles = None
global countsComparison
countsComparison = None

# GLOBAL VARIABLES - CONSTANTS:
global folderPaths
folderPaths = {'imagesScryfall': "MtG HD Cards PNG - Scryfall/",
                  'imagesForge': "MtG HD Cards JPG - Forge/",
             'imagesCockatrice': "MtG HD Cards JPG - Cockatrice/"}
global databasePaths
databasePaths = {'scryfallDefaultCardsDB': "scryfall-default-cards-new.json",
                         'scryfallSetsDB': "scryfall-sets.json",
                         'scryfallMetaDB': "scryfall-meta.json",
                                'localDB': "local-downloaded-cards.json"}
global databaseUris
databaseUris = {'scryfallDefaultCardsDB': "",
                        'scryfallSetsDB': "https://api.scryfall.com/sets",
                        'scryfallMetaDB': "https://api.scryfall.com/bulk-data"}

class Startup:
    def __init__(self):
        self.startupMemory()
        self.startupPrints()

    def startupMemory(self):
        self.readLocalFiles()
        self.loadDB()
        self.countCards()

    def startupPrints(self):
# Print Database versions (dates) and notify of missing files.
        print("DATABASE DATES:")
        for name, path in databasePaths.items():
            if path != "" and Path(path).is_file():
                fileDate, currentDate, daysPassed = self.compareFileDate(path)
                print("Your " + name + " is from \u001b[36m" + str(fileDate) + "\033[00m and today is \u001b[36m" + str(currentDate) + "\033[00m so Your DB file is \u001b[36m" + str(daysPassed) + "\033[00m days old.")
            elif path != "" and not Path(path).is_file():
                print("Your \u001b[31;1m" + path + "\033[00m file is missing!")
            elif path == "":
                print("Your " + name + " file isn't specified in Python code yet!")
        print()
# Print database items count.
        print("DATABASE ITEMS COUNT:")
        if scryfallDefaultCardsDB != None:
            print("Your \u001b[36mscryfallDefaultCardsDB\033[00m object has \u001b[36m" + str(len(scryfallDefaultCardsDB)) + "\033[00m items in it.")
        else:
            print("Missing \u001b[31;1mscryfallDefaultCardsDB\033[00m object!")
        if scryfallSetsDB != None:
            print("Your \u001b[36mscryfallSetsDB\033[00m object has \u001b[36m" + str(len(scryfallSetsDB)) + "\033[00m items in it.")
        else:
            print("Missing \u001b[31;1mscryfallSetsDB\033[00m object!")
        if scryfallMetaDB != None:
            print("Your \u001b[36mscryfallMetaDB\033[00m object has \u001b[36m" + str(len(scryfallMetaDB)) + "\033[00m items in it.")
        else:
            print("Missing \u001b[31;1mscryfallMetaDB\033[00m object!")
        if localDB != None:
            print("Your \u001b[36mlocalDB\033[00m object has \u001b[36m" + str(len(localDB)) + "\033[00m items in it.")
        else:
            print("Missing \u001b[31;1mlocalDB\033[00m object!")
        print()
# Print local files count.
        print("LOCAL FILES COUNT:")
        if countsComparison != None:
            for set in countsComparison:
                if set[1] == set[2]:
                    print(str(set[0]) + " has \u001b[36m" + str(set[1]) + "\033[00m cards indexed in folder from a total of \u001b[36m" + str(set[2]) + "\033[00m cards in scryfallDefaultCardsDB: \u001b[32;1mAll correct!\033[00m")
                elif set[1] < set[2]:
                    print(str(set[0]) + " has \u001b[36m" + str(set[1]) + "\033[00m cards indexed in folder from a total of \u001b[36m" + str(set[2]) + "\033[00m cards in scryfallDefaultCardsDB: \u001b[31;1mSome cards are missing!\033[00m")
        print("...for a total of: \u001b[36m" + str(sum(set[1] for set in countsComparison)) + "\033[00m image files in \u001b[36m" + str(len(countsComparison)) + "\033[00m set folders from a total of \u001b[36m" + str(len(scryfallDefaultCardsDB)) + "\033[00m cards in entire scryfallDefaultCardsDB (including sets not downloaded yet).")
        print()

    def compareFileDate(self, filePath):
# Compare file "last modified" date to current date for any given file.
        fileDate = datetime.strptime(str(datetime.fromtimestamp(os.path.getmtime(filePath)))[0:10], '%Y-%m-%d').date()
        currentDate = datetime.strptime(str(datetime.now())[0:10], '%Y-%m-%d').date()
        daysPassed = (currentDate - fileDate).days
        return fileDate, currentDate, daysPassed

    def loadDB(self):
# Load Databases from files to objects, in case of Local Database, run a function to create it if necessary.
        global scryfallDefaultCardsDB
        if scryfallDefaultCardsDB == None and Path(databasePaths['scryfallDefaultCardsDB']).is_file():
            with open (databasePaths['scryfallDefaultCardsDB'], 'r', encoding="utf-8") as file:
                scryfallDefaultCardsDB = json.load(file)
        elif scryfallDefaultCardsDB == None and not Path(databasePaths['scryfallDefaultCardsDB']).is_file():
            print("Please, download newest version of Scryfall Bulk Data - Default DB, manually.")

        global scryfallSetsDB
        if scryfallSetsDB == None and Path(databasePaths['scryfallSetsDB']).is_file():
            with open (databasePaths['scryfallSetsDB'], 'r', encoding="utf-8") as file:
                scryfallSetsDB = json.load(file)
        elif scryfallSetsDB == None and not Path(databasePaths['scryfallSetsDB']).is_file():
            DataWriter.downloadToJSON(databaseUris['scryfallSetsDB'], databasePaths['scryfallSetsDB'])

        global scryfallMetaDB
        if scryfallMetaDB == None and Path(databasePaths['scryfallMetaDB']).is_file():
            with open (databasePaths['scryfallMetaDB'], 'r', encoding="utf-8") as file:
                scryfallMetaDB = json.load(file)
        elif scryfallMetaDB == None and not Path(databasePaths['scryfallMetaDB']).is_file():
            DataWriter.downloadToJSON(databaseUris['scryfallMetaDB'], databasePaths['scryfallMetaDB'])

        global localDB
        if localDB == None and Path(databasePaths['localDB']).is_file():
            with open (databasePaths['localDB'], 'r', encoding="utf-8") as file:
                localDB = json.load(file)
        elif localDB == None and not Path(databasePaths['localDB']).is_file():
            self.createLocalDB()

    def readLocalFiles(self):
# Reads all local image files in set folders.
        csvContents = []
        folderContents = []
        mainFolder = folderPaths['imagesScryfall']
        for folder in os.listdir(mainFolder):
            if os.path.isdir(Path(mainFolder + folder)):
                csvFile = mainFolder + folder + "/" + folder + ".txt"
                if Path(csvFile).is_file():
                    csvContents.append([folder, csvFile, []])
                    with open(csvFile, "r", encoding='utf-8') as file:
                        csvReader = csv.reader(file, delimiter=";")
                        for row in csvReader:
                            rowContent = []
                            for item in row:
                                rowContent.append(item)
                            csvContents[-1][2].append(rowContent)
        for folder in os.listdir(mainFolder):
            if os.path.isdir(os.path.join(mainFolder, folder)):
                subFolder = mainFolder + folder
                folderContents.append([folder, subFolder, []])
                for file in os.listdir(subFolder):
                    if file.endswith(".png"):
                        imageFile = subFolder + "/" + file + ".png"
                        folderContents[-1][2].append([file, imageFile])
        global localFiles
        localFiles = []
        for set in csvContents:
            localFiles.append([set[0], folderContents[csvContents.index(set)][1], []])
            for card in set[2]:
                imageFile = mainFolder + set[0] + "/" + card[4]
                if Path(imageFile).is_file():
                    localFiles[-1][2].append([card[1], card[2], card[4], imageFile])

    def countCards(self):
# Count cards by set in local image files (based in index and actual files) and in original scryfallDefaultCardsDB.
        global countsComparison
        countsComparison = []
        for set in localFiles:
# ------ Problem Solver for Windows forbidden folder names.
            if set[0].lower() in ["con_"]:
                setName = "CON"
            else:
                setName = set[0]
            countsComparison.append([set[0], len(set[2]), sum(card['set'].lower() == setName.lower() for card in scryfallDefaultCardsDB)])

    def createLocalDB(self):
# Create Local Database object to store data extracted from Scryfall Default DB, updated by local image paths, only for cards that have their images downloaded.
        global localDB
        localDB = []
        for folder in localFiles:
            for file in folder[2]:
                match = next(card for card in scryfallDefaultCardsDB if card['id'] == file[0])
                match.update({'image_paths':{'png':file[3]}})
                localDB.append(match)
        DataWriter.objectToJSON(localDB, databasePaths['localDB'])

class Menus:
    def __init__(self):
        print()
        print("###################################################")
        print("### Scryfall MtG Project version 3 by NecXelos. ###")
        print("###################################################")
        print()
        self.menuMainS = ("[ \033[36;1m(S)\033[00mearch for a card by name ]\n" +
                          "[ \033[36;1m(L)\033[00mist all cards in a set ]\n" +
                          "[ \033[36;1m(F)\033[00mind all tokens used in downloaded sets ]\n" +
                          "[ \033[36;1m(D)\033[00mownload all cards from a set ]\n" +
                          "[ \033[36;1m(R)\033[00mewrite local cards database file ]\n" +
                          "[ \033[36;1m(C)\033[00monvert image files ]\n" +
                          "[ \033[36;1m(Q)\033[00muit application ]")
        self.menuYesNoS = ("[ \033[36;1m(Y)\033[00mes ]\n" +
                           "[ \033[36;1m(N)\033[00mo ]")
        self.menuWhichDBS = ("[ \033[36;1m(L)\033[00mocal Database ]\n" +
                             "[ \033[36;1m(S)\033[00mcryfall Database ]")
        self.incorrectInputS = "Incorrect input. Please choose correct command from the list below:"
        self.menuImageFilesS = ("[ \033[36;1m(1)\033[00m Recreate all image files in MtG Forge - friendly format (.full.jpg files with lands numbered from 1 to X). ]\n" +
                                "[ \033[36;1m(2)\033[00m Recreate all image files in MtG Cockatrice - friendly format (.jpg files, no alternative images). ]\n" +
                                "[ \033[36;1m(3)\033[00m Do a test run with current image convertion settings. ]")

    def menuYesNo(self, description):
# Ask Yes or No question.
        print(description)
        print(self.menuYesNoS)
        print()
        self.userInput = input()
        print()
        while self.userInput.upper() not in ["Y", "N"]:
            print(self.incorrectInputS)
            print(self.menuYesNoS)
            print()
            self.userInput = input()
            print()
        else:
            if self.userInput in ["Y", "y"]:
                return True
            elif self.userInput in ["N", "n"]:
                return False

    def menuWhichDB(self):
# Ask which database user wants to use for his queries.
        print("Which database do You want to use for Your query?")
        print(self.menuWhichDBS)
        print()
        self.userInput = input()
        print()
        while self.userInput.upper() not in ["L", "S"]:
            print("Incorrect input. Please choose from the list below:")
            print(self.menuWhichDBS)
            print()
            self.userInput = input()
            print()
        else:
            if self.userInput in ["L", "l"]:
                return ["localDB", localDB, "localDB"]
            else:
                return ["scryfallDefaultCardsDB", scryfallDefaultCardsDB, "scryfallDefaultCardsDB"]

    def menuMain(self):
# Ask which app functionality user wants to use.
        print("MAIN MENU:")
        print("Choose app functionality You wish to use:")
        print(self.menuMainS)
        print()
        self.userInput = input()
        print()
        while self.userInput.upper() not in ["S", "L", "F", "D", "R", "C", "Q"]:
            print("Incorrect input. Please choose from the list below:")
            print(self.menuMainS)
            print()
            self.userInput = input()
            print()
        else:
            global currentChoice
            if self.userInput in ["S", "s"]:
                currentChoice = CardSearch()
            if self.userInput in ["L", "l"]:
                currentChoice = CardsLister()
            if self.userInput in ["F", "f"]:
                currentChoice = TokenFinder()
            if self.userInput in ["D", "d"]:
                currentChoice = CardsDownloader()
            if self.userInput in ["R", "r"]:
                currentChoice = DataWriter()
            if self.userInput in ["C", "c"]:
                currentChoice = ImageConverter()
            if self.userInput in ["Q", "q"]:
                print("Quiting application...")
                exit(0)

    def menuContinue(self):
# Ask if user wants to continue using app.
        if menus.menuYesNo("Do You want anything else?"):
            self.menuMain()
        else:
            print("Quiting application...")
            exit(0)

    def menuImageFiles(self):
# Menu specific to Image Convertion class, due to lots of options planned there.
        print("What do You want to do?")
        print(self.menuImageFilesS)
        print()
        self.userInput = input()
        print()
        while self.userInput not in ["1", "2", "3"]:
            print("Incorrect input. Please choose from the list below:")
            print(self.menuImageFilesS)
            print()
            self.userInput = input()
            print()
        else:
            return self.userInput

class CardSearch:
    def __init__(self):
        print("Card search engine is on!")
        print()
        self.wantedKeys = ['name', 'released_at', 'mana_cost', 'type_line', 'oracle_text', 'power', 'toughness', 'colors', 'color_identity',
                           'set', 'set_name', 'set_type', 'collector_number', 'rarity', 'border_color', 'frame']
        self.nameSearch(menus.menuWhichDB())
        menus.menuContinue()

    def nameSearch(self, whichDB):
        print("Write card name or it's fragment You want to search for:")
        print()
        self.userInput = input()
        self.results = []
        print()
# Searches chosen database for desired card name (or fragment of it).
        while not any(self.userInput.lower() in card['name'].lower() for card in whichDB[1]):
            print("Name or fragment You provided doesn't exist in " + whichDB[2] + " Database. Try another one:")
            print()
            self.userInput = input()
            print()
        else:
            for card in whichDB[1]:
                if self.userInput.lower() in card['name'].lower():
                    self.results.append(card)
# Filters dictionary to show only important key:value pairs.
        # filteredResults = self.results
        filteredResults = [{key:value for key, value in result.items() if key in self.wantedKeys} for result in self.results]
        print("Search results in " + whichDB[2] + " Database:")
        for i in filteredResults:
            print("\u001b[36mItem: " + str(filteredResults.index(i) + 1) + "\033[00m")
            print(json.dumps(i, indent = 3))
            print()

class CardsLister:
    def __init__(self):
        print("Set search engine is on!")
        print()
        self.setSearch(menus.menuWhichDB())
        menus.menuContinue()

    def setSearch(self, whichDB):
        print("Write abbreviation of the set You want to list:")
        print()
        self.userInput = input()
        self.results = []
        self.set = []
        print()

        while not any(self.userInput.lower() == card['set'].lower() for card in whichDB[1]):
            print("Set with chosen abbreviation doesn't exist in " + whichDB[2] + " Database. Try another one:")
            print()
            self.userInput = input()
            print()
        else:
            for card in whichDB[1]:
                if card['set'].lower() == self.userInput.lower():
                    self.results.append([card['name'], card['type_line'], card['mana_cost'], card['oracle_text']])
                    if len(self.set) != 2:
                        self.set.append(card['set'])
                        self.set.append(card['set_name'])

        print("Search results in " + whichDB[2] + " Database:")
        print(self.set[0].upper() + " : " + self.set[1])
        for i in self.results:
            print("\u001b[36m" + str(self.results.index(i) + 1) + "\033[00m:\u001b[36m" + i[0] + "\033[00m")
            print("    " + i[1] + " - " + i[2])
            print("    " + i[3])
        print()

class TokenFinder:
    def __init__(self):
        print("Token finding engine is on!")
        print()
        self.listTokens()
        menus.menuContinue()

    def listTokens(self):
        tokensCount = 0
        for card in scryfallDefaultCardsDB:
            if "token" in card['type_line'].lower() and card['frame'] == "1997":
                tokensCount += 1
                print(card['type_line'])
        print(tokensCount)
        print()

class CardsDownloader:
    def __init__(self):
        print("Cards downloadeing engine is on!")
        print()
        self.set = []
        self.cardsList = []
        self.cardsDownload()
        menus.menuContinue()

    def cardsDownload(self):
        print("Write abbreviation of the set You want to download:")
        print()
        self.userInput = input()
        print()
# ------ Problem Solver for Windows forbidden folder names.
        if self.userInput.upper() in ["CON"]:
            self.folderName = "con_"
        else:
            self.folderName = self.userInput

# Start the download pipeline if files aren't downloaded yet (and if demanded set exists in the first place).
        while not (any(self.userInput.lower() == card['set'] for card in scryfallDefaultCardsDB)) or ( (any(self.folderName.upper() == folder[0] for folder in localFiles)) and (len(localFiles[next((idx for idx, sublist in enumerate(localFiles) if self.folderName.upper() == sublist[0]), None)][2]) == countsComparison[next((idx for idx, sublist in enumerate(countsComparison) if self.userInput.upper() == sublist[0]), None)][2]) ):
            if not any(self.userInput.lower() == card['set'] for card in scryfallDefaultCardsDB):
                print("Set with chosen abbreviation doesn't exist in Scryfall Database. Try another one:")
            else:
                print("Set with chosen abbreviation already has all the image files (\u001b[36m" + str(len(localFiles[next((idx for idx, sublist in enumerate(localFiles) if self.userInput.upper() == sublist[0]), None)][2])) + "\033[00m/\u001b[36m" + str(countsComparison[next((idx for idx, sublist in enumerate(countsComparison) if self.userInput.upper() == sublist[0]), None)][2]) + "\033[00m) downloaded. Try another one:")
            print()
            self.userInput = input()
            print()
# ------ Problem Solver for Windows forbidden folder names.
            if self.userInput.upper() in ["CON"]:
                self.folderName = "con_"
            else:
                self.folderName = self.userInput
        else:
            self.downloadsList(self.userInput.lower())
            print("Downloading the " + self.userInput.upper() + " set!")
# Check if set directory exists and create one if not.
            dir_path = folderPaths['imagesScryfall'] + self.folderName.upper()
            dir_check = Path(dir_path)
            if not dir_check.exists():
                try:
                    os.mkdir(dir_path)
                except OSError:
                    print("Directory creation failed (due to system error).")
                    print()
                else:
                    print("Directory successfully created.")
                    print()
            else:
                print("Directory already exist in specified location.")
                print()
# Check if image file exist and download one if not.
            for card in self.cardsList:
                image_uri = card[3]
                image_file_path = folderPaths['imagesScryfall'] + self.folderName.upper() + "/" + card[4]
                file_check = Path(image_file_path)
                if not file_check.is_file():
                    urllib.request.urlretrieve(image_uri, image_file_path)
                    print("File " + str(card[0]) + ": \u001b[32;1m" + image_file_path + "\033[00m successfully downloaded.")
                    time.sleep(1)
                else:
                    print("File " + str(card[0]) + ": \u001b[36m" + image_file_path + "\033[00m already exist, skipping to next file.")
            print()
            print("All downloads finished.")
            print()
            self.makeDataFile(self.folderName.upper())

    def downloadsList(self, set):
        if any(set == card['set'] for card in scryfallDefaultCardsDB):
# Create list object containing all the data required to download, name and categorize image files.
            item = 1
            for card in scryfallDefaultCardsDB:
                if card['set'] == set:
                    self.cardsList.append([item, card['id'], card['name'], card['image_uris']['png']])
                    item += 1
# Create future file names of images to be downloaded and correct duplicate names, illegal characters, etc.
            previous = ""
            duplicates = [[], []]
            for card in self.cardsList:
                card.append(card[2])
            for card in self.cardsList:
                if any(illegalSign in card[4] for illegalSign in [" // ", ":", '"']):
                    card[4] = re.sub(" // ", "", card[4])
                    card[4] = re.sub(":", "", card[4])
                    card[4] = re.sub('"', "", card[4])
                if card[4] == previous:
                    duplicates[0].append(card[4])
                    duplicates[1].append(2)
                    card[4] = duplicates[0][duplicates[0].index(card[4])] + str(duplicates[1][duplicates[0].index(card[4])])
                elif card[4] in duplicates[0]:
                    duplicates[1][duplicates[0].index(card[4])] += 1
                    card[4] = duplicates[0][duplicates[0].index(card[4])] + str(duplicates[1][duplicates[0].index(card[4])])
                previous = card[4]
            for card in self.cardsList:
                if card[4] in duplicates[0]:
                    card[4] = card[4] + "1"
            for card in self.cardsList:
                card[4] = card[4] + ".png"

    def makeDataFile(self, set):
# Check if set data file exists and create one if not.
        data_file_path = folderPaths['imagesScryfall'] + set + "/" + set + ".txt"
        file_check = Path(data_file_path)
        if not file_check.is_file():
            with open (data_file_path, "w+", encoding='utf-8') as file:
                for card in self.cardsList:
                    for value in card:
                        file.write(str(value) + ";")
                    file.write("\n")
            print("Data file successfully created.")
            print()
        else:
            print("Data file already exist in specified location.")
            print()

class DataWriter:
    def __init__(self):
        print("Data writing engine is on!")
        print()
        menus.menuContinue()

    @staticmethod
    def downloadToJSON(databaseURL, databasePath):
        database = requests.get(url=databaseURL).json()
        file_check = Path(databasePath)
        if not file_check.is_file():
            data = database['data']
            with open(databasePath, 'w') as file:
                file.write('[\n')
                for item in data:
                    file.write('  ')
                    json.dump(item, file)
                    if data.index(item) != (len(data) - 1):
                        file.write(',\n')
                    else:
                        file.write('\n')
                file.write(']')

    @staticmethod
    def objectToJSON(databaseObject, databasePath):
        file_check = Path(databasePath)
        if not file_check.is_file():
            data = databaseObject
            with open(databasePath, 'w') as file:
                file.write('[\n')
                for item in data:
                    file.write('  ')
                    json.dump(item, file)
                    if data.index(item) != (len(data) - 1):
                        file.write(',\n')
                    else:
                        file.write('\n')
                file.write(']')

class ImageConverter:
    def __init__(self):
        print("Image converting engine is on!")
        print()
        self.setCodePairs = [
                           # Starter Sets:
                             ["POR", "PT"], ["P02", "P2"], ["PTK", "P3"],
                           # Core Sets:
                             ["LEA", "A"], ["LEB", "B"], ["2ED", "U"], ["3ED", "R"], ["4ED", "4E"], ["5ED", "5E"], ["6ED", "6E"], ["7ED", "7E"],
                             ["8ED", "8E"], ["9ED", "9E"], ["10E", "10E"],
                             ["M10", "M10"], ["M11", "M11"], ["M12", "M12"],
                           # Non-Block Expansions:
                             ["ARN", "AN"], ["ATQ", "AQ"], ["LEG", "LG"], ["DRK", "DK"], ["FEM", "FE"], ["HML", "HL"],
                           # Block Expansions:
                             ["ICE", "IA"], ["ALL", "AL"], ["CSP", "CS"],
                             ["MIR", "MI"], ["VIS", "VI"], ["WTH", "WL"],
                             ["TMP", "TE"], ["STH", "SH"], ["EXO", "EX"],
                             ["USG", "US"], ["ULG", "UL"], ["UDS", "UD"],
                             ["MMQ", "MM"], ["NEM", "NE"], ["PCY", "PY"],
                             ["INV", "IN"], ["PLS", "PS"], ["APC", "AP"],
                             ["ODY", "OD"], ["TOR", "TO"], ["JUD", "JU"],
                             ["ONS", "ON"], ["LGN", "LE"], ["SCG", "SC"],
                             ["MRD", "MR"], ["DST", "DS"], ["5DN", "FD"],
                             ["CHK", "CHK"], ["BOK", "BOK"], ["SOK", "SOK"],
                             ["RAV", "RAV"], ["GPT", "GP"], ["DIS", "DIS"],
                             ["TSP", "TSP"], ["PLC", "PLC"], ["FUT", "FUT"],
                             ["LRW", "LRW"], ["MOR", "MOR"],
                             ["SHM", "SHM"], ["EVE", "EVE"],
                             ["ALA", "ALA"], ["CON_", "CFX"], ["ARB", "ARB"],
                             ["ZEN", "ZEN"], ["WWK", "WWK"], ["ROE", "ROE"],
                             ["SOM", "SOM"], ["MBS", "MBS"], ["NPH", "NPH"],
                           # Reprint Expansions:
                             ["CHR", "CH"], ["TSB", "TSB"],
                           # Reprint Box/Deck Sets:
                             ["ATH", "ATH"], ["BRB", "BRB"], ["BTD", "BTD"], ["DKM", "DKM"],
                           # Commander-specific Box/Deck Sets:
                             ["CMD", "COM"],
                           # Game Variants:
                             ["PVAN", "VAN"]
                            ]
        self.setsCropParams = {
                               'POR':(35, 40, 709, 1001), 'P02':(35, 40, 709, 1001), 'PTK':(36, 40, 709, 1001),
                               'LEA':(35, 42, 710, 998), 'LEB':(35, 42, 710, 998), '2ED':(35, 42, 710, 998), '3ED':(35, 42, 710, 998), '4ED':(28, 31, 717, 1009), '5ED':(35, 38, 710, 1001), '6ED':(35, 38, 710, 1001), '7ED':(35, 38, 710, 1001),
                               '8ED':(34, 34, 711, 1004), '9ED':(34, 34, 711, 1007), '10E':(34, 34, 711, 1007),
                               'M10':(34, 34, 711, 1007), 'M11':(34, 34, 711, 1007), 'M12':(34, 34, 711, 1007),
                               'ARN':(27, 31, 718, 1009), 'ATQ':(27, 31, 718, 1009), 'LEG':(27, 30, 718, 1011), 'DRK':(27, 31, 718, 1009), 'FEM':(27, 31, 718, 1009), 'HML':(27, 31, 718, 1009), # LEG slightly different than the rest.
                               'ICE':(27, 31, 718, 1009), 'ALL':(27, 31, 718, 1009), 'CSP':(33, 33, 712, 1008), # CSP varies from other 2 sets in the block, because it is a later addition.
                               'MIR':(35, 39, 710, 1002), 'VIS':(35, 39, 710, 1002), 'WTH':(35, 39, 710, 1002),
                               'TMP':(35, 39, 710, 1002), 'STH':(35, 39, 710, 1002), 'EXO':(35, 39, 710, 1002),
                               'USG':(35, 39, 710, 1002), 'ULG':(35, 39, 710, 1002), 'UDS':(35, 39, 710, 1002),
                               'MMQ':(35, 39, 710, 1002), 'NEM':(35, 39, 710, 1002), 'PCY':(35, 39, 710, 1002),
                               'INV':(35, 39, 710, 1002), 'PLS':(35, 39, 710, 1002), 'APC':(35, 39, 710, 1002),
                               'ODY':(35, 39, 710, 1002), 'TOR':(35, 39, 710, 1002), 'JUD':(35, 39, 710, 1002),
                               'ONS':(35, 39, 709, 1001), 'LGN':(35, 39, 710, 1002), 'SCG':(35, 39, 710, 1002), # Very uneven borders in this block! ONS is the worst!
                               'MRD':(33, 33, 712, 1008), 'DST':(33, 33, 712, 1008), '5DN':(33, 33, 712, 1008), # Somewhat uneven borders in this block - not as bad as in ONS block!
                               'CHK':(33, 33, 712, 1008), 'BOK':(33, 33, 712, 1008), 'SOK':(33, 33, 712, 1008),
                               'RAV':(33, 33, 712, 1008), 'GPT':(33, 33, 712, 1008), 'DIS':(33, 33, 712, 1008),
                               'TSP':(33, 33, 712, 1008), 'PLC':(33, 33, 712, 1008), 'FUT':(33, 33, 712, 1008),
                               'LRW':(33, 33, 712, 1008), 'MOR':(33, 33, 712, 1008),
                               'SHM':(33, 33, 712, 1008), 'EVE':(33, 33, 712, 1008),
                               'ALA':(33, 33, 712, 1008), 'CON_':(33, 33, 712, 1008), 'ARB':(33, 33, 712, 1008),
                               'ZEN':(33, 33, 712, 1008), 'WWK':(33, 33, 712, 1008), 'ROE':(33, 33, 712, 1008),
                               'SOM':(33, 33, 712, 1008), 'MBS':(33, 33, 712, 1008), 'NPH':(33, 33, 712, 1008),
                               'CHR':(29, 30, 716, 1009), 'TSB':(35, 39, 710, 1001),
                               'ATH':(35, 39, 709, 1001), 'BRB':(36, 39, 710, 1001), 'BTD':(36, 39, 710, 1001), 'DKM':(36, 39, 710, 1001),
                               'CMD':(34, 34, 711, 1007),
                               'PVAN':(46, 57, 1014, 1446)
                              }
        self.choice = menus.menuImageFiles()
        if self.choice == "1":
            self.imageConvertForge()
        elif self.choice == "2":
            self.imageConvertCockatrice()
        else:
            self.imageConvertTest()
        menus.menuContinue()

    def imageConvertForge(self):
        print("Converting HQ .png files to HQ .jpg files compatible with Forge App:")
        for folder in localFiles:
            newFolder = self.setCodePairs[next((idx for idx, sublist in enumerate(self.setCodePairs) if folder[0] == sublist[0]), None)][1]
            dir_path = folderPaths['imagesForge'] + newFolder
            dir_check = Path(dir_path)
            if not dir_check.exists():
                try:
                    os.mkdir(dir_path)
                except OSError:
                    print("Directory creation failed (due to system error).")
                    print()
                else:
                    print("Directory successfully created.")
                    print()
            else:
                print("Directory already exist in specified location.")
                print()
            if folder[0] in self.setsCropParams:
                cropParams = self.setsCropParams[folder[0]]
            else:
                cropParams = (30, 30, 715, 1010)
            for file in folder[2]:
                nameFilter = file[2].replace("û", "u")
                newFilePath = folderPaths['imagesForge'] + newFolder + "/" + nameFilter.replace(".png", ".full.jpg")
                file_check = Path(newFilePath)
                if not file_check.is_file():
                    img = Image.open(file[3])
# Crops images by removing border pixels each side (removes most of the card border, depends on the set and settings).
                    croppedImg = img.crop(cropParams)
                    rgbConvertedImg = croppedImg.convert('RGB')
                    rgbConvertedImg.save(newFilePath)
                    print(folder[0] + " : \u001b[36m" + str(folder[2].index(file) + 1) + "\033[00m : " + file[0] + " : successfully converted to : \u001b[32;1m" + newFilePath + "\033[00m")
                else:
                    print("File \u001b[36m" + newFilePath + "\033[00m already exist, skipping to next file.")
            print()
        print()
        print("All images successfully converted and saved in " + folderPaths['imagesForge'])
        print()

    def imageConvertCockatrice(self):
        print("Converting HQ .png files to HQ .jpg files compatible with Cockatrice App:")
        for folder in localFiles:
            dir_path = folderPaths['imagesCockatrice'] + folder[0]
            dir_check = Path(dir_path)
            if not dir_check.exists():
                try:
                    os.mkdir(dir_path)
                except OSError:
                    print("Directory creation failed (due to system error).")
                    print()
                else:
                    print("Directory successfully created.")
                    print()
            else:
                print("Directory already exist in specified location.")
                print()
            for file in folder[2]:
                newFilePath = folderPaths['imagesCockatrice'] + folder[0] + "/" + file[2].replace(".png", ".jpg")
                file_check = Path(newFilePath)
                if not file_check.is_file():
                    if any(numbered in newFilePath for numbered in ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "6.jpg"]):
                        if newFilePath.endswith("1.jpg"):
                            newFilePath = newFilePath.replace("1.jpg", ".jpg")
                            self.cropConvertSave(folder, file, newFilePath)
                    else:
                        self.cropConvertSave(folder, file, newFilePath)
                else:
                    print("File \u001b[36m" + newFilePath + "\033[00m already exist, skipping to next file.")
            print()
        print()
        print("All images successfully converted and saved in " + folderPaths['imagesCockatrice'])
        print()

    def cropConvertSave(self, folder, file, newFilePath):
# Crop images by removing border pixels, converts to RGB .jpg file and save in correct place.
        if folder[0] in self.setsCropParams:
            cropParams = self.setsCropParams[folder[0]]
        else:
            cropParams = (30, 30, 715, 1010)
        img = Image.open(file[3])
        croppedImg = img.crop(cropParams)
        rgbConvertedImg = croppedImg.convert('RGB')
        rgbConvertedImg.save(newFilePath)
        print(folder[0] + " : \u001b[36m" + str(folder[2].index(file) + 1) + "\033[00m : " + file[0] + " : successfully converted to : \u001b[32;1m" + newFilePath + "\033[00m")

    def imageConvertTest(self):
        print("Test grounds:")
        print()
        img = Image.open(folderPaths['imagesScryfall'] + "ALL/Reprisal1.png")
        croppedImg = img.crop((27, 31, 718, 1009))
        rgbConvertedImg = croppedImg.convert('RGB')
        rgbConvertedImg.save(folderPaths['imagesForge'] + "Reprisal1.jpg")
        print("Test successfull!")
        print()

menus = Menus()
startup = Startup()

menus.menuMain()
