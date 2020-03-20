# MtG Arena deck assistant
### Analyses your cardpool to tell you what decks you can play and how many wild cards you need.

## Requirements
* Python 3.6 (or higher)
* requests==2.23.0
* beautifulsoup4==4.8.2

## Usage

1) Enable "Detailed Logs" in MtG Arena and restart the Client: [Official How To](https://mtgarena-support.wizards.com/hc/en-us/articles/360000726823-Creating-Log-Files)
2) If your Arena client is located in a different directory than "C:\Program Files (x86)\Wizards of the Coast\MTGA\", you have to open **src/run.py** in a text editor and edit the values for `DATA_CARDS_FILE` and `DATA_LOC_FILE` to match your locations (Tip: On Windows, Shift + Right click on the files and select "copy as path" to copy the path to your clipboard, then paste it into the python file).
3) Run **src/run.py** with Python. Make sure that the required modules are installed in your environment.
4) The output is stored as text files in the "summary" directory.
