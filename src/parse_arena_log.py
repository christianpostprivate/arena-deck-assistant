from os import path, listdir, mkdir
from time import sleep
from requests import Session
import json
import re

from scrape_decklists import Card, Deck
from summary_strings import DECKLIST_SUMMARY, DECK_STRING

base_dir = path.dirname(path.abspath(__file__))

RARITIES = [
    'Common',
    'Uncommon',
    'Rare',
    'Mythic'
]

BASIC_LANDS = [
    'Plains',
    'Island',
    'Swamp',
    'Mountain',
    'Forest'
]


def parse_logfile(file):
    logfile_dict = {}
    with open(file, 'r') as f:
        logfile_lines = f.readlines()

    for lf in logfile_lines:
        if lf.startswith('[UnityCrossThreadLogger]'):
            lf = lf.replace('[UnityCrossThreadLogger]', '')
            lf = lf.replace('<==', '').replace('==>', '')
            splitted = [item for item in lf.split(' ') if item != '']
            try:
                key = splitted[0]
                value = ' '.join(splitted[1:])
                logfile_dict[key] = json.loads(value)
            except ValueError:
                pass

    return logfile_dict


def filter_cardlist(cardlist, formats):
    filtered_cards = []
    for card in cardlist:
        print(card['name'])
        if any([card['legalities'][f] == 'legal' for f in formats]):
            filtered_cards.append(card)
    return filtered_cards


def analyse_and_summary(output_log, formats, app=None):
    # parse the MtG Arena log file
    log = parse_logfile(output_log)
    # card pool data
    try:
        card_inventory_log_data = log['PlayerInventory.GetPlayerCardsV3'][
            'payload']
        # wild cards, gold, gems etc
        inventory_log_data = log['PlayerInventory.GetPlayerInventory'][
            'payload']
    except KeyError:
        return ('Failed to read data from output log. Make sure ' +
                'detailed logging in the MtG Arena client is active.\n' +
                'For instructions see:\n' +
                'https://mtgarena-support.wizards.com/hc/en-us/articles/360000726823-Creating-Log-Files')
    # make API call to scryfall to get the current legal cardpool
    data_folder = path.join(base_dir, '..', 'data')
    cardbase = path.join(data_folder, 'arena_legal_cards.json')
    if not path.exists(cardbase):
        with Session() as s:
            scryfall_url = ('https://api.scryfall.com/cards/search?q=' +
                            'legal:historic')
            print('Requesting card data from scryfall.com')
            done = False
            page = 1
            card_data = []
            while not done:
                if app and not app.running:
                    return
                response = s.get(scryfall_url)
                if response.status_code == 200:
                    data = json.loads(response.text)
                    total_pages = data['total_cards'] // len(data['data']) + 1
                    print(f'reading page {page} of {total_pages}')
                    card_data += data['data']
                    if data['has_more']:
                        scryfall_url = data['next_page']
                        page += 1
                    else:
                        done = True
                        break
                else:
                    done = True
                    print(f'no response from page {scryfall_url}')
                sleep(2)
        with open(cardbase, 'w') as f:
            json.dump(card_data, f)
    else:
        with open(cardbase, 'r') as f:
            card_data = json.load(f)

    # load card data from arena
    with open(path.join(data_folder, 'card_id_by_name.json'), 'r') as f:
        card_ids_by_name = json.load(f)

    with open(path.join(data_folder, 'card_name_by_id.json'), 'r') as f:
        card_name_by_id = json.load(f)

    # search for arena IDs of the arena log and make a deck list
    cardpool = Deck()
    # make a dictionary with 'card_id': card_data
    card_data_by_id = {}
    card_data_by_name = {}
    # a Deck object with each card's data
    card_deck = Deck()
    for card in card_data:
        if '//' in card['name']:
            card['name'] = card['name'].split('//')[0].strip()
        card_data_by_name[card['name']] = card
        try:
            card_data_by_id[f'{card["arena_id"]}'] = card
            card_deck.maindeck.append(Card(card['name'], 1, card))
        except KeyError:
            # can't find ID in scryfall data
            try:
                arena_ids = card_ids_by_name[card['name']]
                for id_ in arena_ids:
                    card_data_by_id[f'{id_}'] = card
                card_deck.maindeck.append(Card(card['name'], 1, card))
            except KeyError:
                print(f'No data for {card["name"]}')

    # for each item in the inventory, search with the id for the
    # associated card data
    for card_id, quantity in card_inventory_log_data.items():
        try:
            cdata = card_data_by_id[card_id]
            card = Card(cdata['name'], quantity, cdata)
            # print(card)
            cardpool.maindeck.append(card)
        except KeyError:
            c_name = card_name_by_id[card_id]
            cdata = card_data_by_name[c_name]
            card = Card(c_name, quantity, cdata)

    cardpool.to_file(path.join(data_folder, 'arena_cardpool.txt'))

    total_output = ''

    for form in formats:
        # look for decklists in folders
        form = form.lower()
        format_folder = path.join(data_folder, 'decks', form)
        if path.isdir(format_folder):
            all_files = listdir(format_folder)
            decklist_files = [path.join(format_folder, f) for f in all_files if
                              re.match(r'deck_[0-9]{7}.*\.txt', f)]

            # header of output string
            wc_owned = {rarity: inventory_log_data[f'wc{rarity}'] for rarity
                        in RARITIES}
            output = DECKLIST_SUMMARY.format(
                form.capitalize(), len(decklist_files), wc_owned['Common'],
                wc_owned['Uncommon'], wc_owned['Rare'], wc_owned['Mythic'],
            )

            results = []

            for i, file in enumerate(decklist_files):
                with open(file, 'r') as f:
                    decklist_string = f.read()
                deck = Deck(decklist_string)
                cards_needed = Deck()
                # calculate how much wild cards are needed
                wc_needed = {rarity: 0 for rarity in RARITIES}
                for card in deck.all_cards:
                    if card.name in BASIC_LANDS:
                        continue
                    found_card = cardpool.contains(card.name)
                    if found_card:
                        # check quantity
                        if found_card.quantity < card.quantity:
                            rarity = found_card.data['rarity'].capitalize()
                            wc_needed[
                                rarity] += card.quantity - found_card.quantity
                            cards_needed.maindeck.append(
                                Card(card.name,
                                     card.quantity - found_card.quantity)
                            )
                    else:
                        try:
                            card_in_deck = card_deck.contains(card.name)
                            if card_in_deck:
                                rarity = card_in_deck.data[
                                    'rarity'].capitalize()
                                wc_needed[rarity] += card.quantity
                                cards_needed.maindeck.append(
                                    Card(card.name, card.quantity))
                        except KeyError:
                            print(f'No rarity information for {card.name}')

                wc_balances = {}
                for rarity in RARITIES:
                    wc_balances[rarity] = max(0, wc_needed[rarity] -
                                              wc_owned[rarity])

                split_string = file.split('\\')[-1].split('_')
                name = split_string[-1][:-4]
                id_ = split_string[1]

                results.append([
                    None, name, id_,
                    deck.card_number_total - cards_needed.card_number_total,
                    deck.card_number_total,
                    wc_needed['Mythic'], wc_needed['Rare'],
                    wc_needed['Uncommon'], wc_needed['Common'],
                    cards_needed
                ])

            # sort the results (by number of mythic and rare WC needed)
            results = sorted(results,
                             key=lambda x: x[5] + x[6],
                             reverse=False)
            for i, r in enumerate(results):
                r[0] = i + 1
                output += DECK_STRING.format(*r)
                for card in r[9].maindeck:
                    output += f'   {card}\n'
                output += '\n'

            output_folder = path.join(base_dir, '..', 'summary')
            if not path.isdir(output_folder):
                mkdir(output_folder)
            filename = path.join(output_folder, f'summary_{form}.txt')
            with open(filename, 'w') as f:
                f.write(output)

            print(f'Summary for {form} saved as summary\summary_{form}.txt')

            total_output += output

    return total_output

if __name__ == '__main__':
    analyse_and_summary()
