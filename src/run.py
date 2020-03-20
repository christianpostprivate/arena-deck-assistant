import os

from scrape_decklists import update_decklists
from parse_arena_log import analyse_and_summary
from get_arena_ids import collect_arena_ids

username = os.environ['USERPROFILE']

OUTPUT_LOG = f'{username}\AppData\LocalLow\Wizards Of The Coast\MTGA\output_log.txt'
ARENA_DIRECTORY = 'C:\Program Files (x86)\Wizards of the Coast\MTGA'

# get the card name and ID data from the arena files
collect_arena_ids(ARENA_DIRECTORY)

# specify a list of formats
FORMATS = ['Standard', ]

# update the decklist folders for the given formats
# comment this out if done once
update_decklists(*FORMATS)

# analyse the arena logs and list decks
analyse_and_summary(OUTPUT_LOG, FORMATS)
