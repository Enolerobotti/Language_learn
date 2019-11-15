import mysql.connector


def query_database(config, query, *parameter_tuple):
    """
    Generator for queries to a database in MySQL server
    :param config: dict
    configs required for mysql.connector
    For instance, {'user': 'my_user',
                  'password': 'my_pass',
                  'host': 'localhost',
                  'use_pure': False,
                  'database': 'english'}
    :param query: String
    A query e.g. "SELECT * FROM table"

    :param parameter_tuple: tuple (optional)
    Parameters which should replace %s in queries.
    Number of parameters should be equal to number of %s in queries

    :return:
    generator
    """
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute(query, parameter_tuple)
    for c in cursor:
        yield c
    cnx.commit()
    cursor.close()


def modify_database(config, query):
    """
    Function for queries to a database in MySQL server
    It allows do all possible queries like ALTER, UPDATE, CREATE, etc
    :param config:  dict
    see query_database(config, query) for details

    :param query: String
    a query like "ALTER...", "UPDATE...", "CREATE...", etc
    :return: True if done
    """
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit()
    cursor.close()
    return True


# The functions for creation database 'english' and table 'en_voc' (The names are not specified!!!)


def create_database(config, database_name):
    """
    Create a database in MySQL Server
    :param config:  dict
    see query_database(config, query) for details

    :param database_name: String
    a single word, e.g. 'english'
    :return: True if done
    """
    try:
        del config['database']
    except KeyError:
        pass
    db_creation_query = ("CREATE DATABASE IF NOT EXISTS {} "
                         "CHARACTER SET utf8 COLLATE utf8_general_ci;").format(database_name)
    return modify_database(config, db_creation_query)


def create_table(config, table_name):
    """
    Create a table in database
    :param config:  dict
    see query_database(config, query) for details

    :param table_name: String
    a single word, e.g. 'en_voc'
    :return: True if done
    """
    tab_creation_query = ("CREATE TABLE IF NOT EXISTS `{}` "
                          "(`id` INT(11) AUTO_INCREMENT, PRIMARY KEY (`id`), "
                          "`Eng` TEXT, "
                          "`engT` TEXT, "
                          "`EngEx` TEXT, "
                          "`Rus` TEXT, "
                          "`RusEx` TEXT, "
                          "`wellknown` TINYINT(1) NOT NULL DEFAULT 0, "
                          "`marked` DATE NOT NULL DEFAULT '1980-01-01', "
                          "`unmarked` DATE NOT NULL DEFAULT '1980-01-01', "
                          "`added` DATE NOT NULL,"
                          "`visible` TINYINT(1) NOT NULL DEFAULT 1);").format(table_name)
    return modify_database(config, tab_creation_query)


#  The functions for insert data:
def insert_rows(config, rows):
    """
    Insert one or more rows into a table
    :param config:
    see query_database(config, query) for details

    :param rows: a list or tuple of format
    ('Eng', 'engT', 'EngEx', 'Rus', 'RusEx', 'added')
    :return: True if done
    """
    values = ''
    for row in rows:
        eng, eng_t, eng_ex, rus, rus_ex = row
        values = values + '("{}", "{}", "{}", "{}", "{}", CURDATE()), '.format(eng, eng_t, eng_ex, rus, rus_ex)
    query = ("INSERT INTO en_voc(Eng, engT, EngEx, Rus, RusEx, added) "
             "VALUES ") + values
    query = query[:-2] + ";"
    return modify_database(config, query)


def delete_doubles(config):
    query = ("DELETE t1 FROM en_voc t1 "
             "INNER JOIN en_voc t2 "
             "WHERE "
             "t1.id < t2.id AND "
             "t1.Eng = t2.Eng;"
             )
    return modify_database(config, query)

# The functions for the second radio button field of main window


def learn_new():
    """
    Specify a query for new words
    :return: String
    MySQL query
    """
    return ("SELECT Eng, engT, EngEx, Rus, RusEx FROM en_voc "
            "WHERE wellknown = 0 AND visible = 1 "
            "AND Eng is NOT NULL "
            "AND EngT IS NOT NULL "
            "AND EngEx IS NOT NULL "
            "AND Rus IS NOT NULL "
            "AND RusEx IS NOT NULL;")


def from_within_last_n_days(n):
    """
    Specify a query for words which marked as learned within past n days
    :param n: int
    number of days

    :return: String
    MySQL query
    """
    return ("SELECT Eng, engT, EngEx, Rus, RusEx FROM en_voc "
            "WHERE wellknown = 1 AND visible = 1 AND DATE_SUB(CURDATE(), "
            "INTERVAL {} DAY) <= marked;").format(n)


def learn_all():
    """
    Specify a query for all words
    :return: String
    MySQL query
    """
    return ("SELECT Eng, engT, EngEx, Rus, RusEx FROM en_voc WHERE visible = 1 "
            "AND Eng is NOT NULL "
            "AND EngT IS NOT NULL "
            "AND EngEx IS NOT NULL "
            "AND Rus IS NOT NULL "
            "AND RusEx IS NOT NULL;")


def repeat_within_arbitrary_interval():
    """
    Obsoleted
    Required to pass a tuple (start_date, end_date) to query_database()
    as a *parameter_tuple. It is rather complicated
    :return: MySQL query
    """
    return ("SELECT Eng, engT, EngEx, Rus, RusEx FROM en_voc "
            "WHERE wellknown = 1 AND visible = 1 AND marked BETWEEN %s AND %s;")


def random_rows(query, limit):
    """
    Return random rows in table limited by a number.
    :param query: String
    specific MySQL query

    :param limit: int
    number of rows required

    :return: String
    MySQL query
    """
    return query.replace(";", " ") + "ORDER BY RAND() LIMIT {};".format(limit)


# Functions for StatLabel


def count_wellknown(config):
    """
    Count wellknown words in table
    :param config: dict
    see query_database(config, query) for details
    :return: int
    Number of wellknown words in table except NULL values.
    """
    query = ("SELECT COUNT(id) FROM en_voc WHERE wellknown = 1 "
             "AND visible = 1 "
             "AND Eng is NOT NULL "
             "AND EngT IS NOT NULL "
             "AND EngEx IS NOT NULL "
             "AND Rus IS NOT NULL "
             "AND RusEx IS NOT NULL;")
    return next(query_database(config, query))[0]


def count_new(config):
    """
    Count new words in table
    :param config: dict
    see query_database(config, query) for details
    :return: int
    Number of new words in table except NULL values.
    """
    query = ("SELECT COUNT(id) FROM en_voc WHERE wellknown = 0 "
             "AND visible = 1 "
             "AND Eng is NOT NULL "
             "AND EngT IS NOT NULL "
             "AND EngEx IS NOT NULL "
             "AND Rus IS NOT NULL "
             "AND RusEx IS NOT NULL;")
    return next(query_database(config, query))[0]


# Functions for mark and unmark words

def is_marked(config, row):
    """
    Check whether the word is marked
    :param config: dict
    see query_database(config, query) for details
    :param row: tuple
    (Eng, EngT, EngEx, Rus, RusEx)
    :return: True if word is marked as wellknown. False otherwise
    """
    query = ('SELECT wellknown FROM en_voc WHERE Eng = "{}" '
             'AND Rus = "{}" AND visible = 1;').format(row[0], row[3])
    return next(query_database(config, query))[0] == 1


def mark_as_learned(config, row):
    query = ('UPDATE en_voc SET wellknown = 1, marked = CURDATE() '
             'WHERE Eng = "{}" AND Rus = "{}" AND visible = 1;').format(row[0], row[3])
    return modify_database(config, query)


def mark_as_unlearned(config, row):
    query = ('UPDATE en_voc SET wellknown = 0, unmarked = CURDATE() '
             'WHERE Eng = "{}" AND Rus = "{}" AND visible = 1;').format(row[0], row[3])
    return modify_database(config, query)


def hide_word_forever(config, row):
    query = ('UPDATE en_voc SET visible = 0 '
             'WHERE Eng = "{}" AND Rus = "{}";').format(row[0], row[3])
    return modify_database(config, query)


def undo_hiding_forever_for_all(config):
    return modify_database(config, "UPDATE en_voc SET visible = 1;")


if __name__ == '__main__':
    tmp_config = {'user': 'admin',
                  'password': 'Zvezda12/',
                  'host': 'localhost',
                  'use_pure': False,
                  'database': 'english'}

    tmp_query = ("SELECT * FROM en_voc "
                 "WHERE Eng is NOT NULL "
                 "AND EngT IS NOT NULL "
                 "AND EngEx IS NOT NULL "
                 "AND Rus IS NOT NULL "
                 "AND RusEx IS NOT NULL;")

    query1 = ("SELECT Eng, engT, EngEx, Rus, RusEx FROM en_voc "
              "WHERE wellknown = 0 and added BETWEEN %s AND %s;")

    query2 = ("SELECT Eng, engT, EngEx, Rus, RusEx FROM en_voc "
              "LIMIT 5;")

    rows_gen = query_database(tmp_config, query2)
    rows_ = [a for a in rows_gen]
    create_database(tmp_config, 'test')
    tmp_config['database'] = 'test'
    modify_database(tmp_config, "DROP TABLE en_voc;")
    create_table(tmp_config, 'en_voc')

    print(insert_rows(tmp_config, rows_))
