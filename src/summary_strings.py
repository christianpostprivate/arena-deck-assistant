DECKLIST_SUMMARY = """
###############################################################################
------ Summary for the {0} format ------

Analysed decks: {1}

Wild card inventory:
  Common: {2}
  Uncommon: {3}
  Rare: {4}
  Mythic: {5}

Decks ranked by # of Mythic and Rare wild cards missing:
"""


DECK_STRING = """
{0}. {1}
  https://www.mtggoldfish.com/deck/{2}

  Cards in collection:
  {3} / {4}
  Additional wild cards needed:
  {5} M, {6} R, {7} UC, {8} C
  
  Cards needed:
"""


if __name__ == '__main__':
    # Just for testing
    d1 = DECK_STRING.format(
        '1',
        'Jeskai Fires',
        '2825983',
        '30', '75',
        '3', '8', '3', '0'
    )
    d2 = DECK_STRING.format(
        '2',
        'Mono-Red Aggro',
        '2825985',
        '20', '75',
        '3', '8', '3', '0'
    )
    d3 = DECK_STRING.format(
        '3',
        'Jund Food',
        '2825986',
        '45', '75',
        '3', '8', '3', '0'
    )

    ds = DECKLIST_SUMMARY.format(
        'Standard',
        '10',
        '1', '2', '3', '4'
    )
    for d in (d1, d2, d3):
        ds += d

    print(ds)
