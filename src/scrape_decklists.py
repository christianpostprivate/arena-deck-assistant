# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from requests import Session
import re
import logging
from time import sleep
from os import path, mkdir, listdir, remove
import threading


base_dir = path.dirname(path.abspath(__file__))

data_folder = path.join(base_dir, '..', 'data')
if not path.isdir(data_folder):
    mkdir(data_folder)

RARITY_CODES = {
    'Mythic': 1,
    'Rare': 2,
    'Uncommon': 3,
    'Common': 4,
    'Basic': 5,
    'Token': 6
}


class Card:
    def __init__(self, cardname, quantity, data=None):
        self.name = cardname
        self.quantity = int(quantity)
        if data:
            self.data = data
        else:
            self.data = {}
        self.rarity = self.data.get('rarity', None)
        self.rarity_code = RARITY_CODES.get(self.rarity, 7)

    def __repr__(self):
        if self.rarity:
            return f'{self.quantity} {self.name} ({self.rarity})'
        else:
            return f'{self.quantity} {self.name}'


class Deck:
    def __init__(self, decklist_string=None):
        self.maindeck = []
        self.sideboard = []
        if decklist_string:
            if '\r' in decklist_string:
                decklist = decklist_string.split('\r\n')
            else:
                decklist = decklist_string.split('\n')
            for _ in range(len(decklist)):
                line = decklist.pop(0)
                if line:
                    quantity = line.split(' ')[0]
                    name = line.replace(quantity, '').strip()
                    self.maindeck.append(Card(name, quantity))
                else:
                    break
            for _ in range(len(decklist)):
                line = decklist.pop(0)
                if line:
                    quantity = line.split(' ')[0]
                    name = line.replace(quantity, '').strip()
                    self.sideboard.append(Card(name, quantity))

    def __repr__(self):
        if self.sideboard:
            repr_string = f'//Maindeck ({self.card_number_maindeck})'
        else:
            repr_string = ''
        for card in self.maindeck:
            repr_string += '\n' + str(card)
        if self.sideboard:
            repr_string += f'\n//Sideboard ({self.card_number_sideboard})'
            for card in self.sideboard:
                repr_string += '\n' + str(card)
        return repr_string

    def contains(self, cardname):
        for card in self.all_cards:
            if '//' in cardname or '//' in card.name:
                if card.name in cardname or cardname in card.name:
                    return card
            else:
                if card.name == cardname:
                    return card
        return None

    @property
    def all_cards(self):
        return self.maindeck + self.sideboard

    @property
    def card_number_total(self):
        return self.card_number_maindeck + self.card_number_sideboard

    @property
    def card_number_maindeck(self):
        return sum([card.quantity for card in self.maindeck])

    @property
    def card_number_sideboard(self):
        return sum([card.quantity for card in self.sideboard])

    def to_file(self, filename):
        if self.sideboard:
            card_list = self.maindeck + list('\n') + self.sideboard
        else:
            card_list = self.maindeck
        card_list = [str(c) + '\n' for c in card_list]
        with open(filename, 'w') as f:
            f.writelines(card_list)


def make_deck_from_url(session, deck_url, deck_name=None,
                       folder=None):
    response = session.get(deck_url)
    if response.status_code == 200:
        if deck_name:
            filename = f'deck_{deck_url.split("/")[-1]}_{deck_name}.txt'
        else:
            filename = f'deck_{deck_url.split("/")[-1]}.txt'
        with open(path.join(folder, filename), 'wb') as f:
            f.write(response.content)
    else:
        logging.error(f'Download of {deck_url} failed.' +
                      f'Status code: {response.status_code}')


def update_decklists(formats, max_number=50, delay=1, app=None):
    decklists_folder = path.join(base_dir, '..', 'data', 'decks')
    if not path.isdir(decklists_folder):
        mkdir(decklists_folder)

    with Session() as s:
        for form in formats:
            form = form.lower()
            goldfish_url = 'https://www.mtggoldfish.com/metagame/{}/full#online'
            response = s.get(goldfish_url.format(form))
            if response.status_code == 200:
                # create a folder for each format
                format_folder = path.join(decklists_folder, form)
                if not path.isdir(format_folder):
                    mkdir(format_folder)
                else:
                    # delete all files in that folder
                    for filename in listdir(format_folder):
                        remove(path.join(format_folder, filename))

                raw_html = BeautifulSoup(response.content, 'html.parser')
                url_tags = raw_html.find_all('a',
                        attrs={'href': re.compile("^/archetype.*#online$")})
                tierdeck_urls = ['https://www.mtggoldfish.com' + tag['href']
                                 for tag in url_tags]

            else:
                logging.error((f'No response from {goldfish_url} ' +
                               f'(Status code {response.status_code})'))

            for url in tierdeck_urls[:max_number]:
                if app and not app.running:
                    return
                response = s.get(url)
                if response.status_code == 200:
                    raw_html = BeautifulSoup(response.content, 'html.parser')
                    download_link = raw_html.find('a',
                                                  attrs={'href': re.compile(
                                                      "^/deck/download/")})
                    deck_title_tag = raw_html.find('h1',
                                                {'class': 'deck-view-title'})
                    deck_title = deck_title_tag.text.split('\n')[1]
                    if download_link:
                        deck_url = ('https://www.mtggoldfish.com' +
                                    download_link['href'])
                        # make_deck_from_url(s, deck_url, deck_title,
                        #                    format_folder)
                        t = threading.Thread(target=make_deck_from_url,
                                             args=[s, deck_url, deck_title,
                                                   format_folder])
                        t.start()
                        logging.info(f'Downloading and saving from {deck_url}')
                sleep(delay)


if __name__ == '__main__':
    update_decklists(['Standard'], max_number=16)
