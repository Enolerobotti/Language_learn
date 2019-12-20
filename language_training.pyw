import tkinter as tk

from tkinter import messagebox

import OpenSSL
from mysql.connector.errors import ProgrammingError, DatabaseError, InterfaceError
from gspread.exceptions import SpreadsheetNotFound, APIError

from ancillary import clear_text_data, add_newlines_to_row, desired_word
from card import CardWindowWidgets, Side
from configs import ConfigWidgets, ExportImport
from help_msg import get_help
from mainwindow import MainWindowWidgets
from my_sql_connector import count_wellknown, count_new, random_rows, learn_new, query_database, \
    from_within_last_n_days, learn_all, is_marked, mark_as_unlearned, mark_as_learned, create_database, create_table, \
    modify_database, hide_word_forever, insert_rows, delete_doubles
from table import Table


class MainDriver:
    def __init__(self):
        self.card_open = False
        self.config_open = False
        self.rows = None
        self.current_row = None
        self.ok = True
        self.stat_correct = 0
        self.stat_wrong = 0
        self.submit_flag = False

        self.root = tk.Tk()
        self.root.protocol("WM_DELETE_WINDOW", self.close_windows)
        self.main_window = MainWindowWidgets(master=self.root)
        self.root.withdraw()

        self.card = tk.Toplevel()
        self.card.protocol("WM_DELETE_WINDOW", self.cancel_test)
        self.card_window = CardWindowWidgets(master=self.card)
        self.side_A = Side(self.card_window.side_frame, 2, True, color_bg="green yellow")
        self.side_B = Side(self.card_window.side_frame, 4, color_bg="gold")
        self.side_B.disable()
        self.card.withdraw()

        self.conf = tk.Toplevel()
        self.conf.protocol("WM_DELETE_WINDOW", self.cancel_conf)
        self.conf_window = ConfigWidgets(master=self.conf)
        try:
            self.apply_conf()
        except KeyError:
            messagebox.showerror("Error", "Create a new user by new_user.py!")
            self.root.destroy()

        try:
            self.update_stat_labels()
            self.conf.withdraw()
            self.root.deiconify()
        except ProgrammingError:
            self.ok = False
            self.conf_window.cancel_button.config(state='disabled')
            self.root.withdraw()
        except InterfaceError:
            self.ok = False
            self.conf_window.cancel_button.config(state='disabled')
            self.root.withdraw()
        except DatabaseError:
            self.ok = False
            self.conf_window.cancel_button.config(state='disabled')
            self.root.withdraw()

        self.ei = tk.Toplevel()
        self.ei.protocol("WM_DELETE_WINDOW", self.cancel_dialog)
        self.ei_dialog = ExportImport(master=self.ei)
        self.ei.withdraw()

        self.update_side_a_label()

        self.main_window.import_button["command"] = self.import_words
        self.main_window.export_button["command"] = self.export_words
        self.main_window.preferences_button["command"] = self.open_config

        self.main_window.start_button["command"] = self.open_cards
        self.main_window.help_button["command"] = self.open_help
        self.main_window.exit_button["command"] = self.close_windows

        self.card_window.flip_button["command"] = self.flip
        self.card_window.next_button["command"] = self.next_card
        self.card_window.mark_button["command"] = self.mark
        self.card_window.cancel_button["command"] = self.cancel_test
        self.card_window.hide_button["command"] = self.hide_forever

        self.side_A.b["command"] = self.submit

        self.conf_window.cancel_button["command"] = self.cancel_conf
        self.conf_window.apply_button["command"] = self.apply_button_pressed
        self.conf_window.ok_button["command"] = self.ok_conf

        self.ei_dialog.cancel_button["command"] = self.cancel_dialog
        self.ei_dialog.ok_button["command"] = self.ok_dialog

        self.table = Table()

    # Main window top button's commands
    def import_words(self):

        self.ei_dialog.flag_export = False
        self.ei_dialog.set_title(title="Import table")
        self.table.clear_table()
        self.root.withdraw()
        self.ei.deiconify()

    def export_words(self):
        config = self.conf_window.my_sql_frame.notations
        self.ei_dialog.flag_export = True
        self.ei_dialog.set_title()
        rows = query_database(config, learn_new())
        self.table.clear_table()
        for row in rows:
            self.table.add_row(row)
        self.root.withdraw()
        self.ei.deiconify()

    def open_config(self):
        self.config_open = True
        self.conf.deiconify()
        self.root.withdraw()

    # Main window bottom button's commands
    def open_cards(self):
        self.stat_correct = 0
        self.stat_wrong = 0
        self.card_open = True
        self.table.clear_table()
        if not self.main_window.rb3.ch.get_ch_value():
            self.side_A.additional_instances = False
            self.side_A.e.grid_remove()
            self.side_A.b.grid_remove()
            self.side_A.add_lab.grid_remove()
        else:
            self.side_A.additional_instances = True
            self.side_A.e.grid()
            self.side_A.e.focus_set()
            self.side_A.e.bind("<Return>", self.submit_key)
            self.side_A.b.grid()
            self.side_A.add_lab.grid()

        text = self.main_window.specify_entry.get()
        text = clear_text_data(text)
        self.main_window.specify_entry.delete(0, tk.END)
        self.main_window.specify_entry.insert(0, text)

        # the section below for MySQL
        try:
            self.rows, rows_length = self.set_training_mode()
            self.current_row = next(self.rows)  # raise StopIteration
            self.fill_side_labels(self.current_row)
            self.card.deiconify()
            self.root.withdraw()
            if int(text) > rows_length:
                text = str(rows_length)
                self.main_window.specify_entry.delete(0, tk.END)
                self.main_window.specify_entry.insert(0, text)
        except StopIteration:
            messagebox.showerror("Empty set",
                                 "It seems you have no words in selected mode to learn!\n"
                                 "Please check your database or choose another mode.")
        # end section

        self.card_window.set_label_value(1, text)

    def open_help(self):
        message = get_help()
        self.root.withdraw()
        if messagebox.showinfo(title="About program", message=message):
            self.root.deiconify()

    def close_windows(self):
        if self.card_open:
            self.card.withdraw()
        else:
            self.root.withdraw()

        if messagebox.askokcancel("Exit program", "Do you want to exit the program?"):
            self.conf_window.config_loader.update_notations(self.conf_window.my_sql_frame.notations,
                                                            self.conf_window.google_frame.notations,
                                                            self.conf_window.excel_frame.notations)
            self.conf_window.config_loader.remove_file()
            self.conf_window.config_loader.create_file()
            self.root.destroy()
        else:
            if self.card_open:
                self.card.deiconify()
            else:
                self.root.deiconify()

    # card window button's commands
    def flip(self):
        if self.side_A.does_it_enabled():
            self.side_B.enable()
            self.side_A.disable()
        else:
            self.side_A.enable()
            self.side_B.disable()

    def next_card(self):
        if self.side_B.does_it_enabled():
            self.side_A.enable()
            self.side_B.disable()
        text = self.card_window.step_label.cget("text")
        current_step = self.card_window.increment_step()
        number_of_steps = int(text[text.find("/") + 1:])
        self.update_side_a_label()
        self.table.add_row(self.current_row)
        if current_step > number_of_steps:
            self.card.withdraw()
            if self.side_A.additional_instances:
                # cond = (messagebox.askyesno("Test completed", "Correct answers {}. Wrong answers {}\n"
                #                                              "Would you like to export the words?".
                #                            format(self.stat_correct, self.stat_wrong)))
                messagebox.showinfo("Test completed", "Test completed. Thank you!\n"
                                                      "Correct answers {}. Wrong answers {}\n".format(self.stat_correct,
                                                                                                      self.stat_wrong))
            else:
                # cond = messagebox.askyesno("Test completed", "Test completed\n"
                #                                             "Would you like to export the words?")
                messagebox.showinfo("Test completed", "Test completed. Thank you!")
            # if cond:
            #    self.ei_dialog.flag_export = True
            #    self.ei_dialog.set_title()
            #    self.ei.deiconify()
            # else:
            #    self.close_cards()
            self.close_cards()
        else:
            self.card_window.set_label_value(current_step, number_of_steps)
            self.current_row = next(self.rows)
            self.fill_side_labels(self.current_row)

    def mark(self):
        config = self.conf_window.my_sql_frame.notations
        row = self.current_row
        if is_marked(config, row):
            mark_as_unlearned(config, row)
            self.card_window.mark_button.config(text="Mark as learned")
        else:
            mark_as_learned(config, row)
            self.card_window.mark_button.config(text="Mark as unlearned")

    def hide_forever(self):
        self.card.withdraw()
        if messagebox.askyesno("Word will be deleted", "This action cannot be undone!!!\nAre you sure?"):
            config = self.conf_window.my_sql_frame.notations
            row = self.current_row
            hide_word_forever(config, row)
            self.next_card()
        self.card.deiconify()

    def cancel_test(self):
        self.card.withdraw()
        if messagebox.askokcancel("Cancel test", "Do you really want to cancel the test?"):
            self.close_cards()
        else:
            self.card.deiconify()

    def close_cards(self):
        self.card_open = False
        self.root.deiconify()
        self.card.withdraw()
        self.card_window.reset_step()
        self.update_stat_labels()
        self.update_side_a_label()
        if self.side_B.does_it_enabled():
            self.side_A.enable()
            self.side_B.disable()

    # SideA button's command
    def submit(self):
        self.submit_flag = True
        true_eng_word = desired_word(self.current_row[0].lower())
        user_eng_word = self.side_A.e.get().lower().strip(" ")
        if true_eng_word == user_eng_word:
            self.side_A.additional_val_label.set("Correct! Well done!")
            self.stat_correct += 1
        else:
            self.side_A.additional_val_label.set("Incorrect! Please try again.")
            self.stat_wrong += 1

    def submit_key(self, event):
        self.submit()
        # default_bg = self.side_A.b.cget('bg')
        # self.side_A.b.config(bg='gray90')
        # self.side_A.after(1000, lambda: self.side_A.b.config(bg=default_bg))
        self.side_A.b.config(relief='sunken')
        self.side_A.after(500, lambda: self.side_A.b.config(relief='raised'))

    def update_side_a_label(self):
        self.side_A.additional_val_label.set("Please enter the word in the text field above")
        self.side_A.e.delete(0, tk.END)

    # config window button's commands
    def cancel_conf(self):
        self.return_to_main_window()
        self.conf_window.my_sql_frame.discard_values()
        self.conf_window.google_frame.discard_values()
        self.conf_window.excel_frame.discard_values()
        self.conf_window.apply_button.config(state="disabled")

    def apply_conf(self):
        temp_config = self.conf_window.my_sql_frame.notations["database"]
        try:
            self.conf_window.my_sql_frame.save_values()
            self.conf_window.google_frame.save_values()
            self.conf_window.excel_frame.save_values()
            self.update_stat_labels()
            self.conf_window.cancel_button.config(state='normal')
            self.ok = True
        except ProgrammingError as error:
            self.db_error(error, temp_config)
            self.ok = False
        except DatabaseError as db_err:
            self.conf.withdraw()
            messagebox.showerror("Connection failed", db_err.msg)
            self.conf.deiconify()
            self.ok = False
        except InterfaceError as i_err:
            self.conf.withdraw()
            messagebox.showerror("Connection failed", i_err.msg)
            self.conf.deiconify()
            self.ok = False
        except TypeError as t_err:
            self.conf.withdraw()
            messagebox.showerror("Something wrong", t_err)
            self.conf.deiconify()
            self.ok = False

    def apply_button_pressed(self):
        self.apply_conf()
        if self.ok:
            self.conf_window.apply_button.config(state="disabled")

    def ok_conf(self):
        self.apply_conf()
        if self.ok:
            self.return_to_main_window()

    def db_error(self, error, temp_config):
        if error.errno == 1049:
            self.wrong_database(temp_config)
        elif error.errno == 1045 or error.errno == 1044:
            self.conf.withdraw()
            messagebox.showerror("Access denied", error.msg)
            self.conf.deiconify()
        else:
            print(error)

    def wrong_database(self, db_name):
        self.conf.withdraw()
        if messagebox.askyesno("Wrong database", "Database does not exist!\n"
                                                 "Would you like to create it?"):
            new_db_name = self.conf_window.my_sql_frame.entry_list[-1].get()
            try:
                create_database(self.conf_window.my_sql_frame.notations,
                                new_db_name)
                self.conf_window.my_sql_frame.notations["database"] = new_db_name
                error_flag = True
            except ProgrammingError:
                self.conf.deiconify()
                error_flag = False
            try:
                create_table(self.conf_window.my_sql_frame.notations, 'en_voc')
                self.apply_conf()
                messagebox.showinfo("Success", "Database '{}' and table 'en_voc' are created.".format(new_db_name))
                self.return_to_main_window()
            except ProgrammingError as p_err:
                messagebox.showerror("Access denied", "Unable to create a table.\n" + p_err.msg)
                if error_flag:
                    modify_database(self.conf_window.my_sql_frame.notations, 'DROP DATABASE {};'.format(new_db_name))
                self.abort_creation(db_name)
        else:
            self.abort_creation(db_name)

    def abort_creation(self, db_name):
        self.conf_window.my_sql_frame.entry_list[-1].delete(0, tk.END)
        self.conf_window.my_sql_frame.entry_list[-1].insert(0, db_name)
        self.conf_window.my_sql_frame.notations["database"] = db_name
        self.conf.deiconify()

    def return_to_main_window(self):
        self.config_open = False
        self.root.deiconify()
        self.conf.withdraw()

    # methods for database query
    def update_stat_labels(self):
        config = self.conf_window.my_sql_frame.notations

        self.main_window.wn_f.number = count_wellknown(config)
        self.main_window.wn_f.refresh_label()

        self.main_window.new_f.number = count_new(config)
        self.main_window.new_f.refresh_label()

        self.main_window.all_f.number = self.main_window.wn_f.number + self.main_window.new_f.number
        self.main_window.all_f.refresh_label()

    def set_training_mode(self):
        """
        Set the training mode which is specified in the second radio button frame
        :return: Generator with MySQL queries and its length
        """
        config = self.conf_window.my_sql_frame.notations
        limit = int(clear_text_data(self.main_window.specify_entry.get()))
        try:
            days = int(self.main_window.custom_entry.get())
        except ValueError:
            days = 0
            self.main_window.custom_entry.insert(0, '0')
        if self.main_window.rb2.v.get() == 0:
            rows = query_database(config, random_rows(learn_new(), limit))
            rows_length = sum(1 for _ in query_database(config, random_rows(learn_new(), limit)))
        elif self.main_window.rb2.v.get() == 1:
            rows = query_database(config, random_rows(from_within_last_n_days(30), limit))
            rows_length = sum(1 for _ in query_database(config, random_rows(from_within_last_n_days(30), limit)))
        elif self.main_window.rb2.v.get() == 2:
            rows = query_database(config, random_rows(from_within_last_n_days(days), limit))
            rows_length = sum(1 for _ in query_database(config, random_rows(from_within_last_n_days(days), limit)))
        elif self.main_window.rb2.v.get() == 3:
            rows = query_database(config, random_rows(learn_all(), limit))
            rows_length = sum(1 for _ in query_database(config, random_rows(learn_all(), limit)))
        else:
            raise ValueError
        return rows, rows_length

    def fill_side_labels(self, in_row):
        row = add_newlines_to_row(in_row, 60)  # alter the int if the text is too wide
        if self.main_window.rb1.v.get() == 0 and self.main_window.rb3.v.get() == 0:
            # return 0  # Words, Eng->Rus
            self.side_A.val_label[0].set(row[0])
            self.side_A.val_label[1].set('')

            # "Translation"
            self.side_B.val_label[0].set(row[3])
            # "English word"
            self.side_B.val_label[1].set(row[0])
            # "Transcription"
            self.side_B.val_label[2].set(row[1])
            # "An example"
            self.side_B.val_label[3].set(row[2])

        elif self.main_window.rb1.v.get() == 1 and self.main_window.rb3.v.get() == 0:
            # return 1  # Phrases, Eng->Rus
            self.side_A.val_label[0].set(row[2])
            self.side_A.val_label[1].set('')

            # "Translation"
            self.side_B.val_label[0].set(row[4])
            #            self.side_B.val_label[2].set("English word")
            self.side_B.val_label[1].set(row[0])
            # "Transcription"
            self.side_B.val_label[2].set(row[1])
            # "Russian word"
            self.side_B.val_label[3].set(row[3])

        elif (self.main_window.rb1.v.get() == 0 and self.main_window.rb3.v.get() == 1
              and not self.main_window.rb3.ch.get_ch_value()):
            # return 2  # Words, Rus->Eng
            self.side_A.val_label[0].set(row[3])
            self.side_A.val_label[1].set('')

            # "Translation"
            self.side_B.val_label[0].set(row[0])
            # "Transcription"
            self.side_B.val_label[1].set(row[1])
            # "Russian word"
            self.side_B.val_label[2].set(row[3])
            # "An Example"
            self.side_B.val_label[3].set(row[2])

        elif (self.main_window.rb1.v.get() == 0 and self.main_window.rb3.v.get() == 1
              and self.main_window.rb3.ch.get_ch_value()):
            # return 3  # Words, Rus->Eng, spell checker enabled
            self.side_A.val_label[0].set(row[3])
            self.side_A.val_label[1].set('')

            # "Translation"
            self.side_B.val_label[0].set(row[0])
            # "Transcription"
            self.side_B.val_label[1].set(row[1])
            # "Russian word"
            self.side_B.val_label[2].set(row[3])
            # "An Example"
            self.side_B.val_label[3].set(row[2])

        elif (self.main_window.rb1.v.get() == 1 and self.main_window.rb3.v.get() == 1
              and not self.main_window.rb3.ch.get_ch_value()):
            # return 4  # Phrases, Rus->Eng
            self.side_A.val_label[0].set(row[4])
            self.side_A.val_label[1].set('')

            # "Translation"
            self.side_B.val_label[0].set(row[2])
            # "English word"
            self.side_B.val_label[1].set(row[0])
            # "Transcription"
            self.side_B.val_label[2].set(row[1])
            # "Russian word"
            self.side_B.val_label[3].set(row[3])

        elif (self.main_window.rb1.v.get() == 1 and self.main_window.rb3.v.get() == 1
              and self.main_window.rb3.ch.get_ch_value()):
            # return 5  # Phrases, Rus->Eng, spell checker enabled
            self.side_A.val_label[0].set(row[4])
            self.side_A.val_label[1].set(row[3])

            # "Translation"
            self.side_B.val_label[0].set(row[2])
            # "English word"
            self.side_B.val_label[1].set(row[0])
            # "Transcription"
            self.side_B.val_label[2].set(row[1])
            # "Russian word"
            self.side_B.val_label[3].set(row[3])

        else:
            raise ValueError

        if is_marked(self.conf_window.my_sql_frame.notations, in_row):
            self.card_window.mark_button.config(text="Mark as unlearned")
        else:
            self.card_window.mark_button.config(text="Mark as learned")

    # Export dialog buttons
    def cancel_dialog(self):
        self.ei.withdraw()
        self.close_cards()

    def ok_dialog(self):
        msg = 'Some error is occurred!'
        self.ei.withdraw()
        flag = True
        table = None
        if self.ei_dialog.rb.v.get() == 1 and self.ei_dialog.flag_export:
            try:
                self.table.update_google_notations(self.conf_window.google_frame.notations)
                num_of_words = self.table.google_export()
                msg = ("Congrats! {} rows have been written in "
                       " {} to account {}").format(num_of_words,
                                                   self.table.google_notations["table_name_for_export"],
                                                   self.table.google_notations["user_email"])
            except APIError as e:
                messagebox.showerror("APIError", e)
                flag = False
        elif self.ei_dialog.rb.v.get() == 2 and self.ei_dialog.flag_export:
            self.table.update_excel_notations(self.conf_window.excel_frame.notations)
            try:
                num_of_words = self.table.excel_export()
                msg = ("Congrats! {} rows have been written in "
                       " {}").format(num_of_words, self.table.excel_notations["file_path_for_export"])
            except PermissionError as err:
                flag = False
                if err.errno == 13:
                    messagebox.showerror("Permission denied", "Perhaps the file is already open.")
                else:
                    print(err)
        elif self.ei_dialog.rb.v.get() == 1 and not self.ei_dialog.flag_export:
            self.table.update_google_notations(self.conf_window.google_frame.notations)
            try:
                table = self.table.google_import()
                msg = ("Congrats! Items have been successfully "
                       "imported from {}".format(self.table.google_notations["table_name_for_import"]))
            except SpreadsheetNotFound:
                self.ei.withdraw()
                flag = False
                messagebox.showerror("Error", "Spreadsheet not found")
            except FileNotFoundError:
                self.ei.withdraw()
                flag = False
                messagebox.showerror("Error", "Your .json is not found!")
            except OpenSSL.crypto.Error:
                self.ei.withdraw()
                flag = False
                messagebox.showerror("Error", "The problem with your .json is occurred!")

        elif self.ei_dialog.rb.v.get() == 2 and not self.ei_dialog.flag_export:
            self.table.update_excel_notations(self.conf_window.excel_frame.notations)
            table, not_recognized, errors = self.table.excel_import()
            msg = ("Congrats! Items have been successfully "
                   "imported from {} with {} not recognized "
                   "sheets which are: {}.".format(self.table.excel_notations["file_path_for_import"],
                                                  len(not_recognized),
                                                  not_recognized))
        else:
            raise UserWarning("Something wrong!")

        if not self.ei_dialog.flag_export and table is not None:
            config = self.conf_window.my_sql_frame.notations
            try:
                insert_rows(config, table.values.tolist())
                delete_doubles(config)
            except ValueError:
                self.ei.withdraw()
                messagebox.showerror("Error", "The spreadsheet is empty!")
                flag = False

        if flag:
            messagebox.showinfo("Success!", msg)
        self.ei_dialog.rb.save_values()
        self.close_cards()

    # other
    def launch(self):
        self.main_window.mainloop()


if __name__ == '__main__':
    main_window = MainDriver()
    main_window.launch()
