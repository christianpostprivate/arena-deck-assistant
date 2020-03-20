from os import path, environ
import json

from scrape_decklists import update_decklists
from parse_arena_log import analyse_and_summary
from get_arena_ids import collect_arena_ids

base_dir = path.dirname(path.abspath(__file__))
data_folder = path.join(base_dir, '..', 'data')

with open(path.join(data_folder, 'settings.json'), 'r') as f:
    settings = json.load(f)

username = environ['USERPROFILE']

OUTPUT_LOG = f'{username}\AppData\LocalLow\Wizards Of The Coast\MTGA\output_log.txt'

# get the card name and ID data from the arena files
collect_arena_ids(settings['ARENA_DIRECTORY'])

# update the decklist folders for the given formats
if settings['UPDATE_DECKLISTS']:
    update_decklists(*settings['FORMATS'])

# analyse the arena logs and list decks
analyse_and_summary(OUTPUT_LOG, settings['FORMATS'])
input(' ')
