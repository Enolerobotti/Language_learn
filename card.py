import tkinter as tk


class CardWindowWidgets(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Card")
        self.master.resizable(0, 0)
        self.pack()

        self.step = tk.StringVar()
        self.current_step = 1

        self.side_frame = tk.Frame(self)
        self.side_frame.pack()

        self.step_label = tk.Label(self, textvariable=self.step)
        self.step_label.pack()

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side='right')
        self.flip_button = tk.Button(self.button_frame, text="Flip", width=15)
        self.flip_button.pack(side='left', padx=5, pady=5)
        self.next_button = tk.Button(self.button_frame, text="Next", width=15)
        self.next_button.pack(side='left', padx=5, pady=5)
        self.mark_button = tk.Button(self.button_frame, width=15)
        self.mark_button.config(text="Mark as learned")
        self.mark_button.pack(side='left', padx=5, pady=5)
        self.hide_button = tk.Button(self.button_frame, text="Not show again", width=15)
        self.hide_button.pack(side='left', padx=5, pady=5)
        self.cancel_button = tk.Button(self.button_frame, text="Cancel", width=15)
        self.cancel_button.pack(side='left', padx=5, pady=5)

    def set_label_value(self, current_step, number_of_steps):
        self.step.set("step: {}/{}".format(current_step, number_of_steps))

    def increment_step(self):
        self.current_step += 1
        return self.current_step

    def reset_step(self):
        self.current_step = 1
        return self.current_step


class Side(tk.Frame):
    def __init__(self, master=None, number_of_labels=0, additional_instances=False, color_bg="lavender"):
        super().__init__(master)
        self.master = master
        self.is_enabled = True
        self.additional_instances = additional_instances
        self.color_bg = color_bg
        self.configure(height=250, width=430, bg=self.color_bg)
        self.grid_propagate(0)
        self.grid()
        self.val_label = []

        for i in range(number_of_labels):
            self.val_label.append(tk.StringVar())
            tk.Label(self, textvariable=self.val_label[i], bg=self.color_bg,
                     width=60, pady=15, justify=tk.LEFT,
                     anchor=tk.W).grid(sticky=tk.NS)

        if self.additional_instances:
            self.e = tk.Entry(self, width=30)
            self.e.grid(pady=15)
            self.b = tk.Button(self, text="Submit")
            self.b.grid()
            self.additional_val_label = tk.StringVar()
            self.add_lab = tk.Label(self, textvariable=self.additional_val_label, bg=self.color_bg, width=60,
                                    pady=15)
            self.add_lab.grid()
            self.additional_val_label.set("Try to enter the word in the text field above.")

    def disable(self):
        self.grid_remove()
        self.is_enabled = False

    def enable(self):
        self.grid()
        self.is_enabled = True

    def does_it_enabled(self):
        return self.is_enabled


if __name__ == '__main__':
    root = tk.Tk()
    card_window = CardWindowWidgets(master=root)
    card_window.pack()
    card_window.mainloop()
