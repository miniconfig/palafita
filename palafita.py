#! /usr/bin/python
#################################################
#       Palafita                                #
#################################################
#  dev@miniconfig.com                           #
#                                               #
#################################################
#################################################

import json
import homeassistant.remote as remote
import homeassistant_settings as settings
from homeassistant.const import STATE_LOCKED, STATE_UNLOCKED

homeassistant_server = settings.homeassistant_server
homeassistant_api = settings.homeassistant_api
api=remote.API(homeassistant_server, homeassistant_api)
appVersion = 1.0

def get_entity_type(state):
    entity_id = state.entity_id
    entity_type = entity_id.partition('.')[0]
    return entity_type

def data_init():
        global MyDataStore
        MyDataStore = DataStore()

def data_handler(rawdata):
        global MyDataStore
        currentSession = MyDataStore.getSession(rawdata['session'])
        currentUser = MyDataStore.getUser(rawdata['session'])
        currentRequest = rawdata['request']
        response = request_handler(currentSession, currentUser, currentRequest)
        return json.dumps({"version":appVersion,"response":response},indent=2,sort_keys=True)

def request_handler(session, user, request):
        requestType = request['type']
        
        if requestType == "LaunchRequest":
                return launch_request(session, user, request)
        elif requestType == "IntentRequest":
                return intent_request(session, user, request)

def build_response(output_speech, shouldEndSession=True):
    output_type = "PlainText"
    response = {"outputSpeech" : {"type":output_type, "text":output_speech}, 'shouldEndSession':shouldEndSession}
    return response
 
def launch_request(session, user, request):
        output_speech = "Welcome to HomeAssistant"
        output_type = "PlainText"

        card_type = "Simple"
        card_title = "HomeAssistant"
        card_content = "Hello"

        response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':False}

        return response

def intent_request(session, user, request):
        if request['intent']['name'] == "LocateIntent":
                hass_devices = {}
                user = request['intent']['slots']['User']['value']
                allStates=remote.get_states(api)
                for state in allStates:
                    if get_entity_type(state) == "device_tracker":
                        hass_devices[state.attributes['friendly_name']]=state.state
                output_speech = user + " is at " + hass_devices[user]
                return build_response(output_speech) 

        elif request['intent']['name'] == "LockIntent":
                matched_lock = False
                action = request['intent']['slots']['Action']['value']
                requested_lock = request['intent']['slots']['LockName']['value']
                allStates = remote.get_states(api)
                for state in allStates:
                    if get_entity_type(state) == "lock":
                        friendly_name = state.attributes['friendly_name']
                        if friendly_name.lower() == requested_lock:
                            matched_lock = True
                            print(action)
                            if action == "lock":
                                remote.set_state(api, state.entity_id, new_state=STATE_LOCKED)
                                output_speech = "I have locked the " + requested_lock
                            elif action == "unlock":
                                remote.set_state(api, state.entity_id, new_state=STATE_UNLOCKED)
                                output_speech = "I have unlocked the " + requested_lock
                if matched_lock == False:
                    output_speech = "I'm sorry, I have not found a lock by that name."
                return build_response(output_speech)
      
        elif request['intent']['name'] == "BedIntent":
                who = request['intent']['slots']['Who']['value']
                if who == "We are" or who == "We're":
                   script_name = "script.go_to_bed2"
                else:
                   script_name = "script.go_to_bed1"
                remote.call_service(api, 'script', 'turn_on', {'entity_id': '{}'.format(script_name)}) 
                output_speech = "Goodnight"
                return build_response(output_speech)

        elif request['intent']['name'] == "WakeIntent":
                script_name = "script.wake_up"
                remote.call_service(api, 'script', 'turn_on', {'entity_id': '{}'.format(script_name)})
                output_speech = "Good Morning"
                return build_response(output_speech)
        
        elif request['intent']['name'] == "CurrentEnergyIntent":
                energy_usage = remote.get_state(api, 'sensor.energy_usage')
                output_speech = 'Your {} is {} {}.'.format(energy_usage.attributes['friendly_name'], energy_usage.state, energy_usage.attributes['unit_of_measurement'])
                return build_response(output_speech)

        elif request['intent']['name'] == "MonthlyEnergyIntent":
                energy_cost = remote.get_state(api, 'sensor.energy_cost')
                output_speech = 'Your {} is ${}'.format(energy_cost.attributes['friendly_name'], energy_cost.state)
                return build_response(output_speech)
                
        elif request['intent']['name'] ==  "HelpIntent":
                output_speech = "This is the HomeAssistant app. Right now, you can only ask where someone is, or ask about your energy usage.  But I have big plans. "
                output_type = "PlainText"
                card_type = "Simple"
                card_title = "HelloWorld - Title"
                card_content = "HelloWorld - This is the Hello World help! Just say Hi"

                response = {"outputSpeech": {"type":output_type,"text":output_speech},'shouldEndSession':False}

                return response
        
                
        else:
                return launch_request(session, user, request) ##Just do the same thing as launch request





class Session:
        def __init__(self,sessionData):
                self.sessionId = sessionData['sessionId']


        def getSessionID(self):
                return self.sessionId

class User:
        def __init__(self,userId):
                self.userId = userId
                self.settings = {}

        def getUserId(self):
                return self.userId

class DataStore:
        def __init__(self):
                self.sessions = {}
                self.users = {}

        def getSession(self,session):
                if session['new'] is True or session['sessionId'] not in self.sessions:
                        self.sessions[session['sessionId']] = Session(session)

                return self.sessions[session['sessionId']]

        def getUser(self,session):
                userId = session['user']['userId']
                if userId not in self.users:
                        self.users[userId] = User(userId)

                return self.users[userId]

