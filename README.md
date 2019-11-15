# Vocabulary
App that helps me to learn English words

Language Learning 1.0
Authors Artem Pavlovskii, Kate Dedova
Developed by Artem Pavlovskii
Tested by Kate Dedova

email: 'enolerobotti.py@gmail.com' (Artem)

Quick start:
1. You can create new user if you have access to the MySQL server with privileges to create users and databases. To create a new user's credentials use new_user.py. After the creation, move config.pickle from the new_user folder to your work folder. Replace the original file if needed. Remove admin.pickle if you do not need it anymore.
2. Start program language_training.pyw. User's credentials will be loaded automatically on the tab 'Parameters'. Specify your parameters for export and import from (to) Google sheets and MS Excel.
3. You must obtain your own json file in Google cloud platform. You need a 'service account' type of such file. See the link https://medium.com/@vince.shields913/reading-google-sheets-into-a-pandas-dataframe-with-gspread-and-oauth2-375b932be7bf for details.
4. After that you may import words into database by the 'Import' button. You table must contain 5 columns with data and any amount of columns with numbers and empty columns. These 5 columns od the data may be in an arbitrary order but they must contain: the English word, transcription, English example, Russian word, and Russian example.
5. It is time to start the test. Select preferable type of test and enjoy!
6. After the test you can upload the words into the google or excel spreadsheets.

Have a fun:)
