from tkinter import filedialog
import pandas as pd
from webscraper import scraper


def delete_columns(dicti):
    cols = ['shop_list', 'photo_url', 'id']
    return {key: dicti[key] for key in dicti if key not in cols}


def load_file_and_save_to_csv(mode, sort_mode):
    filename = filedialog.askopenfilename(initialdir="c:/pdw",
                                          title="Select a csv file",
                                          filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
    if filename == '':
        return []
    listing = pd.read_csv(filename, header=None).iloc[:, 0].tolist()
    offer_list = []
    for search in listing:
        search = search.replace(' ', '+')
        ws = scraper(search, mode, sort_mode)
        if ws:
            offer_list.append(ws[0])
        else:
            offer_list.append("NOT FOUND")

    #df = pd.DataFrame([delete_columns(vars(s)) for s in offer_list])
    #df.to_csv('wyniki.csv')
    # test
    return offer_list


def save_cart_to_file(offer_list):
    df = pd.DataFrame(offer_list)
    df.to_csv('koszyk.csv')
