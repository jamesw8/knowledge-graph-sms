import requests
from flask import Flask, request
from twilio.rest import Client as Twilio
from pprint import pprint
import os

app = Flask(__name__)

def get_api_key():
	try:
		with open('google_api_key', 'r') as f:
			return f.read()
	except:
		return os.environ.get('google_api_key')

def get_twilio_credentials():
	sid = None
	token = None
	try:
		with open('twilio_sid', 'r') as f:
			sid = f.read()
		with open('twilio_auth_token' ,'r') as f:
			token = f.read()
	except:
		sid = os.environ.get('twilio_sid')
		token = os.environ.get('twilio_auth_token')
	return sid, token

twilio_sid, twilio_auth_token = get_twilio_credentials()

twilio_client = None

def initialize_twilio_client():
	global twilio_client
	twilio_client = Twilio(twilio_sid, twilio_auth_token)

initialize_twilio_client()

api_key = get_api_key()
knowledge_graph_api_link = "https://kgsearch.googleapis.com/v1/entities:search"
geocoding_api_link = "https://maps.googleapis.com/maps/api/geocode/json"

def send_message(to, from_, body):
	 message = client.messages.create(
		to=to,
		from_=from_,
		body=body)
	 return message

def search(query):
	res = requests.get(knowledge_graph_api_link, params={'query':query, 'key':api_key})
	return res.json()

def get_first_result(res):
	if len(res.get('itemListElement', [])) == 0:
		return None
	return res.get('itemListElement', [])[0]['result']

def get_address(query):
	res = requests.get(geocoding_api_link, params={'address':query, 'key':api_key})
	return res.json()

def main():
	query = input('Query? ')
	search_result = search(query)

	result = get_first_result(search_result)
	if result is None:
		print('Nothing')
	else:
		pprint(result)
		types = result.get('@type', '')
		address = get_address(query)['results'][0]['formatted_address']
		if 'description' in result.keys():
			print(query,' is a ', result['description'])
		print('Description:', result['detailedDescription']['articleBody'])
		print('It is located at', address)
		print(query,' falls under the categories: ', ', '.join(types), '.', sep='')

@app.route('/')
def index():
	return 'Welcome to the landing page!'

@app.route('/sms', methods=['POST'])
def handle_incoming_sms():
	query = request.form.get('Body')
	from_ = request.form.get('From')

	app.logger.info('Query: %s coming from %s', query, from_)
	body = ''

	search_result = search(query)
	result = get_first_result(search_result)
	if result is None:
		body += 'No results found'
	else:
		try:
			pprint(result)
			types = result.get('@type', '')
			address_results = get_address(query)['results']
			if len(address_results) == 0:
				address_string = 'Could not find the location of your query'
			else:
				address_string = '\nIt is located at {}\n'.format(address_results[0]['formatted_address'])
			if 'description' in result.keys():
				body += '{} is a {}\n'.format(query, result['description'])
			if 'detailedDescription' in result.keys():
				body += 'Description: {}\n'.format(result['detailedDescription']['articleBody'])
			body += address_string
			body += '\n{} falls under the categories: {}'.format(query, ', '.join(types))
		except Exception as e:
			print(e)
			body += 'Error'
	print(send_message(from_, os.environ.get('twilio_number'), body))

	return 'SMS endpoint'

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)