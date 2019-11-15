import tkinter as tk
import os.path
import pickle
import base64


services = [("MySQL", 0),
            ("Google sheets", 1),
            ("MS Excel", 2)]

mysql_default_notations = {'user': 'user',
                           'password': 'pass',
                           'host': 'localhost',
                           'use_pure': False,
                           'database': 'user_db'}

google_default_notations = {'your_json_file': 'google_api.json',
                            'user_email': 'user@userdomain.com',
                            'table_name_for_import': 'New_table',
                            'table_name_for_export': 'New_table'}

excel_default_notations = {'file_path_for_import': 'New_table.xlsx',
                           'file_path_for_export': 'New_table.xlsx'}


def uppercase(s):
    """
    str -> str
    :param s: e.g. 'field'
    :return: 'Field'
    """
    return s[0].upper() + s[1:]


def zero_to_false(s):
    """
    str -> bool
    :param s: 0,    1,   or String
    :return: False, True or String without any transformations
    """
    if s.isdigit() and len(s) == 1:
        return int(s) != 0
    else:
        return s


def to_bytes(notations):
    return {base64.urlsafe_b64encode(key.encode()): base64.urlsafe_b64encode(str(value).encode())
            for key, value in notations.items()}


def undo_bytes(notations):
    return {base64.urlsafe_b64decode(key).decode(): base64.urlsafe_b64decode(value).decode()
            for key, value in notations.items()}


def decode_list(list_of_notations):
    return [undo_bytes(notations) for notations in list_of_notations]


class ConfigWidgets(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Parameters")
        self.master.resizable(0, 0)
        self.pack()
        self.config_loader = Loader()
        self.my_sql_frame = Unit(self, text=services[0][0], notations=self.config_loader.mysql_notations,
                                 hide_pass=True, entry_callback=self.widget_callback)
        self.google_frame = Unit(self, text=services[1][0], notations=self.config_loader.google_notations,
                                 entry_callback=self.widget_callback)
        self.excel_frame = Unit(self, text=services[2][0], notations=self.config_loader.excel_notations,
                                entry_callback=self.widget_callback)

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(anchor=tk.E)

        self.ok_button = tk.Button(self.button_frame, text="Ok", width=10)
        self.apply_button = tk.Button(self.button_frame, text="Apply", width=10)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", width=10)

        self.apply_button.config(state="disabled")

        self.ok_button.pack(side='right', pady=5)
        self.apply_button.pack(side='right', padx=5, pady=5)
        self.cancel_button.pack(side='right', pady=5)

        # validate = self.my_sql_frame.register(validate_host)
        # self.my_sql_frame.entry_list[2].config(validate="key", validatecommand=(validate, '%S'))

    def widget_callback(self, key=None):
        self.apply_button.config(state="normal")
        return key


class ExportImport(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.resizable(0, 0)
        self.flag_export = True
        self.set_title()
        self.pack()
        self.rb = RadioButtons(self, text="Select service")
        self.button_frame = tk.Frame(self)
        self.button_frame.pack(anchor=tk.E)

        self.ok_button = tk.Button(self.button_frame, text="Ok", width=10)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", width=10)
        self.ok_button.pack(side='right', pady=5, padx=5)
        self.cancel_button.pack(side='right', pady=5)

    def set_title(self, title="Export table"):
        self.master.title(title)


class Unit(tk.LabelFrame):
    def __init__(self, master=None, text=None, notations=None, hide_pass=False, entry_callback=None):
        super().__init__(master)
        self.master = master
        self.config(text=text)
        self.notations = notations
        self.entry_callback = entry_callback
        self.pack(fill="both", expand="yes")

        self.entry_list = []
        self.label_list = []
        i = 0
        for label_text, entry_text in self.notations.items():
            label_ = tk.Label(self, text=uppercase(label_text.replace("_", ' ')),
                              width=20, anchor=tk.W)
            e = tk.Entry(self, width=30)
            e.bind("<Key>", self.entry_callback)
            if hide_pass and i == 1:
                e.config(show='*')
            e.insert(0, entry_text)
            self.entry_list.append(e)
            self.label_list.append(label_)
            label_.grid(row=i, column=0)
            e.grid(row=i, column=1)
            i += 1

    def get_values(self):
        new_dict = {}
        for e, l in zip(self.entry_list, self.label_list):
            new_dict[l.cget("text").lower().replace(" ", "_")] = zero_to_false(e.get())
        return new_dict

    def save_values(self):
        for key, value in self.get_values().items():
            self.notations[key] = str(value)

    def discard_values(self):
        for value, e in zip(self.notations.values(), self.entry_list):
            if value:
                e.delete(0, 'end')
                e.insert(0, value)


class RadioButtons(tk.LabelFrame):
    def __init__(self, master=None, text=None, radio_callback=None):
        super().__init__(master)
        self.master = master
        self.config(text=text)

        self.pack(fill="both", expand="yes")

        self.v = tk.IntVar()
        self.state = 1
        self.v.set(self.state)
        for text, val in services[1:]:
            tk.Radiobutton(self,
                           text=text,
                           variable=self.v,
                           command=radio_callback,
                           width=20,
                           anchor=tk.W,
                           value=val).pack(anchor=tk.W)

    def save_values(self):
        self.state = self.v.get()

    def discard_values(self):
        self.v.set(self.state)


class Loader:
    def __init__(self, mysql_notations=None, google_notations=None, excel_notations=None, config_file='config.pickle'):
        if excel_notations is None:
            excel_notations = {}
        if google_notations is None:
            google_notations = {}
        if mysql_notations is None:
            mysql_notations = {}
        self.mysql_notations = mysql_notations
        self.google_notations = google_notations
        self.excel_notations = excel_notations
        self.config_file = config_file
        self.create_file()

    def create_file(self):
        configuration = None
        if os.path.exists(self.config_file):
            with open(self.config_file, 'rb') as conf:
                configuration = pickle.load(conf)
                self.mysql_notations, self.google_notations, self.excel_notations = decode_list(configuration)
        if not configuration:
            configuration = [to_bytes(self.mysql_notations),
                             to_bytes(self.google_notations),
                             to_bytes(self.excel_notations)]
            with open(self.config_file, 'wb') as conf:
                pickle.dump(configuration, conf)

    def remove_file(self):
        if os.path.exists(self.config_file):
            os.remove(self.config_file)

    def update_notations(self, mysql_notations=None, google_notations=None, excel_notations=None, config_file=None):
        if mysql_notations is not None:
            self.mysql_notations = mysql_notations
        if google_notations is not None:
            self.google_notations = google_notations
        if excel_notations is not None:
            self.excel_notations = excel_notations
        if config_file is not None:
            self.config_file = config_file


if __name__ == '__main__':
    loader = Loader(mysql_notations=mysql_default_notations,
                    google_notations={},
                    excel_notations={},
                    config_file='admin.pickle')
    print(loader.mysql_notations)
    print(loader.google_notations)
    print(loader.excel_notations)