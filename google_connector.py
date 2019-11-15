import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


def connect_to_gspread(json_filename):
    """
    An instance for communications with Google API.
    Thanks to Vincent Shields for incredible instructions regarding the credentials:
    https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf
    :param json_filename: credentials file
    :return: an instance of type Client
    """
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        json_filename, scope)
    gs = gspread.authorize(credentials)
    return gs


def load_table(json_filename, table_name):
    """
    load a table from google spreadsheets from sheet 1
    :param json_filename: Path to Google API credentials file .json
    :param table_name: String. A name of the table
    :return: pandas.DataFrame()
    """
    gs = connect_to_gspread(json_filename)
    w = gs.open(table_name).sheet1
    data = w.get_all_values()
    return pd.DataFrame(data, columns=None)


def reformat_table(table):
    """
    Reformat the table for export. Set the next format:
    1 | Eng | engT | EngEx | 1 | Rus | RusEX
    2 | Eng | engT | EngEx | 2 | Rus | RusEX
    ...
    :param table: pd.DataFrame()
    :return: pd.DataFrame()
    """
    table = (table.reset_index().drop(columns=["index"]).
             reset_index().rename(columns={0: 1, 1: 2, 2: 3, 3: 5, 4: 6}))
    ind = table["index"].to_list()
    new_ind = [i + 1 for i in ind]
    table = table.drop(columns=["index"])
    table.insert(0, 0, new_ind, True)
    table.insert(4, 4, new_ind, True)
    return table


def prepare_table_to_export(table):
    """
    Prepare table for export to Google spreadsheet.
    Reformat pd.DataFrame() by reformat_table(table)
    Turn it into list of String (not list if lists)
    Create range of cells for spreadsheet (String).
    :param table: pd.DataFrame
    :return: list, String
    """
    table = reformat_table(table)
    table_l = table.values.tolist()
    return ([item for sublist in table_l for item in sublist],
            "A1:G{}".format(len(table_l)))


def save_table(json_filename, user_email, new_table, new_table_range, new_table_name="new_table", role='owner'):
    """
    Save table to Google spreadsheets
    :param json_filename: Path to Google API credentials file .json
    :param user_email: An email referred to a google account with which the spreadsheets will be shared
    :param new_table: list of items in new table prepared by prepare_table_to_export(table)
    :param new_table_range: A cell range prepared by prepare_table_to_export(table)
    :param new_table_name: A name of new table (optional, default="new_table")
    :param role: user role (optional, default="owner". Also possible: "reader" and "writer")
    :return: object. link to a table
    """
    gs = connect_to_gspread(json_filename)
    w = gs.create(new_table_name)
    cell_list = w.sheet1.range(new_table_range)
    for item, cell in zip(new_table, cell_list):
        cell.value = item
    w.sheet1.update_cells(cell_list)
    w.share(user_email, perm_type='user', role=role)
    return w


if __name__ == '__main__':
    filename = 'google_api.json'
    table_name_ = "Словарные слова"
    user_email_ = "enolerobotti.py@gmail.com"

    from table_classifier import excel_parser

    filename_input = "d:\\English\\May2019\\2019_05_01_MyVocabulary.xlsx"
    table_gen = excel_parser(filename_input)
    df = next(table_gen)
    df = df.dropna().head(5)
    data_, t_range = prepare_table_to_export(df)
    save_table(filename, user_email_, data_, t_range, "new")
