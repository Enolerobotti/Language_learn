from math import isnan

import pandas as pd

from google_connector import reformat_table, load_table, save_table, prepare_table_to_export
from table_classifier import excel_parser, classify_table, get_sheet_names, clear_data_drop_int, \
    convert_empty_str_to_nan


def swap_columns(table):
    """
    The columns in an input table may be in different order.
    We swap columns in our order: Eng | EngT | EngEx | Rus | RusEx
    with machine learning classifier (see function classify_table(table) in table_classifier.py).
    :param table: pd.DataFrame()
    :return: pd.DataFrame()
    """
    recognized_columns = classify_table(table)
    numeral_columns = {v: i for i, v in enumerate(recognized_columns.values()) if not isnan(v)}
    # print(numeral_columns)
    return table[[k for k in numeral_columns.keys()]].rename(columns=numeral_columns)


class Table:
    """
    Represents a table:
    Table.table

    Methods:
    get_robot_email,
    update_google_notations,
    update_excel_notations,
    add_row,
    clear_table,
    google_import,
    google_export,
    excel_import,
    excel_export
    """

    def __init__(self, google_notations=None, excel_notations=None):
        """
        Initialization
        :param google_notations: dict with Google Api credentials
        :param excel_notations: dict with excel file paths
        """
        self.google_notations = google_notations
        self.excel_notations = excel_notations
        self.table = pd.DataFrame(columns=[0, 1, 2, 3, 4])
        self.web_address = None

    def get_robot_email(self):
        """
        Get a email from Google Api credentials .json file
        :return: String
        """
        file = open(self.google_notations["your_json_file"], "r")
        row = file.readline()
        while not ("client_email" in row):
            row = file.readline()
        email = row[row.find(': "') + 3: row.find(',') - 1]
        file.close()
        return email

    def update_google_notations(self, google_notations):
        """
        Update credentials
        :param google_notations: dict
        :return: Updated dict
        """
        self.google_notations = google_notations
        return google_notations

    def update_excel_notations(self, excel_notations):
        """
        Update file paths
        :param excel_notations: dict
        :return: Updated dict
        """
        self.excel_notations = excel_notations
        return excel_notations

    def add_row(self, row):
        """
        Add row to Table.table
        :param row: list or tuple, len(row) <= 5
        :return: pd.DataFrame: Table.table
        """
        self.table = pd.concat([self.table, pd.DataFrame(row).T], axis=0)
        return self.table

    def clear_table(self):
        """
        Delete all from Table.table
        :return: empty pd.DataFrame: Table.table
        """
        self.table = pd.DataFrame(columns=[0, 1, 2, 3, 4])
        return self.table

    def google_import(self):
        """
        Import table from google spreadsheet
        :return: pd.DataFrame() (local variable)

        note: to update Table.table, use command
        >> Table.table = Table.google_import()
        """
        table = load_table(self.google_notations['your_json_file'],
                           self.google_notations['table_name_for_import'])
        table = clear_data_drop_int(table)
        table = convert_empty_str_to_nan(table).dropna(how='all')  # clear empty rows in Google Spreadsheets
        return swap_columns(table).applymap(lambda x: x.replace('"', "''") if isinstance(x, str) else x)

    def google_export(self, role='owner'):
        """
        Export Table.table to google spreadsheet
        :param role: user role (optional, default="owner". Also possible: "reader" and "writer")
        :return: number of rows which are written
        """
        data, table_range = prepare_table_to_export(self.table)
        w = save_table(self.google_notations["your_json_file"],
                       self.google_notations["user_email"],
                       new_table=data,
                       new_table_range=table_range,
                       new_table_name=self.google_notations["table_name_for_export"],
                       role=role)
        self.web_address = "https://docs.google.com/spreadsheets/d/{}".format(w.id)
        return len(self.table)

    def excel_import(self):
        """
        Import table from excel file
        :return: pd.DataFrame() (local variable)

        note: to update Table.table, use command
        >> Table.table = Table.excel_import()
        """
        filename = self.excel_notations["file_path_for_import"]
        table_gen = excel_parser(filename)
        sheet_names = get_sheet_names(filename)
        table = pd.DataFrame(columns=[0, 1, 2, 3, 4])
        not_recognized = []
        errors = []
        for sheet, sheet_name in zip(table_gen, sheet_names):
            try:
                sheet = swap_columns(sheet)
                table = pd.concat([table, sheet], axis=0, ignore_index=True)
            except IndexError as er:
                not_recognized.append(sheet_name)
                errors.append(er)
        return table.applymap(lambda x: x.replace('"', "''") if isinstance(x, str) else x), not_recognized, errors

    def excel_export(self):
        """
        Export Table.table to excel file
        :return: number of rows which are written
        """
        table = reformat_table(self.table)
        table.to_excel(self.excel_notations['file_path_for_export'], index=False, header=False)
        return len(self.table)


if __name__ == '__main__':
    google_default_notations = {'your_json_file': 'google_api.json',
                                'user_email': 'enolerobotti.py@gmail.com',
                                'table_name_for_import': 'Словарные слова',
                                'table_name_for_export': 'New_table'}

    excel_default_notations = {'file_path_for_import': 'test_table.xlsx',
                               'file_path_for_export': 'New_table.xlsx'}
    # excel_default_notations['file_path_for_import'] = "test_table.xlsx"
    # excel_default_notations['file_path_for_import'] = "d:\\English\\April2019\\2019_04_08_MyVocabulary.xlsx"

    # google_default_notations["table_name_for_import"] = "new1"
    t = Table(google_default_notations, excel_default_notations)
    # email_ = t.get_robot_email()
    # print(email_)
    # t.table, skipped, errs = t.excel_import()
    # print(t.table)
    # t.excel_export()
    # t.table = t.google_import()
    # t.google_export()
    # tab = t.google_import().head(5)
    # tab = tab.applymap(lambda x: x.replace('"', "''"))
    # print(t1)
    # print(tab)
