import os
import logging
import datetime as dt
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import zlwebostv
import zlhue
import zlpath
import platform
import socketio
import pysve.email_handler
import zlbroadlink
import threading
import time
import utils

class PrivateCache:
    should_update_volume = False

    pass


def init_logger(
    log_filename: str
):
    log_file_folder = os.path.dirname(log_filename)

    if not os.path.exists(log_file_folder):
        print(f"Log file folder doesn't exist, creating: {log_file_folder}")
        os.makedirs(log_file_folder)

    # Configure the logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')

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
    log_file_folder = zlpath.file_path_from_project_root(['log', 'dash_server'])

    full_path = f'{log_file_folder}/{file_name}'
    return full_path

def publish_data_repeat():

    while True:

        MasterHandler.publishData()

        time.sleep(2)

    return

class MasterHandler:

    def publishData():        
        data_str = '123\n12312\n <br>123'
        current_time = time.localtime()
        time_string = time.strftime("%Y-%m-%d %H:%M:%S", current_time)

        data_str += time_string

        
        data = {'data_tag': 'rt_data', 'data': data_str}
        PrivateCache.sio.emit('local_server_msg', data )
        return
     

def init():

    log_filename = log_file_full_path('{}.log'.format(dt.datetime.strftime(dt.datetime.now(), '%Y%m%d_%H_%M_%S')))
    init_logger(log_filename)


    PrivateCache.sio = socketio.Client()


    PrivateCache.command_handler_map = {        
        "frontend_request_data_refresh": MasterHandler.publishData
    }



def main():
    init()    

    # PrivateCache.sio = socketio.Client()


    

    # Define event handler for when connected to the server
    @PrivateCache.sio.event
    def connect():
        print('Connected to server')

    # Define event handler for when disconnected from the server
    @PrivateCache.sio.event
    def disconnect():
        print('Disconnected from server')

    # # Define event handler for receiving messages from the server
    @PrivateCache.sio.event
    def server_response(data):
        print('Message from server:', data)
        command_received = data.get('data', 'Unknown')

        if command_received in PrivateCache.command_handler_map:
            handler = PrivateCache.command_handler_map[command_received]

            meta = data.get('meta', 'Unknown')
            logging.info('Received valid command.')

            if meta != 'Unknown':                
                response = handler(meta)
            else:
                response = handler()

            logging.info('Received websocket request: {}'.format(command_received))
            
            
            # sio.emit('client_event', {'data': response})


        else:
            response = 'No handler found for the request.'

        # return jsonify({'message': 'Request received', 'data_received': data, 'data': response})


    if utils.get_env() == 'prod':
        PrivateCache.sio.connect('http://eatoomuch.com:5000')    
    else:
        PrivateCache.sio.connect('http://localhost:5000') 


    thread_data_pub = threading.Thread(target=publish_data_repeat)
    thread_data_pub.start()

    
   
    # PrivateCache.sio.disconnect()

    # Send a message to the server
    PrivateCache.sio.emit('client_event', {'data': 'Hello from Python client!'})


    # Keep the client running
    PrivateCache.sio.wait()    

   
if __name__ == '__main__':
    main()



    
    
    