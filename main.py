import requests
import json
from config import domain, mail, password

def login(session):
    url = domain + '?q=login'
    data = {'email' : mail, 
            'password' : password,
            "rememberMe":"true", 
            "top_login":"true",
            'directtool' : 'yes'}
    return session.post(url, data).content
    
def logout(session):
    url = domain + '?q=logout';
    data = {'func' : 'logout', 
            'directtool' : 'yes'}
    return session.post(url, data).content

def create_message(response):
    response_str = str(response.content).replace('b\'{"status":', '{"status":', 1).replace('"}]}\'', '"}]}', 1)
    data = json.loads(response_str)
    data = data["data"]
    message = "Hallo,\n" + "in den nächsten 30 Tagen haben Geburtstag: \n"
    for i in range(0, len(data)): 
        person_json = data[i]
        vorname = person_json["vorname"]
        nachname = person_json["name"]
        geburtsdatum = person_json["geburtsdatum_d"]
        message = message + vorname + " " + nachname + " " + geburtsdatum + "\n"
    # ensures that Umlaute are getting displayed correctly
    message = message.replace("\\u00f6", "ö").replace("\\u00e4 ", "ä").replace("\\u00fc  ", "ß") + "\n" + "(Dies ist eine automatisch erstellte Nachrit)"
    return message

with requests.Session() as s:
    login(s)
    url = domain + '?q=churchdb/ajax'
    data = {'func' : 'getBirthdayList', 
            "from" : '0', 
            "to" : '30'}
    response = s.post(url, data)
    html = create_message(response)
    print(html)
    logout(s)