import os

from scrape_decklists import update_decklists
from parse_arena_log import analyse_and_summary
from get_arena_ids import collect_arena_ids

username = os.environ['USERPROFILE']

OUTPUT_LOG = f'{username}\AppData\LocalLow\Wizards Of The Coast\MTGA\output_log.txt'

DATA_CARDS_FILE = 'C:\Program Files (x86)\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Data\data_cards_296741a1382e4e59c7e0e658f9ff376c.mtga'
DATA_LOC_FILE = 'C:\Program Files (x86)\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Data\data_loc_c9f4f3eee920063a46a2d4a42654ab5b.mtga'

# get the card name and ID data from the arena files
collect_arena_ids(DATA_CARDS_FILE, DATA_LOC_FILE)

# specify a list of formats
FORMATS = ['Standard', ]

# update the decklist folders for the given formats
# comment this out if done once
#update_decklists(*FORMATS)

# analyse the arena logs and list decks
analyse_and_summary(OUTPUT_LOG, FORMATS)
