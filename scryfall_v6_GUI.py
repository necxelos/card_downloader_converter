# CORE PYTHON IMPORTS:
import os
import time
import json
import threading
from pathlib import Path
from datetime import datetime
# EXTERNAL LIBRARY IMPORTS (pip installed):
import requests
from tinydb import TinyDB, Query
# KIVY GENERAL IMPORTS & SETTINGS:
from kivy.app import App
from kivy.config import Config
Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '768')
# KIVY SPECIFIC IMPORTS:
from kivy.clock import Clock
from functools import partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

# GLOBAL VARIABLES:
global file_structure
file_structure = {'database_files':{'local':"Database Files/Local/", 'scryfall':"Database Files/Scryfall/"}}
global required_files
required_files = {
                  'local':   {'cards':"local-default-cards.json",    'sets':"local-sets.json",    'rulings':"local-rulings.json",    'meta':"local-meta.json"},
                  'scryfall':{'cards':"scryfall-default-cards.json", 'sets':"scryfall-sets.json", 'rulings':"scryfall-rulings.json", 'meta':"scryfall-meta.json"}
                 }
global scryfall_sources
scryfall_sources = {
                    'API':  {
                             'cards':"",
                             'sets':"https://api.scryfall.com/sets",
                             'rulings':"",
                             'meta':"https://api.scryfall.com/bulk-data"
                            },
                    'files':{
                             'cards':"https://archive.scryfall.com/json/scryfall-default-cards.json",
                             'sets':"",
                             'rulings':"https://archive.scryfall.com/json/scryfall-rulings.json",
                             'meta':""
                            }
                   }

class ManageSets(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ManageCards(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class ConvertImages(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# Database Download, Convert and Files Check:
class ImportExportDatabase(AnchorLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files_check()

    def files_check(self):
# Display (at start or refresh after change) all information about .JSON files required by this app.
        label_ids = {
                     'exist':{
                              'local':{   'cards':self.ids.local_cards_file_exist,    'sets':self.ids.local_sets_file_exist,    'rulings':self.ids.local_rulings_file_exist,    'meta':self.ids.local_meta_file_exist},
                              'scryfall':{'cards':self.ids.scryfall_cards_file_exist, 'sets':self.ids.scryfall_sets_file_exist, 'rulings':self.ids.scryfall_rulings_file_exist, 'meta':self.ids.scryfall_meta_file_exist}
                             },
                     'date':{
                             'local':{   'cards':self.ids.local_cards_file_date,    'sets':self.ids.local_sets_file_date,    'rulings':self.ids.local_rulings_file_date,    'meta':self.ids.local_meta_file_date},
                             'scryfall':{'cards':self.ids.scryfall_cards_file_date, 'sets':self.ids.scryfall_sets_file_date, 'rulings':self.ids.scryfall_rulings_file_date, 'meta':self.ids.scryfall_meta_file_date},
                            }
                    }
        today_date = datetime.strptime(str(datetime.now())[0:10], '%Y-%m-%d').date()
        for k1, v1 in required_files.items():
            for k2, v2 in v1.items():
                path = file_structure['database_files'][k1] + v2
                if Path(path).is_file():
                    label_ids['exist'][k1][k2].text = "File Exists!"
                    label_ids['exist'][k1][k2].color = (0, 1, 0, 1)
                    modification_date = datetime.strptime(str(datetime.fromtimestamp(os.path.getmtime(path)))[0:10], '%Y-%m-%d').date()
                    label_ids['date'][k1][k2].text = str(modification_date) + " which is " + str((today_date - modification_date).days) + " days ago."
                elif not Path(file_structure['database_files'][k1] + v2).is_file():
                    label_ids['exist'][k1][k2].text = "File Missing!"
                    label_ids['exist'][k1][k2].color = (1, 0, 0, 1)
                    label_ids['date'][k1][k2].text = ""

    def download_to_JSON(self, data_choice):
        if data_choice in ["sets", "meta"]:
            source_url = scryfall_sources['API'][data_choice]
        elif data_choice in ["cards", "rulings"]:
            source_url = scryfall_sources['files'][data_choice]
        file_path = file_structure['database_files']['scryfall'] + required_files['scryfall'][data_choice]
        if source_url != "" and not Path(file_path).is_file():
            response = requests.get(source_url)
            if data_choice in ["sets", "meta"]:
                data = response.json()['data']
            elif data_choice in ["cards", "rulings"]:
                data = response.json()
            with open(file_path, 'w') as file:
                file.write('[\n')
                for item in data:
                    file.write('  ')
                    json.dump(item, file)
                    if data.index(item) != (len(data) - 1):
                        file.write(',\n')
                    else:
                        file.write('\n')
                file.write(']')
            del response
            del data
            self.files_check()

    def convert_to_tinyDB(self, file_choice):
        threading.Thread(target=self.convert_to_tinyDB_method_itself, args=(file_choice,)).start()

    def convert_to_tinyDB_method_itself(self, file_choice):
        source_file = file_structure['database_files']['scryfall'] + required_files['scryfall'][file_choice]
        result_file = file_structure['database_files']['local'] + required_files['local'][file_choice]
        if Path(source_file).is_file() and not Path(result_file).is_file():
            with open (source_file, 'r', encoding="utf-8") as file:
                data = json.load(file)
            self.ids.process_progress_pb.max = len(data)
            self.ids.process_progress_pb.value = 0
            self.ids.process_progress_pb.opacity = 1
            self.ids.process_progress_l.opacity = 1
            with open(result_file, 'w') as file:
                file.write('{\n')
                file.write('    "_default":{\n')
                for item in data:
                    file.write('        ')
                    file.write('"' + str(data.index(item)) + '":')
                    json.dump(item, file)
                    if data.index(item) != (len(data) - 1):
                        file.write(',\n')
                    else:
                        file.write('\n')
                    Clock.schedule_once(partial(self.convert_to_tinyDB_update_GUI))
                file.write('    }\n')
                file.write('}')
            del data
            self.files_check()
            time.sleep(0.5)
            self.ids.process_progress_pb.max = 100
            self.ids.process_progress_pb.value = 0
            self.ids.process_progress_pb.opacity = 0
            self.ids.process_progress_l.text = ""
            self.ids.process_progress_l.opacity = 0

    def convert_to_tinyDB_update_GUI(self, dt):
        self.ids.process_progress_pb.value += 1
        self.ids.process_progress_l.text = str("{:.1%}".format(int(self.ids.process_progress_pb.value)/int(self.ids.process_progress_pb.max)))

# Top Level Kivy Interface:
class ScryfallRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.local_cards_db_path = file_structure['database_files']['local'] + required_files['local']['cards']
        self.local_sets_db_path = file_structure['database_files']['local'] + required_files['local']['sets']
        self.local_rulings_db_path = file_structure['database_files']['local'] + required_files['local']['rulings']
        self.local_meta_db_path = file_structure['database_files']['local'] + required_files['local']['meta']
        if not Path(self.local_cards_db_path).is_file() or not Path(self.local_sets_db_path).is_file() or not Path(self.local_rulings_db_path).is_file() or not Path(self.local_meta_db_path).is_file():
            self.ids.button_manage_sets.disabled = True
            self.ids.button_manage_cards.disabled = True
            self.ids.button_convert_images.disabled = True

    def sectionPick(self, instance, item):
        if item == 1:
            self.ids.activeSection.clear_widgets()
            manageSets = ManageSets()
            self.ids.activeSection.add_widget(manageSets)
        elif item == 2:
            self.ids.activeSection.clear_widgets()
            manageCards = ManageCards()
            self.ids.activeSection.add_widget(manageCards)
        elif item == 3:
            self.ids.activeSection.clear_widgets()
            convertImages = ConvertImages()
            self.ids.activeSection.add_widget(convertImages)
        elif item == 4:
            self.ids.activeSection.clear_widgets()
            importExportDatabase = ImportExportDatabase()
            self.ids.activeSection.add_widget(importExportDatabase)

# Root Kivy Class:
class Scryfall_v6App(App):
    def build(self):
        return ScryfallRoot()

# App starter:
if __name__ == '__main__':
    Scryfall_v6App().run()

# local_DB = TinyDB('local-default-cards.json')
#
# cards = Query()
#
# print(len(local_DB.search(cards.set == "mrd")))
