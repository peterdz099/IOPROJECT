from tkinter import filedialog
import pandas as pd
from webscraper import scraper

def delete_columns(dicti):
    cols = ['shop_list', 'photo_url', 'id']
    return {key: dicti[key] for key in dicti if key not in cols}

def load_file_and_save_to_excel():
    filename = filedialog.askopenfilename(initialdir="c:/pdw",
                                          title="Select a xlsx file",
                                          filetypes=(("xlsx files", "*.xlsx"), ("all files", "*.*")))
    list = pd.read_excel(filename, header=None).iloc[:,0].tolist()
    offer_list = []
    for search in list:
        search = search.replace(' ','+')
        ws = scraper(search)
        ws.sort(key=lambda t: t.min_price)
        offer_list.append(ws[0])
    df = pd.DataFrame([delete_columns(vars(s)) for s in offer_list])
    df.to_excel('wyniki.xlsx')
    return list

def save_cart_to_file(cart_df):
    # toy_name, price, url, shop_name, manufacturer, img_url
    cart_df.to_excel('koszyk.xlsx')


