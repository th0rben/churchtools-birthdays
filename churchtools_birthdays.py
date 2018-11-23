import requests
import json
from config import domain, mail, password, password_sender, sender, recipients, server, port, filename
import smtplib
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def login(session):
    url = domain + '?q=login'
    data = {'email' : mail, 
            'password' : password,
            'directtool' : 'yes'}
    return session.post(url, data).content
    
def logout(session):
    url = domain + '?q=logout';
    data = {'func' : 'logout', 
            'directtool' : 'yes'}
    return session.post(url, data).content

# ensures that Umlaute are getting displayed correctly
def umlaute_correcter(string):
    return string.replace("\\u00f6", "ö").replace("\\u00e4", "ä").replace("\\u00df", "ß").replace("\\u00fc", "ü")

def save_birthdays(data):
    file = open(filename, 'w')
    csvwriter = csv.writer(file)

    count = 0
    for emp in data:
        if count == 0:
            header = emp.keys()
            csvwriter.writerow(header)
            count += 1
        csvwriter.writerow(emp.values())

    file.close()
    
def create_message(response, message):
    response_str = str(response.content).replace('b\'{"status":', '{"status":', 1).replace('"}]}\'', '"}]}', 1)
    data = json.loads(response_str)
    data = data["data"]
    save_birthdays(data)
    for i in range(0, len(data)): 
        person_json = data[i]
        vorname = person_json["vorname"]
        nachname = person_json["name"]
        geburtsdatum = person_json["geburtsdatum_d"]
        message = umlaute_correcter(message) + vorname + " " + nachname + " " + geburtsdatum + "\n"
    message = message + "Für mehr Infos: siehe details.csv" + "\n \n" + "(Dies ist eine automatisch erstellte Nachricht)"
    return message

def get_birthdays(from_int, to_int, message):
    with requests.Session() as s:
        login(s)
        url = domain + '?q=churchdb/ajax'
        data = {'func' : 'getBirthdayList', 
                "from" : str(from_int), 
                "to" : str(to_int)}
        response = s.post(url, data)
        html = create_message(response, message)
        logout(s)
        return html

# http://naelshiab.com/tutorial-send-email-python/    
def sendmail(recipient, subject, message_text, attached_file):
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
     
    msg.attach(MIMEText(message_text.encode('utf-8'), 'plain', 'utf-8'))
    attachment = open("./"+ attached_file, "rb")
     
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % attached_file)
     
    msg.attach(part)
     
    smtp = smtplib.SMTP(server, port)
    smtp.starttls()
    smtp.login(sender, password_sender)
    text = msg.as_string()
    smtp.sendmail(sender, recipient, text)
    smtp.quit()

def send_birthdays_last_week():
    subject = "Geburtstage der letzten Woche (Sonntag-Sonntag)"
    text = "Hallo,\n" + "in der vergangenen Woche hatten Geburtstag: \n"
    text = get_birthdays(-5, 2, text)
    for i in range(0, len(recipients)):
        sendmail(recipients[i], subject, text, filename)

send_birthdays_last_week()