import requests
import json
from config import domain, mail, password, password_sender, sender, recipients, server, port
import smtplib

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
def umlaute_correcter(str):
    return str.replace("\\u00f6", "oe").replace("\\u00e4", "ae").replace("\\u00df", "ss").replace("\\u00fc", "ue")

def create_message(response, message):
    response_str = str(response.content).replace('b\'{"status":', '{"status":', 1).replace('"}]}\'', '"}]}', 1)
    data = json.loads(response_str)
    data = data["data"]
    for i in range(0, len(data)): 
        person_json = data[i]
        vorname = person_json["vorname"]
        nachname = person_json["name"]
        geburtsdatum = person_json["geburtsdatum_d"]
        message = umlaute_correcter(message) + vorname + " " + nachname + " " + geburtsdatum + "\n"
    message = message + "\n" + "(Dies ist eine automatisch erstellte Nachricht)"
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
        
def get_birthdays_last_week():
    subject = "Geburtstage der letzten Woche (Sonntag-Sonntag)"
    text = "Hallo,\n" + "in der vergangenen Woche hatten Geburtstag: \n"
    message = "Subject: {}\n\n{}".format(subject, text)
    return get_birthdays(-5, 2, message)

# send text as email
def sendmail(message):
    smtp_server = smtplib.SMTP_SSL(server, port)
    smtp_server.login(sender, password_sender)
    for i in range(0, len(recipients)):
        print(recipients[i])
        print(sender)
        print(message)
        smtp_server.sendmail(sender, recipients[i], message)
    smtp_server.close()
    
sendmail(get_birthdays_last_week())