import os
from getpass import getpass

from mysql.connector.errors import ProgrammingError, DatabaseError, InterfaceError
from configs import Loader
from my_sql_connector import modify_database, create_database, create_table


def is_email(s):
    if "@" in s and "." in s:
        return True
    else:
        return False


def get_username(s):
    if is_email(s) and '+' in s:
        c_number = min(s.find('@'), s.find('.'), s.find('+'))
    elif is_email(s) and not ('+' in s):
        c_number = min(s.find('@'), s.find('.'))
    else:
        raise ValueError("{} is not an email".format(s))
    return s[:c_number]


def get_admin_config():
    loader = Loader(config_file='admin.pickle')
    return loader.mysql_notations


def create_new_user(username, password, host='localhost'):
    config = get_admin_config()
    database_name = username + "_db"
    create_database(config, database_name)
    config['database'] = database_name
    create_table(config, 'en_voc')
    modify_database(config, "CREATE USER '{}'@'{}' "
                            "IDENTIFIED BY '{}';".format(username, host, password))
    query = ("GRANT SELECT, INSERT, UPDATE, DELETE "
             "ON {}.* TO '{}'@'{}';").format(database_name, username, host)
    modify_database(config, query)
    config['user'] = username
    config['password'] = password
    config['host'] = host
    config['database'] = database_name
    return config


def new_account(conf_filename, email, password, host='localhost', google_table='New_table'):
    my_sql_config = create_new_user(username=get_username(email),
                                    password=password,
                                    host=host)
    google_config = {'your_json_file': 'google_api.json',
                     'user_email': email,
                     'table_name_for_import': google_table,
                     'table_name_for_export': 'New_table'}
    excel_config = {'file_path_for_import': 'test_table.xlsx',
                    'file_path_for_export': 'New_table.xlsx'}
    loader = Loader(mysql_notations=my_sql_config,
                    google_notations=google_config,
                    excel_notations=excel_config,
                    config_file=conf_filename)
    return loader


if __name__ == '__main__':
    question = input("Would you like to specify MySQL config with admin privileges (y/n)? ")
    if question == '':
        question == 'n'
    if (not os.path.exists('admin.pickle')) or question[0] == 'y':
        notations = {'user': input("User: "),
                     'password': getpass(prompt='Your password: ', stream=None),
                     'host': input("Host: "),
                     'use_pure': False,
                     'database': 'default'
                     }
        loader = Loader(mysql_notations=notations, config_file='admin.pickle')
        loader.remove_file()
        loader.create_file()
        print("File admin.pickle was created. Delete it later.")

    email_ = input("\nEnter user email: ")
    password_ = getpass(prompt='Set user password: ', stream=None)
    google_table_ = 'Словарные слова'
    config_filename = 'new_user/config.pickle'
    if password_ == getpass(prompt='Repeat user password: ', stream=None):
        if os.path.exists(config_filename):
            os.remove(config_filename)
        try:
            lo = new_account(config_filename, email_, password_, host='localhost', google_table=google_table_)
            print('\nNew account has been created.\n\nMove {} '
                  'to the work directory to apply new user credentials'.format(config_filename))
        except DatabaseError as db_err:
            print(db_err)
        except ProgrammingError as pr_err:
            print(pr_err)
        except InterfaceError as i_err:
            print(i_err)
    else:
        print("Passwords do not match")

    input("\n\nPress enter to exit...")
