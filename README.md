# MtG Arena deck assistant
### Analyses your cardpool to tell you what decks you can play and how many wild cards you need.

## Requirements
* Python 3.6 (or higher)
* requests==2.23.0
* beautifulsoup4==4.8.2

## Usage

1) Enable "Detailed Logs" in MtG Arena and restart the Client: [Official How To](https://mtgarena-support.wizards.com/hc/en-us/articles/360000726823-Creating-Log-Files)
2) If your Arena client is located in a different directory than `C:\Program Files (x86)\Wizards of the Coast\MTGA`, you have to open **src/run.py** in a text editor and edit the value for `ARENA_DIRECTORY` to match the locations on your PC.
3) The default list for formats contains only Standard. If you want additional formats (currently Historic and Brawl) you have to add them to the list `FORMATS`.
4) The `update_decklists` function needs to run once to request the current top decks from mtggoldfish.com. They are saved as txt files in the data/decks folder. For a re-run you can comment that function out. 
5) It is possible to add custom decks as text files to that folder if they match the pattern `r'deck_[0-9]{7}.*\.txt'`.
6) Run **src/run.py** with Python. Make sure that the required modules are installed in your environment.
7) The output is stored as text files in the "summary" directory.
