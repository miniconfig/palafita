#! /usr/bin/python
#################################################
#       Palafita				#
#################################################
#  dev@miniconfig.com   			#
#						#
#################################################
#################################################

import json
import homeassistant.remote as remote
import homeassistant_settings as settings

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
                output_type = "PlainText"
                card_type = "Simple"
                card_title = "Location"
                card_content = hass_devices[user]
                print(output_speech)
                response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':True}	
                return response 

	elif request['intent']['name'] == "CurrentEnergyIntent":
                energy_usage = remote.get_state(api, 'sensor.energy_usage')
                output_speech = 'Your {} is {} {}.'.format(energy_usage.attributes['friendly_name'], energy_usage.state, energy_usage.attributes['unit_of_measurement'])
                output_type = "PlainText"

                card_type = "Simple"
                card_title = "Energy Usage"
                card_content = output_speech
                response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':False}
                return response

	elif request['intent']['name'] == "MonthlyEnergyIntent":
                energy_cost = remote.get_state(api, 'sensor.energy_cost')
                output_speech = 'Your {} is ${}'.format(energy_cost.attributes['friendly_name'], energy_cost.state)
                output_type = "PlainText"

                card_type = "Simple"
                card_title = "Energy Cost"
                card_content = output_speech
                response = {"outputSpeech": {"type":output_type,"text":output_speech},"card":{"type":card_type,"title":card_title,"content":card_content},'shouldEndSession':False}
                return response
                
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

