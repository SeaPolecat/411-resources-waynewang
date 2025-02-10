from flask import Flask, make_response, request
import os

app = Flask(__name__)

@app.route('/')
def hello():
    response = make_response(
        {
            'response': 'Hello, World!',
            'status': 200
        }
    )
    return response

# adding an 'input' parameter
# call like http://localhost:5002/repeat?input=blahblahblah
@app.route('/repeat')
def input_anything():
    input = request.args.get('input')

    response = make_response(
        {
            'body': input,
            'status': 200
        }
    )
    return response

# expose on multiple endpoints
@app.route('/health')
@app.route('/healthcheck')
def health():
    response = make_response(
        {
            'response': 'OKAY',
            'status': 200
        }
    )
    return response

if __name__ == '__main__':
    # By default flask is only accessible from localhost.
    # Set this to '0.0.0.0' to make it accessible from any IP address
    # on your network (not recommended for production use)
    app.run(host='0.0.0.0', port=os.getenv('PORT'), debug=True)
