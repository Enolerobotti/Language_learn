# We dropped digits and classified columns into three groups.
# Next we figure out how to distinct Eng from EngEx and Rus from RusEx.
# We use machine learning.
# We save the results of learning and use them in further code.
# We classify columns of the table
# We can relearn the program in order to enhance the accuracy of predictions. (But it is non needed)

import pandas as pd
import numpy as np
import pickle

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn import metrics


def get_sheet_names(filename):
    """
    Return names of sheet in MS Excel file specified in filename
    :param filename: path to the .xls or .xlsx file
    :return: list of Strings

    >>get_sheet_names("d:\\English\\April2019\\2019_04_09_MyVocabulary.xlsx")
    ['09.04.2019',
     '11.04.2019',
     '12.04.2019',
     '17.04.2019',
     '18.04.2019']
    """
    xls = pd.ExcelFile(filename)
    sheet_names = xls.sheet_names
    xls.close()
    return sheet_names


def clear_data_drop_int(table):
    """
    Drop numerical and empty columns in pd.DataFrame() specified by table
    Rename the remained columns with int from zero in accent order
    :param table: pandas.DataFrame()
    :return: pandas.DataFrame()
    """
    condition = True
    i = 0
    j = 0
    columns_to_drop = []
    columns_to_rename = {}
    while condition:
        try:
            dtype_ = table[i].get_dtype_counts().index
            if ('int64' in dtype_ or 'float64' in dtype_
                    or table[i].apply(lambda x: str(x).isdigit()).sum() >= len(table) // 2):
                columns_to_drop.append(i)
            else:
                columns_to_rename[i] = j
                j += 1
            i += 1
        except KeyError:
            condition = False
    return table.drop(columns=columns_to_drop).rename(columns=columns_to_rename)


def excel_parser(filename):
    """
    Generator to parse excel file specified by filename
    :param filename: path to the .xls or .xlsx file
    :return: pandas.DataFrame() cleared from numbers and empty columns. Max 5 columns.
    """
    for number, current_sheet_name in enumerate(get_sheet_names(filename)):
        table = clear_data_drop_int(pd.read_excel(io=filename, sheet_name=number, header=None, index=None))
        if not table.empty:
            yield table


def word_processing(word, alphabet):
    """
    Make a decision whether a word belongs to a specific alphabet
    :param word: String
    :param alphabet: String, e.g. 'abcdefghijklmnopqrstuvwxyz '
    :return: True if the word belongs to the alphabet and False otherwise
    """
    mask = [(i in alphabet) for i in list(word)]
    true = 0
    false = 0
    for val in mask:
        if val:
            true += 1
        else:
            false += 1
    return true > false


def is_english(word):
    """
    Chech whether a word is an english word
    :param word: String
    :return: True if the word belongs to the English alphabet
    """
    eng = 'abcdefghijklmnopqrstuvwxyz '
    return word_processing(str(word).lower(), eng)


def is_russian(word):
    """
    Chech whether a word is an russian word
    :param word: String
    :return: True if the word belongs to the Russian alphabet
    """
    rus = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя '
    return word_processing(str(word).lower(), rus)


def is_transcription(word):
    """
    not used, but one usage is commented below
    :param word:
    :return:
    """
    symbols = ("[]'ˌ:ʌæʃəɪɔʤŋ")
    return word_processing(str(word).lower(), symbols)


def first_classifier(table):
    """
    Split a table into three groups: eng, eng_t, and rus.
    Each group may contains only one or two elements.
    `eng` may contain an English word and (or) an example,
    `eng_t` may contain only an English transcription
    `rus` may contain a Russian word and (or) an example,
    :param table: pandas.DataFrame()
    :return: three lists with numbers (int) of column of the table corresponging the group
    """
    table = table.dropna()
    num_of_rows = len(table.index)
    condition = True
    i = 0
    eng = []
    eng_t = []
    rus = []
    while condition:
        try:
            if table[i].apply(lambda x: is_english(x)).sum() >= num_of_rows // 2:
                eng.append(i)
            elif table[i].apply(lambda x: is_russian(x)).sum() >= num_of_rows // 2:
                rus.append(i)
            else:
                # elif table[i].apply(lambda x: not (is_russian(x) or is_english(x))).sum() >= num_of_rows // 2:
                # elif table[i].apply(lambda x: is_transcription(x)).sum() >= num_of_rows // 3:
                eng_t.append(i)
            i += 1
        except KeyError:
            condition = False
    return eng, rus, eng_t


def make_dataset(table, columns, number_of_groups=2):
    """
    Create a dataset for machine learning

    :param table: pandas.DataFrame()
    :param columns: list of integers with numbers of table columns
    :param number_of_groups: int, default 2, number of different groups
    :return: lists of equal length which are a dataset and its target
    """
    out_set = []
    target = []
    for i in range(len(table)):
        for j in range(number_of_groups):
            out_set.append(table[columns[j]].iloc[i])
            target.append(j)
    return out_set, target


def prepare_learn_data(filename):
    """
    Prepare datasets for the program learning
    :param filename: path to MS Excel file .xls or .xlsx
    :return: English and Russian datasets and its target (the target fits the both datasets, because it is 0 or 1)
    """
    tables = excel_parser(filename)
    table = pd.DataFrame()
    for t in tables:
        table = table.append(t.dropna())
    eng, rus, eng_t = first_classifier(table)
    eng_set, target = make_dataset(table, eng)
    rus_set, target = make_dataset(table, rus)
    return eng_set, rus_set, target


def predictor(dataset, target, show_info=False, save_result=False, out_filename='finalized_model.sav'):
    """
    Learn a classifier with a dataset and a target,
    Show metrics, and
    Save the model if needed
    :param dataset: a list of String
    :param target: a list of String len(target) == len(dataset)
    :param show_info: bool (default False) Show metrics
    :param save_result: bool (default False) Save the model
    :param out_filename: String. A name of the file you wont to save the model
    :return: Pipeline object (classifier)
    """
    text_clf = Pipeline([
        ('vector', CountVectorizer()),
        ('tfidf', TfidfTransformer()),
        ('clf', SGDClassifier(alpha=1e-4)),
    ])
    n_samples = len(target)
    text_clf.fit(dataset[:n_samples // 2], target[:n_samples // 2])
    if show_info:
        expected = target[n_samples // 2:]
        predicted = text_clf.predict(dataset[n_samples // 2:])
        print("Classification report for classifier %s:\n%s\n"
              % (text_clf, metrics.classification_report(expected, predicted)))
        print("Confusion matrix:\n%s" % metrics.confusion_matrix(expected, predicted))
    if save_result:
        pickle.dump(text_clf, open(out_filename, 'wb'))
    return text_clf


def relearn_model(filename, show_info=False):
    """
    Relearn the program with new data specifyed in filename
    Save new model
    :param filename: path to MS Excel file .xls or .xlsx
    :param show_info: bool (default False) Show metrics
    :return: two classifiers
    """
    eng, rus, target = prepare_learn_data(filename)
    eng_file = 'finalized_model_eng.sav'
    rus_file = 'finalized_model_rus.sav'
    clf1 = predictor(dataset=eng, target=target, show_info=show_info, save_result=True, out_filename=eng_file)
    clf2 = predictor(dataset=rus, target=target, show_info=show_info, save_result=True, out_filename=rus_file)
    return clf1, clf2


def predict_single_entry(classifier, text=None):
    """
    Not used.
    Just for fun
    :param classifier: Pipeline object
    :param text: single String. default text is None.
    Nonetype of text causes infinite interactive cycle. Type `stop` if you bored:)
    :return: list with a predictions
    """
    while text is None:
        text_sample = input("Specify the word: ")
        print("The column label is {}".format(predict_single_entry(classifier, text_sample)))
        if text_sample.lower() == 'stop':
            text = text_sample
    return classifier.predict([text])


def predict_column(column, model_filename):
    """
    load the learning model from model_filename and predict each entry in a column of a table
    :param column: list. e.g. a column of a table
    :param model_filename: path to saved model .sav
    :return: list with predictions (0 or 1 for each element)
    """
    model = pickle.load(open(model_filename, 'rb'))
    return model.predict(column)


def classify_group(group, table, model_filename):
    """
    Decide whether an element of some group belongs to class 0 or 1
    :param group: list returned by the first_classifier()
    :param table: pd.DataFrame()
    :param model_filename: path to saved model .sav
    :return: dict with numbers of the table columns as the keys and predictions as the values
    """
    prediction = {}
    for column in group:
        prediction[column] = np.mean(predict_column(table[column].tolist(), model_filename))
    return prediction


def classify_table(table, eng_filename='finalized_model_eng.sav', rus_filename='finalized_model_rus.sav'):
    """
    The most important function in this file!
    Figure out where is what in the table.
    :param table: pd.DataFrame()
    :param eng_filename: path to saved model .sav for English predictions
    :param rus_filename: path to saved model .sav for Russian predictions
    :return: dict with keys 'Eng', 'engT', 'EngEx', 'Rus', 'RusEx' and numbers of the table columns as the values.
    If some of the categories are absent in the table, returns np.NaN as the dict value
    """
    table = table.dropna()
    eng, rus, eng_t = first_classifier(table)
    columns_signs = {'Eng': np.NaN,
                     'engT': np.NaN,
                     'EngEx': np.NaN,
                     'Rus': np.NaN,
                     'RusEx': np.NaN}
    eng_prediction = classify_group(eng, table, eng_filename)
    if len(eng_prediction) > 1:
        if eng_prediction[eng[0]] < eng_prediction[eng[1]]:
            columns_signs['Eng'] = eng[0]
            columns_signs['EngEx'] = eng[1]
        else:
            columns_signs['Eng'] = eng[1]
            columns_signs['EngEx'] = eng[0]
    elif len(eng_prediction) == 0:
        pass
    else:
        if eng_prediction[eng[0]] < 0.5:
            columns_signs['Eng'] = eng[0]
        else:
            columns_signs['EngEx'] = eng[0]

    rus_prediction = classify_group(rus, table, rus_filename)
    if len(rus_prediction) > 1:
        if rus_prediction[rus[0]] < rus_prediction[rus[1]]:
            columns_signs['Rus'] = rus[0]
            columns_signs['RusEx'] = rus[1]
        else:
            columns_signs['Rus'] = rus[1]
            columns_signs['RusEx'] = rus[0]
    elif len(rus_prediction) == 0:
        pass
    else:
        if rus_prediction[rus[0]] < 0.5:
            columns_signs['Rus'] = rus[0]
        else:
            columns_signs['RusEx'] = rus[0]
    if len(eng_t) > 1:
        raise IndexError("Two columns of english transcription are observed!")
    elif len(eng_t) == 0:
        pass
    else:
        columns_signs["engT"] = eng_t[0]
    return columns_signs


def prepare_learning_data_from_first_classifier(filename):
    """
    Not used
    :param filename:
    :return:
    """
    tables = excel_parser(filename)
    table = pd.DataFrame()
    for t in tables:
        table = table.append(t.dropna())
    eng, rus, eng_t = first_classifier(table)
    out_set = []
    target = []
    for i in range(len(table)):
        for j in range(2):
            out_set.append(table[eng[j]].iloc[i])
            target.append(1)
            out_set.append(table[rus[j]].iloc[i])
            target.append(3)
        out_set.append(table[eng_t[0]].iloc[i])
        target.append(2)
    return out_set, target


def print_table(table):
    """
    ancillary function. It is not important
    :param table:
    :return:
    """
    i = 0
    condition = True
    while condition:
        try:
            print(table[i].iloc[0])
            i += 1
        except KeyError:
            condition = False


if __name__ == '__main__':
    # filename_input = "d:\\English\\April2019\\2019_04_08_MyVocabulary.xlsx"
    filename_input_p = "d:\\English\\May2019\\2019_05_01_MyVocabulary.xlsx"
    filename_input = "test_table.xlsx"
    # filename_input = "d:\\English\\May2019\\2019_06_15_MyVocabulary.xlsx"

    tables_input = excel_parser(filename_input)
    table_ = next(tables_input)

    eng_filename_ = 'finalized_model_eng.sav'
    rus_filename_ = 'finalized_model_rus.sav'

    eng_, rus_, eng_t_ = first_classifier(table_)
    print(eng_t_)
    print(eng_)
    print(rus_)
    #print(classify_group(eng_, table_, eng_filename_))

    # print(table_[1].get_dtype_counts().index)
    # print_table(table_)
    # print(classify_table(table_))

    # out, targ = prepare_learning_data_from_first_classifier(filename_input_p)
    # model_filename = 'three_groups.sav'
    # clf = predictor(out, targ, show_info=True, save_result=True, out_filename=model_filename)
    # print(classify_group([0, 1, 2, 3, 4], table_.dropna(), model_filename))
