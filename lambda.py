# -*- coding: utf-8 -*-
from __future__ import print_function
import urllib
import xml.etree.ElementTree as ET

"""
MIT License

copyright 2017 Bruno Hautzenberger

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

"""
This Lambda Function is used for the "Aquarinthia" Alexa Skill.
It queries Information about Carinthia's lakes in Carinthia's OpenData
records from data.ktn.gv.at.
"""

class Lake(object):
    """
    Used to store structured Lake data extracted from the georss feed
    """
    
    def __init__(self):
        self.name = ""
        self.temp = ""
        self.waterheight = ""
        self.date_of_meassurment = ""
        
    def get_temp_string(self):
        return "Der " + self.name + " hat " + self.temp + ". Zeitpunkt der Messung: " + self.date_of_meassurment
    
    def get_water_height_string(self):
        return "Der Pegelstand des " + self.name + " ist " + self.waterheight + ". Zeitpunkt der Messung: " + self.date_of_meassurment
    
    def get_info_string(self):
        return "Der " + self.name + " hat " + self.temp + " und der Pegelstand beträgt " + self.waterheight + ". Zeitpunkt der Messung: " + self.date_of_meassurment

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

# --------------- Functions to load data ----------------------

def get_lake_data():
    feed = urllib.urlopen("https://info.ktn.gv.at/asp/hydro/hydro_stationen_see_rss_mit_Werte.asp")

    tree = ET.parse(feed)
    root = tree.getroot()
    lake_entries = root.findall('channel/item')
    
    lakes = {}
    for lake_entry in lake_entries:
        lake = Lake()
        title = lake_entry.find('title')
        desc = lake_entry.find('description')
        if title != None and desc != None:
            lake.name = title.text.split('-')[0].strip().lower()
            desc_data = desc.text.replace("<p>",'').replace("</p>",'').replace("\n",'').split('<br>')
            
            for line in desc_data:
                if line.startswith("Datum/Uhrzeit"):
                    lake.date_of_meassurment = line.split(' : ')[1]
                    if len(lake.date_of_meassurment.split(":")) == 3:
                        lake.date_of_meassurment = lake.date_of_meassurment[:-3] + " Uhr"
                    else:
                        lake.date_of_meassurment = lake.date_of_meassurment + " Uhr"
                    
                elif line.startswith("Wasserstand"):
                    lake.waterheight = line.split(':')[1] .strip()+ "cm"
                elif line.startswith("Wassertemperatur"):
                    lake.temp = line.split(':')[1].strip() + "°C"
        
            lakes[lake.name] = lake
            
            print(lake.name)
            print(lake.date_of_meassurment)
    
    return lakes

# --------------- Functions that control the skill's behavior ------------------

def handle_intent_lake_temp(intent, session):
    """
    Tries to find temperature for a given lake.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    if 'LakeName' in intent['slots'] and intent['slots']['LakeName'].has_key("value"):
        lake = intent['slots']['LakeName']['value']
        lakes = get_lake_data()
        if lakes.has_key(lake):
            speech_output = lakes[lake].get_temp_string()
            reprompt_text = lakes[lake].get_temp_string()
        else:
            speech_output = "Diesen See konnte ich leider nicht finden."
            reprompt_text = "Versuche es zum Beispiel mit 'Wie warm ist der Wörthersee'."
    else:
        speech_output = "Diesen See konnte ich leider nicht finden."
        reprompt_text = "Versuche es zum Beispiel mit 'Wie warm ist der Wörthersee'."
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_intent_lake_water_height(intent, session):
    """
    Tries to find water height for a given lake.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    if 'LakeName' in intent['slots'] and intent['slots']['LakeName'].has_key("value"):
        lake = intent['slots']['LakeName']['value']
        lakes = get_lake_data()
        if lakes.has_key(lake):
            speech_output = lakes[lake].get_water_height_string()
            reprompt_text = lakes[lake].get_water_height_string()
        else:
            speech_output = "Diesen See konnte ich leider nicht finden."
            reprompt_text = "Versuche es zum Beispiel mit 'Wie hoch ist der Pegelstand des Wörthersee'."
    else:
        speech_output = "Diesen See konnte ich leider nicht finden."
        reprompt_text = "Versuche es zum Beispiel mit 'Wie hoch ist der Pegelstand des Wörthersee'."
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def handle_intent_lake_info(intent, session):
    """
    Tries to find information for a given lake.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = True

    if 'LakeName' in intent['slots'] and intent['slots']['LakeName'].has_key("value"):
        lake = intent['slots']['LakeName']['value']
        lakes = get_lake_data()
        if lakes.has_key(lake):
            speech_output = lakes[lake].get_info_string()
            reprompt_text = lakes[lake].get_info_string()
        else:
            speech_output = "Diesen See konnte ich leider nicht finden."
            reprompt_text = "Versuche es zum Beispiel mit 'Informationen zum Wörthersee'."
    else:
        speech_output = "Diesen See konnte ich leider nicht finden."
        reprompt_text = "Versuche es zum Beispiel mit 'Informationen zum Wörthersee'."
    
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session)) 

def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Bis zum nächsten Mal"
                    
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Wilkommen"
    speech_output = "Willkommen zu Aquarinthia. Hier bekommst du Informationen über Kärntens Seen. " 
                    
    # If the user does not respond text.
    reprompt_text = "Du kannst mich zum Beispiel fragen wie warm der Woerthersee ist."
                    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they want """
    print("on_launch requestId=" + launch_request['requestId'] + ", sessionId=" + session['sessionId'])
    return get_welcome_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "IntentLaketemp":
        return handle_intent_lake_temp(intent, session)
    elif intent_name == "IntentLakeWaterHeight":
        return handle_intent_lake_water_height(intent, session)
    elif intent_name == "IntentLakeInfo":
        return handle_intent_lake_info(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")

# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        print("lambda Handler")
        return on_intent(event['request'], event['session'])
