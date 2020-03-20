import json
from os import path

# grpid = Arena card id
# titleId = localisation id

base_dir = path.dirname(path.abspath(__file__))
data_folder = path.join(base_dir, '..', 'data')

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

    card_ids_by_name = {}
    for card in data_cards:
        name = card_name_by_id[card['titleId']]
        if name in card_ids_by_name.keys():
            card_ids_by_name[name].append(card[str('grpid')])
        else:
            card_ids_by_name[name] = [card[str('grpid')]]

    return card_ids_by_name


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


def collect_arena_ids(data_cards_file, data_loc_file):
    d = get_names_from_id(data_cards_file, data_loc_file)
    with open(path.join(data_folder, 'card_id_by_name.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f)

    d = get_ids_from_name(data_cards_file, data_loc_file)
    with open(path.join(data_folder, 'card_name_by_id.json'), 'w',
              encoding='utf-8') as f:
        json.dump(d, f)


if __name__ == '__main__':
    DATA_CARDS_FILE = 'C:\Program Files (x86)\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Data\data_cards_296741a1382e4e59c7e0e658f9ff376c.mtga'
    DATA_LOC_FILE = 'C:\Program Files (x86)\Wizards of the Coast\MTGA\MTGA_Data\Downloads\Data\data_loc_c9f4f3eee920063a46a2d4a42654ab5b.mtga'

    d = get_names_from_id(DATA_CARDS_FILE, DATA_LOC_FILE)
    with open(path.join(data_folder, 'card_id_by_name.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f)

    d = get_ids_from_name(DATA_CARDS_FILE, DATA_LOC_FILE)
    with open(path.join(data_folder, 'card_name_by_id.json'), 'w', encoding='utf-8') as f:
        json.dump(d, f)

