import json
from os import path, listdir
import re

# grpid = Arena card id
# titleId = localisation id

base_dir = path.dirname(path.abspath(__file__))
data_folder = path.join(base_dir, '..', 'data')

RARITIES = {
    # Rarity codes from data_cards_
    0: 'Token',
    1: 'Basic',
    2: 'Common',
    3: 'Uncommon',
    4: 'Rare',
    5: 'Mythic Rare'
}


def get_names_from_id(data_cards_file, data_loc_file):
    try:
        with open(data_cards_file, 'r', encoding='utf-8') as f:
            data_cards = json.load(f)

        with open(data_loc_file, 'r', encoding='utf-8') as f:
            data_loc = json.load(f)
    except FileNotFoundError:
        print('Can not find card data files.')
        return

    # connect card id with names
    card_name_by_id = {}
    for data_dict in data_loc:
        if data_dict['isoCode'] == 'en-US':
            for id_text in data_dict['keys']:
                card_name_by_id[id_text['id']] = id_text['text']

    card_data_by_name = {}
    for card in data_cards:
        name = card_name_by_id[card['titleId']]
        card_data_by_name[name] = {}
        card_data_by_name[name]['rarity'] = RARITIES[card['rarity']]
        # add ID information
        # there are multiple IDs for the same name
        if 'ID' in card_data_by_name[name].keys():
            card_data_by_name[name]['ID'].append(card[str('grpid')])
        else:
            card_data_by_name[name]['ID'] = [card[str('grpid')]]

    return card_data_by_name


def get_ids_from_name(data_cards_file, data_loc_file):
    try:
        with open(data_cards_file, 'r', encoding='utf-8') as f:
            data_cards = json.load(f)

        with open(data_loc_file, 'r', encoding='utf-8') as f:
            data_loc = json.load(f)
    except FileNotFoundError:
        print('Can not find card data files.')
        return

    card_name_by_title_id = {}
    for data_dict in data_loc:
        if data_dict['isoCode'] == 'en-US':
            for id_text in data_dict['keys']:
                card_name_by_title_id[id_text['id']] = id_text['text']

    card_name_by_id = {}
    for card in data_cards:
        name = card_name_by_title_id[card['titleId']]
        arena_id = card['grpid']
        card_name_by_id[arena_id] = name

    return card_name_by_id


def collect_arena_ids(arena_directory):
    arena_directory += '\\MTGA_Data\\Downloads\\Data'
    files = listdir(arena_directory)
    r_cards = re.compile(r'^data_cards.*.mtga$')
    r_loc = re.compile(r'^data_loc.*.mtga$')
    data_cards_file = (arena_directory + '\\' +
                       list(filter(r_cards.match, files))[0])
    data_loc_file = (arena_directory + '\\' +
                     list(filter(r_loc.match, files))[0])

    d = get_names_from_id(data_cards_file, data_loc_file)
    with open(path.join(data_folder, 'card_id_by_name.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f)

    d = get_ids_from_name(data_cards_file, data_loc_file)
    with open(path.join(data_folder, 'card_name_by_id.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f)


if __name__ == '__main__':
    # for testing
    ARENA_DIRECTORY = 'C:\\Program Files (x86)\\Wizards of the Coast\\MTGA'
    ARENA_DIRECTORY += '\\MTGA_Data\\Downloads\\Data'

    files = listdir(ARENA_DIRECTORY)

    r_cards = re.compile(r'^data_cards.*.mtga$')
    r_loc = re.compile(r"^data_loc.*.mtga$")

    DATA_CARDS_FILE = ARENA_DIRECTORY + '\\' + list(filter(r_cards.match, files))[0]
    DATA_LOC_FILE = ARENA_DIRECTORY + '\\' + list(filter(r_loc.match, files))[0]
    d = get_names_from_id(DATA_CARDS_FILE, DATA_LOC_FILE)
    with open(path.join(data_folder, 'card_id_by_name.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f)

    d = get_ids_from_name(DATA_CARDS_FILE, DATA_LOC_FILE)
    with open(path.join(data_folder, 'card_name_by_id.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f)

