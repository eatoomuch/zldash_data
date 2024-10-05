import os
import logging
import datetime as dt
from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, send
from flask_cors import CORS, cross_origin
import json
import eventlet
import utils



def init_logger(
    log_filename: str
):
    log_file_folder = os.path.dirname(log_filename)

    if not os.path.exists(log_file_folder):
        print(f"Log file folder doesn't exist, creating: {log_file_folder}")
        os.mkdir(log_file_folder)

    # Configure the logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Create a file handler that logs to a file
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)

    # Create a handler for stdout that logs to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create a formatter for both handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Set the formatter for both handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Get the root logger and add both handlers
    logger = logging.getLogger()
    logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def log_file_full_path(file_name):
    log_file_folder = os.path.join(__file__, '../../log')
    log_file_folder = os.path.abspath(log_file_folder)

    full_path = f'{log_file_folder}/{file_name}'
    return full_path



class PrivateCache:
    pass

def init():

    log_filename = log_file_full_path('{}.log'.format(dt.datetime.strftime(dt.datetime.now(), '%Y%m%d_%H_%M_%S')))
    init_logger(log_filename)




def login_handler(meta):
    username = meta['username']
    password = meta['password']


    if username == 'admin' and password == 'admin':
        return {'token': 'admin'}   
    else:
        return {'token': None} # not allowed to login

def main():
    init()
    
    app = Flask(__name__)
    CORS(app)  # Allow all origins, adjust as needed
    app.config['SECRET_KEY'] = 'secret!'
    socketio = SocketIO(app, cors_allowed_origins='*')
    
    command_handler_map = {
        "login": login_handler,
    }


    @app.route('/', methods=['POST'])
    @cross_origin()
    def handle_post():
        logging.info('POST received\n')
        data = request.get_json()
        
        
        socketio.emit('server_response', data)

        command_received = data.get('data', 'Unknown')

        logging.debug('received Post.')

        if command_received in command_handler_map:
            handler = command_handler_map[command_received]

            meta = data.get('meta', 'Unknown')

            if meta != 'Unknown':
                logging.info('Received')
                response = handler(meta)
            else:
                response = handler()

            logging.info('Received POST request: {}'.format(command_received))
        else:
            response = 'No POST handler found for the request from websocket server'

        return jsonify({'message': 'Request received', 'data_received': data, 'data': response})
    # Change host to '0.0.0.0' to allow network access

    @app.route('/os-info', methods=['GET'])
    def os_info():
        os_type = platform.system()  # This will give 'Linux', 'Windows', 'Darwin' (macOS), etc.
        return jsonify({'platform': os_type})

    @socketio.on('message')
    def handle_message(message):
        print(f'Received message: {message}')
        send(message, broadcast=True)        

    @socketio.on('connect')
    def handle_connect():
        print('Client connected')

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('client_event')
    def handle_client_event(data):
        print('Received data from client:', data)
        socketio.emit('server_response', {'message': 'Ack from server!'})        

        if data.get('data_tag', '') == 'volume':
            socketio.emit('volume_update', {'volume': data['volume']})        

    @socketio.on('local_server_msg')
    def handle_local_server_msg(data):
        print('Received data from local server:', data)
        socketio.emit('server_response', {'message': 'Ack from server!'})        

        if data.get('data_tag', '') != '':
            socketio.emit(data['data_tag'], data)        
            print('Received data from local server. Proceed to relaying.')

    @app.route('/send_message')
    def send_message():
        message = "Hello from the server!"
        socketio.emit('server_response', message)
        return "Message sent to all clients!"

    # app.run(host='0.0.0.0', port=5000, debug=True)
    port = utils.get_websocket_port()
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), app)


if __name__ == '__main__':
    main()
    