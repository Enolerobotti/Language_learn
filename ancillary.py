def desired_word(s):
    i = 0
    s = s.replace('(', '').replace(')', '')
    new_s = ''
    while i < len(s) and s[i] not in '-\n,.;:/\t_[{]}*+^#$!?':
        new_s = new_s + s[i]
        i += 1
    return new_s.strip(' ')


def add_newlines(text, length_of_instance):
    new_text = ""
    row = ""
    condition = True
    try:
        words = text.split()
    except AttributeError:
        # None type is observed
        words = []
    words_iter = iter(words)
    while condition:
        try:
            row = row + next(words_iter)
            if len(row) >= length_of_instance:
                new_text = new_text + row + "\n"
                row = ""
            else:
                row = row + " "
        except StopIteration:
            condition = False
            new_text = new_text + row

    return new_text.rstrip(" ").rstrip("\n")


def add_newlines_to_row(row, length_of_instance):
    return tuple([add_newlines(text, length_of_instance) for text in row])


def clear_text_data(text):
    if text == '':
        text = "1"
    elif text[0] == "0":
        i = 0
        try:
            while text[i] == "0":
                i += 1
            text = text[i:]
        except IndexError:
            text = '1'
    return text


def validate_host(key):
    valid = key.isdigit() | (key in "localhost.")
    return valid


if __name__ == '__main__':
    text_ = ("There are plenty of things to note in this example. "
             "First, no position is specified for the label widgets. "
             "In this case, the column defaults to 0, and the row to "
             "the first unused row in the grid. ")
    new_text_ = add_newlines(text=text_, length_of_instance=20)
    print(text_ + "\n")
    print(new_text_)
