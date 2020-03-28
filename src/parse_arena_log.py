# -*- coding: utf-8 -*-
from os import path, listdir, mkdir
import json
import re
import logging

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

    # load card data from arena
    data_folder = path.join(base_dir, '..', 'data')
    with open(path.join(data_folder, 'card_id_by_name.json'), 'r') as f:
        card_ids_by_name = json.load(f)

    with open(path.join(data_folder, 'card_name_by_id.json'), 'r') as f:
        card_name_by_id = json.load(f)

    arena_legal_cards = Deck()
    for name, card_data in card_ids_by_name.items():
        # No Split/adventure card names in decklists
        if '//' in name:
            name = name.split('//')[0].strip()
        card = Card(name, 1, card_data)
        arena_legal_cards.maindeck.append(card)

    arena_legal_cards.to_file(path.join(data_folder,
                                        'arena_legal_cards.txt'))

    # for each item in the inventory, search with the id for the
    # associated card data
    cardpool = Deck()
    for card_id, quantity in card_inventory_log_data.items():
        name = card_name_by_id[card_id]
        card = arena_legal_cards.contains(name)
        cardpool.maindeck.append(Card(card.name, quantity, card.data))

    cardpool.to_file(path.join(data_folder, 'arena_cardpool.txt'))

    # analyse the decklists and compare them to the cardpool
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
                        # if card is in the cardpool, check its quantity
                        if found_card.quantity < card.quantity:
                            rarity = found_card.rarity.capitalize()
                            wc_needed[
                                rarity] += card.quantity - found_card.quantity
                            cards_needed.maindeck.append(
                                Card(card.name,
                                     card.quantity - found_card.quantity,
                                     found_card.data)
                            )
                    else:
                        try:
                            card_in_deck = arena_legal_cards.contains(
                                card.name)
                            if card_in_deck:
                                rarity = card_in_deck.rarity.capitalize()
                                wc_needed[rarity] += card.quantity
                                cards_needed.maindeck.append(
                                    Card(card.name, card.quantity,
                                         card_in_deck.data))
                        except KeyError:
                            logging.info(f'No rarity information for {card.name}')

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
                    wc_balances['Mythic'], wc_balances['Rare'],
                    wc_balances['Uncommon'], wc_balances['Common'],
                    cards_needed
                ])

            # sort the results (by number of mythic and rare WC needed)
            results = sorted(results,
                             key=lambda x: x[5] + x[6],
                             reverse=False)
            for i, r in enumerate(results):
                r[0] = i + 1
                output += DECK_STRING.format(*r)
                # sort by Rarity (Mythic first)
                for card in sorted(r[9].maindeck, key=lambda c: c.rarity_code):
                    output += f'   {card}\n'
                output += '\n'

            output_folder = path.join(base_dir, '..', 'summary')
            if not path.isdir(output_folder):
                mkdir(output_folder)
            filename = path.join(output_folder, f'summary_{form}.txt')
            with open(filename, 'w') as f:
                f.write(output)

            logging.info(f'Summary for {form} saved as summary\summary_{form}.txt')
            total_output += output

    return total_output


if __name__ == '__main__':
    from os import environ
    username = environ['USERPROFILE']

    OUTPUT_LOG = f'{username}\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\output_log.txt'
    out = analyse_and_summary(OUTPUT_LOG, ['Standard'])
