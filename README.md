# MtG Arena deck assistant
### Analyses your cardpool to tell you what decks you can play and how many wild cards you need.

## Requirements
* Python 3.6 (or higher)
* requests==2.23.0
* beautifulsoup4==4.8.2
* PySimpleGUI==4.16.0

## Usage
### General

1) Enable "Detailed Logs" in MtG Arena and restart the Client: [Official How To](https://mtgarena-support.wizards.com/hc/en-us/articles/360000726823-Creating-Log-Files)

### Windows executable
1) A windows executable is located under `dist/src/arena-deck-assistant.exe`.
2) Make sure the paths for the `Wizards of the Coast\MTGA` folder and the `output_log.txt` file match the paths on your PC. If not, use the `Browse` button to select them via the file explorer.
3) Select at least one format.
4) Check the `Update downloaded decks?`to request the current top decks from mtggoldfish.com. They are saved as txt files in the data/decks folder. For a re-run you can leave this box unchecked to save time.
5) The parameter `max number of downloaded decks` limits the number of decks that are downloaded from mtggoldfish. `None` means all available lists will be downloaded and saved.
6) Click `Analyse` to begin the analysis. A popup will appear once the process is finished. The output is also stored as a text file in the "summary" directory.

### Python
#### With PySimpleGUI
1) Run **src/run_gui.py** with Python. Make sure that the required modules are installed in your environment.
2) The remaining process is the same as described under "Windows executable".

### Without PySimpleGUI
1) If your Arena client is located in a different directory than `C:\Program Files (x86)\Wizards of the Coast\MTGA`, you have to open **data/settings.json** in a text editor and edit the value for `ARENA_DIRECTORY` to match the location on your PC.
2) The default list for formats contains only Standard. If you want additional formats (currently Historic and Brawl) you have to add them to the list `FORMATS`.
3) The `UPDATE_DECKLISTS` function needs to run once to request the current top decks from mtggoldfish.com. They are saved as txt files in the data/decks folder. For a re-run you can set this value to `false`to save time. 
4) It is possible to add custom decks as text files to that folder if they match the pattern `r'deck_[0-9]{7}.*\.txt'` and the arena deck text file formatting.
5) Run **src/run.py** with Python. Make sure that the required modules are installed in your environment.
6) The output is stored as a text file in the "summary" directory.

