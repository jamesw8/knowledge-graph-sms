import requests

def get_api_key():
	try:
		with open('google_api_key', 'r') as f:
			return f.read()
	except:
		return None

api_key = get_api_key()
knowledge_graph_api_link = "https://kgsearch.googleapis.com/v1/entities:search"
geocoding_api_link = "https://maps.googleapis.com/maps/api/geocode/json"

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
if __name__ == '__main__':
	main()