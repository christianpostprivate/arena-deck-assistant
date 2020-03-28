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
1) A windows executable is found in `arena-deck-assistant-Windows` under `src\arena-deck-assistant.exe`.
2) Make sure the paths for the `Wizards of the Coast\MTGA` folder and the `output_log.txt` file match the paths on your PC. If not, use the `Browse` button to select them via the file explorer.
3) Select at least one format.
4) Check the `Update downloaded decks?`to request the current top decks from mtggoldfish.com. They are saved as txt files in the data/decks folder. For a re-run you can leave this box unchecked to save time.
5) The parameter `max number of downloaded decks` limits the number of decks that are downloaded from mtggoldfish. `None` means all available lists will be downloaded and saved.
6) Click `Analyse` to begin the analysis. A popup will appear once the process is finished. The output is also stored as a text file in the "summary" directory.

### Python
1) Run **src/run.py** with Python. Make sure that the required modules are installed in your environment.
2) The remaining process is the same as described under "Windows executable".
