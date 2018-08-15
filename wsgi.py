from knowledge_graph import app
import os

if __name__ == '__main__':
	app.run(port=int(os.environ.get('port', 5000)), host='0.0.0.0')