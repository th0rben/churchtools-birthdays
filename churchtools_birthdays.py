import requests
import time
from config import domain, mail, password, password_sender, sender, recipients, server, port, birthdays_filename, \
    all_persons_filename
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import openpyxl
import numpy as np


def login(session):
    url = domain + '?q=login'
    data = {'email': mail,
            'password': password,
            'directtool': 'yes'}
    return session.post(url, data).content


def logout(session):
    url = domain + '?q=logout';
    data = {'func': 'logout',
            'directtool': 'yes'}
    return session.post(url, data).content


# ensures that Umlaute are getting displayed correctly
def umlaute_correcter(string):
    return string.replace("\\u00f6", "ö").replace("\\u00e4", "ä").replace("\\u00df", "ß").replace("\\u00fc", "ü")


def save_birthdays(data_array):
    date = time.strftime("%Y-%m-%d")
    birthdays_filename_xlsx = date + "_" + birthdays_filename + ".xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    row = ['Vorname', 'Nachname', 'Gebubrtstag', 'Alter']
    ws.append(row)
    for i in range(0, len(data_array)):
        raw_row = data_array[i]
        row = [raw_row['vorname'], \
               raw_row['name'],
               raw_row['geburtsdatum_compact'],
               raw_row['age']]
        ws.append(row)

    wb.save(birthdays_filename_xlsx)
    return birthdays_filename_xlsx


def save_all_persons(data_array):
    date = time.strftime("%Y-%m-%d")
    all_persons_filename_xlsx = date + "_" + all_persons_filename + ".xlsx"

    wb = openpyxl.Workbook()
    ws = wb.active

    row = ['Vorname', 'Nachname', 'Email', 'Handy', 'Festnetz', 'Strasse', 'PLZ', 'Ort']
    ws.append(row)
    for i in range(0, len(data_array)):
        raw_row = data_array[i]
        row = [raw_row['vorname'], \
               raw_row['name'], \
               raw_row['em'], \
               raw_row['telefonhandy'], \
               raw_row['telefonprivat'], \
               raw_row['strasse'], \
               raw_row['plz'], \
               raw_row['ort']]
        ws.append(row)

    wb.save(all_persons_filename_xlsx)
    return all_persons_filename_xlsx


# return: json array of persons and their birthdays
def get_birthdays(from_int, to_int):
    with requests.Session() as s:
        login(s)
        url = domain + '?q=churchdb/ajax'
        data = {'func': 'getBirthdayList',
                "from": str(from_int),
                "to": str(to_int)}
        response = s.post(url, data)
        logout(s)
        df = pd.read_json(response.text)
        data_array = np.array(df['data'], dtype=pd.Series)
        return data_array


def get_all_persons():
    with requests.Session() as s:
        login(s)
        url = domain + '?q=churchdb/ajax'
        data = {'func': 'getAllPersonData'}
        response = s.post(url, data)
        logout(s)
        df = pd.read_json(response.text)
        data_array = np.array(df['data'], dtype=pd.Series)
        return data_array


# http://naelshiab.com/tutorial-send-email-python/
def sendmail(recipient, subject, message_text, attachment):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(message_text.encode('utf-8'), 'plain', 'utf-8'))

    # attaching all files
    for file in attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(file, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % file)
        msg.attach(part)

    smtp = smtplib.SMTP(server, port)
    smtp.starttls()
    smtp.login(sender, password_sender)
    text = msg.as_string()
    smtp.sendmail(sender, recipient, text)
    smtp.quit()


def send_birthdays_next_forty_days_all_persons():
    subject = "[EFG] Geburtstage (40 Tagen) + Gemeindeliste"
    all_persons_filename_xlsx = save_all_persons(get_all_persons())
    birthdays_filename_xlsx = save_birthdays(get_birthdays(0, 40))
    text = "Hallo,\n" + "anbei befindet sich " + \
           all_persons_filename_xlsx + " (das ist das aktuelle Gemeindeverzeichnis)." + \
           " Ausserdem noch: " + birthdays_filename_xlsx + " (das ist eine Liste der Geburtstagskinder der nächsten 40 Tage)\n\n\n" \
           + "(das ist eine automatisch erstellte email, falls irgendetwas nicht stimmt wende dich an Thorben S.)"
    for i in range(0, len(recipients)):
        sendmail(recipients[i], subject, text, [all_persons_filename_xlsx, birthdays_filename_xlsx])


send_birthdays_next_forty_days_all_persons()
