import tkinter as tk


def callback(char_in_entry):
    """
    Restrict any chars except digits in a tkinter.Entry()
    Thanks for the idea:
    https://stackoverflow.com/questions/8959815/restricting-the-value-in-tkinter-entry-widget

    :param char_in_entry: a symbol which one try to enter into the entry.
    :return: True if digit and False otherwise.
    """
    if str.isdigit(char_in_entry) or char_in_entry == "":
        return True
    else:
        return False


class MainWindowWidgets(tk.Frame):
    def __init__(self, master=None):
        """
        The main window constructor

        :param master: root = tkinter.Tk()
        """
        super().__init__(master)
        self.master = master
        self.pack()
        self.master.title("Language training")
        self.master.resizable(0, 0)

        self.export_frame = tk.LabelFrame(self, text="Vocabulary")
        self.radio_frame = tk.Frame(self)
        self.specify_frame = tk.LabelFrame(self, text="Specify the maximum number of questions")
        self.custom_frame = tk.LabelFrame(self, text="Specify the custom time period in days:",
                                          fg="snow3")
        self.button_frame = tk.Frame(self)
        self.export_frame.grid(row=0, column=0, columnspan=3, padx=5, sticky=tk.EW)
        self.radio_frame.grid(row=2, column=0, columnspan=3, padx=5, sticky=tk.EW)
        self.specify_frame.grid(row=3, column=0, columnspan=3, padx=5, sticky=tk.EW)
        self.custom_frame.grid(row=4, column=0, columnspan=3, padx=5, sticky=tk.EW)
        self.button_frame.grid(row=5, column=0, columnspan=3, padx=5, sticky=tk.E)

        self.import_button = tk.Button(self.export_frame, text='Import words', width=10)
        self.export_button = tk.Button(self.export_frame, text='Export words', width=10)
        self.preferences_button = tk.Button(self.export_frame, text='Parameters', width=10)

        self.import_button.grid(row=0, column=0, padx=5, pady=5, sticky=tk.EW)
        self.export_button.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        self.preferences_button.grid(row=0, column=2, padx=5, pady=5, sticky=tk.EW)

        self.wn_f = StatLabels(self, text='Well known')
        self.new_f = StatLabels(self, text='New')
        self.all_f = StatLabels(self, text='All')

        self.wn_f.grid(row=1, column=0, padx=5, sticky=tk.EW)
        self.new_f.grid(row=1, column=1, sticky=tk.EW)
        self.all_f.grid(row=1, column=2, padx=5, sticky=tk.EW)

        notations_rb1 = [
            ("Words", 0),
            ("Phrases", 1)
        ]

        notations_rb2 = [
            ("Learn new", 0),
            ("Repeat learned in the past month", 1),
            ("Repeat learned in a custom period", 2),
            ("Learn all", 3)
        ]

        notations_rb3 = [
            ("Eng => Rus", 0),
            ("Rus => Eng", 1)
        ]

        val_cmd = self.register(callback)  # callback is the function!
        self.specify_entry = tk.Entry(self.specify_frame, width=30, validate='all', validatecommand=(val_cmd, '%P'))
        self.specify_entry.pack(anchor=tk.W, padx=5)
        self.specify_entry.insert(0, "10")

        self.custom_entry = tk.Entry(self.custom_frame, width=30, validate='all',
                                     validatecommand=(val_cmd, '%P'))
        self.custom_entry.pack(anchor=tk.W, padx=5)
        self.custom_entry.insert(0, "7")
        self.custom_entry.config(state="disabled")

        self.rb1 = MyRadio(self.radio_frame, notations_rb1, text="Do you prefer to learn words or phrases?")
        self.rb1.pack(fill=tk.X)

        self.rb2 = MyRadio(self.radio_frame, notations_rb2, text="Choose the following training mode",
                           radio_callback=self.radio_callback)
        self.rb2.pack(fill=tk.X)

        self.rb3 = MyRadio(self.radio_frame, notations_rb3, ch_box=True, text="Select language")
        self.rb3.pack(fill=tk.X)

        self.start_button = tk.Button(self.button_frame, text="Start", width=10)
        self.help_button = tk.Button(self.button_frame, text="Help", width=10)
        self.exit_button = tk.Button(self.button_frame, text="Exit", width=10)
        self.start_button.pack(side='left', pady=5)
        self.help_button.pack(side='left', padx=5, pady=5)
        self.exit_button.pack(side='left', pady=5)

    def radio_callback(self, var):
        if var == 2:
            self.custom_entry.config(state="normal")
            self.custom_frame.config(fg='black')
        else:
            self.custom_entry.config(state="disabled")
            self.custom_frame.config(fg='snow3')
        return var


class StatLabels(tk.LabelFrame):
    def __init__(self, master=None, text=None, number=0):
        super().__init__(master)
        self.master = master
        self.config(text=text)
        self.number = number
        self.v = tk.StringVar()
        self.label = tk.Label(self, textvariable=self.v, width=10)
        self.label.pack()
#        self.refresh_label()

    def refresh_label(self):
        """
        set the number value for the label
        :return: None
        """
        self.v.set(self.number)


class MyRadio(tk.LabelFrame):
    def __init__(self, master=None, notations=None, ch_box=False,
                 text=None, radio_callback=lambda x: x):
        """
        Create the sequence of Radio buttons specified by notations.
        In addition the __init__ creates a checkbox when parameter ch_box is True
        Has a get_radio_value() method to obtain the value of the Radio button variable outside the class.
        This method assign the Radio button variable to the MyRadio.value variable.

        For instance:
        >> button = tkinter.Button(self)
        >> rb = MyRadio(self, notations=my_notations)
        >> button["command"] = lambda: print(rb.value)
        Out: 1

        :param master: e.g., tkinter.Frame()
        :param notations: should be a list of tuples like
        [("some text", 0),
        ("some text", 1),
        ("some text", 2)]
        :param ch_box: Create a checkbox or not (default False)
        """
        super().__init__(master)
        self.master = master
        self.notations = notations
        self.config(text=text)
        self.value = 0
        self.ch_box = ch_box
        self.radio_callback = radio_callback

        self.v = tk.IntVar()
        self.v.set(0)

        self.ch = MyCheckBox(self)
        for notations, val in self.notations:
            tk.Radiobutton(self,
                           text=notations,
                           variable=self.v,
                           command=self.get_radio_value,
                           width=29,
                           anchor=tk.W,
                           value=val).pack(fill=tk.X)

        self.get_radio_value()

        if self.ch_box:
            self.ch.pack()

    def get_radio_value(self):
        """
        Assign int value of Radio button variable to MyRadio.value variable
        Make checkbox either active or inactive depending on the radio variable value
        :return: None
        """
        self.value = self.v.get()
        if self.ch_box and self.value == 0:
            self.ch.make_ch_inactive()
        elif self.ch_box and self.value == 1:
            self.ch.make_ch_active()

        self.radio_callback(self.v.get())


class MyCheckBox(tk.Frame):
    def __init__(self, master=None):
        """
        Create a checkbox.
        Has a get_ch_value() method to obtain values
        Has methods to make the checkbox either inactive or active

        :param master: tkinter.Frame
        """
        super().__init__(master)
        self.master = master
        self.ch_var = tk.IntVar()
        self.ch_var.set(1)
        self.temp_ch = 0
        self.ch_button = tk.Checkbutton(self,
                                        text="Check spelling",
                                        variable=self.ch_var,
                                        command=self.get_ch_value,
                                        width=29,
                                        anchor=tk.W)
        self.ch_button.pack()

    def get_ch_value(self):
        """
        Get a value of a checkbox variable
        :return: False or True
        """
        return self.ch_var.get() == 1

    def make_ch_inactive(self):
        """
        Make the checkbox inactive.
        Store an old value of a checkbox variable in self.temp_ch
        Assign the checkbox variable to null
        :return: None
        """
        self.temp_ch = self.ch_var.get()
        self.ch_var.set(0)
        self.ch_button.config(state='disabled')

    def make_ch_active(self):
        """
        Remember the old value of checkbox variable from self.temp_ch
        Make the checkbox active.
        :return: None
        """
        self.ch_var.set(self.temp_ch)
        self.ch_button.config(state='normal')
