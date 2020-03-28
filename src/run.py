# -*- coding: utf-8 -*-
"""
TODO:
- each deck download as a separate thread
"""
from os import path, environ
import json
import threading
from collections import deque
import PySimpleGUI as sg
import logging

from scrape_decklists import update_decklists
from parse_arena_log import analyse_and_summary
from get_arena_ids import collect_arena_ids


base_dir = path.dirname(path.abspath(__file__))
data_folder = path.join(base_dir, '..', 'data')

username = environ['USERPROFILE']
DEFAULT_LOG_FOLDER = f'{username}\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\'
OUTPUT_LOG = DEFAULT_LOG_FOLDER + 'output_log.txt'

logfile = f'{path.basename(__file__).strip(".py")}.log'

logging.basicConfig(filename=path.join(base_dir, '..', logfile),
                    level=logging.INFO,
                    format='%(asctime)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


class CustomOutput(sg.Output):
    """
    Wrapper for the PySimpleGUI Output class to work properly with logging
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def write(self, txt):
        # txt = self.Get().strip() + '\n' + txt
        txt = txt + self.Get().strip()
        self.Update(value=txt)


class App:
    def __init__(self):
        with open(path.join(data_folder, 'settings.json'), 'r') as f:
            self.settings = json.load(f)

        sg.theme('DarkAmber')   # Add a touch of color
        # All the stuff inside your window.
        layout = [[sg.Text('')],
          [sg.Text('Path to MTGA folder:             '),  # TODO: wow such lazy
           sg.InputText(self.settings['ARENA_DIRECTORY']),
           sg.FolderBrowse(initial_folder=self.settings['ARENA_DIRECTORY'])],
          [sg.Text('Path to MTGA output_log.txt: '), sg.InputText(OUTPUT_LOG),
           sg.FileBrowse(file_types=(("Text Files", "*.txt"),),
                         initial_folder=DEFAULT_LOG_FOLDER)],
          [sg.Text('Formats to analyse (Select one or more): '),
           sg.Listbox(values=('Standard', 'Historic', 'Brawl'),
                      size=(20, 3),
                      select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE)],
          [sg.Checkbox(text='Update downloaded decks?',
                       default=self.settings['UPDATE_DECKLISTS'])],
          [sg.Text('Max. number of downloaded decks: '),
           sg.Spin(values=[None] +
                   list(range(1, self.settings['DECKLIST_MAX_NUMBER'] + 1)),
                   size=(5, 1))],
          [sg.Text('_' * 80)],
          [CustomOutput(size=(80, 6), key='_CONSOLE_')],
          [sg.Multiline(default_text='No results yet.',
                        size=(80, 30),
                        disabled=True,
                        key='_OUTPUT_')],
          [sg.Button('Analyse', key='_RUN_'),
           sg.Button('Cancel', key='_CANCEL_')]]

        # Create the Window
        self.window = sg.Window('Arena Deck Assistant', layout)
        # add logging to console
        logging.getLogger().addHandler(
            logging.StreamHandler(self.window['_CONSOLE_']))

        self.results = deque()
        self.stop_threads = threading.Event()
        self.running = True

    def arena_analysis(self, values):
        collect_arena_ids(self.settings['ARENA_DIRECTORY'])
        # update the decklist folders for the given formats
        if values[3]:
            update_decklists(values[2], max_number=values[4],
                             delay=self.settings['DOWNLOAD_DELAY'],
                             app=self)
        # analyse the arena logs and list decks
        result = analyse_and_summary(OUTPUT_LOG, values[2], app=self)
        self.results.append(result)

    def run(self):
        while self.running:
            event, values = self.window.read(timeout=100)
            if event in (None, '_CANCEL_'):
                # if user closes window or clicks cancel
                self.running = False
            elif event in (None, '_RUN_'):
                if values[2]:
                    analysis = threading.Thread(target=self.arena_analysis,
                                                args=[values])
                    analysis.start()
                    self.window.Element('_OUTPUT_').Update(
                        value='Waiting for results')
                    self.window.Element('_CONSOLE_').Update(
                        value='')
                    self.window.Element('_RUN_').Update(disabled=True)
                else:
                    sg.Popup('Select at least one format!')
            if len(self.results) >= 1:
                self.window.Element('_OUTPUT_').Update(
                    value=self.results.pop())
                self.window.Element('_RUN_').Update(disabled=False)
        self.window.close()


if __name__ == '__main__':
    app = App()
    app.run()
