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



class MasterHandler:

    def lights_brightness_down():
        PrivateCache.broadlink_handler.floorlamp_brightness_down()
        PrivateCache.hue_handler.set_incremental_brightness(-50)
        return

    def lights_brightness_up():
        PrivateCache.broadlink_handler.floorlamp_brightness_up()
        PrivateCache.hue_handler.set_incremental_brightness(50)
        return

    @staticmethod
    def scene_bright():
        PrivateCache.broadlink_handler.floorlamp_warm()
        PrivateCache.hue_handler.activate_scene_by_name('Bright Scene')
                
        return

    @staticmethod
    def scene_concentrate():
        PrivateCache.broadlink_handler.floorlamp_cold()
        PrivateCache.hue_handler.activate_scene_by_name('Concentrate Scene')
                
        return

    @staticmethod
    def scene_movie():
        PrivateCache.broadlink_handler.floorlamp_night()
        PrivateCache.hue_handler.activate_scene_by_name('Movie Scene')
                
        return

    
    @staticmethod
    def tv_get_volume():
        volume = PrivateCache.tv_handler.get_volume()['volumeStatus']['volume']
        PrivateCache.sio.emit('client_event', {'volume': volume, 'data_tag': 'volume'})

    @staticmethod
    def tv_reconnect():
        if not PrivateCache.tv_handler.is_connected():
            if PrivateCache.tv_handler.is_tv_reachable():
                PrivateCache.tv_handler.connect()
                PrivateCache.tv_handler.subscribe_get_volume(on_volume_change_handler)

        MasterHandler.tv_send_heartbeat()                                    
        MasterHandler.tv_get_volume()
        return

    @staticmethod
    def tv_send_heartbeat():
        connected = PrivateCache.tv_handler.is_connected()

        data = {'data_tag': 'tv_heartbeat'}
        if connected:
            data['data'] = 'tv_connected'
        else:
            data['data'] = 'tv_disconnected'

        PrivateCache.sio.emit('local_server_msg', data )

        return 

    @staticmethod
    def tv_on_off():
        PrivateCache.broadlink_handler.tv_on_off()        
        return

    @staticmethod
    def lock_workstation():
        import ctypes
        ctypes.windll.user32.LockWorkStation()

    @staticmethod
    def snap_email():
        handler = pysve.email_handler.EmailHandler()
        handler.attach_snap_to_inbox()

        return    

def on_volume_change_handler(status, payload):
    print(payload)
    if status:
        print('volume change callback triggered')
        # pass
    else:
        print("Something went wrong.")

    PrivateCache.should_update_volume = True
    return

def init():

    log_filename = log_file_full_path('{}.log'.format(dt.datetime.strftime(dt.datetime.now(), '%Y%m%d_%H_%M_%S')))
    init_logger(log_filename)


    PrivateCache.hue_handler = zlhue.HueHandler()
    PrivateCache.broadlink_handler = zlbroadlink.BroadlinkHandler()
    PrivateCache.sio = socketio.Client()

    PrivateCache.tv_handler = zlwebostv.TVHandler()
    PrivateCache.tv_handler.subscribe_get_volume(on_volume_change_handler)

    PrivateCache.command_handler_map = {
        'tv_notify': lambda: PrivateCache.tv_handler.send_notification('Activate'),
        "tv_volume_up": lambda: logging.info(PrivateCache.tv_handler.volume_up()),
        "tv_volume_down": lambda: logging.info(PrivateCache.tv_handler.volume_down()),
        "tv_source_pc": lambda: PrivateCache.tv_handler.set_source(1),
        "tv_source_appletv": lambda: PrivateCache.tv_handler.set_source(0),
        "tv_set_volume": lambda x: PrivateCache.tv_handler.set_volume(int(x)),
        "tv_get_volume": MasterHandler.tv_get_volume,
        "tv_request_heartbeat": MasterHandler.tv_send_heartbeat,
        "tv_reconnect": MasterHandler.tv_reconnect,
        "tv_on_off": MasterHandler.tv_on_off,
        
        'lights_on': PrivateCache.hue_handler.lights_on,
        'lights_off': PrivateCache.hue_handler.lights_off,
        'lights_brightness_up': MasterHandler.lights_brightness_up,
        'lights_brightness_down': MasterHandler.lights_brightness_down,

        "scene_bright": MasterHandler.scene_bright,
        "scene_night": lambda: PrivateCache.hue_handler.activate_scene_by_name('Nightlight'),
        "scene_focus": MasterHandler.scene_concentrate,
        "scene_movie": MasterHandler.scene_movie,
        "lock_work_station": MasterHandler.lock_workstation,
        "snap_email": MasterHandler.snap_email,
    }


def tv_send_heartbeat_repeat():
    
    while True:
        MasterHandler.tv_send_heartbeat()
        time.sleep(60 * 30)

    return

def tv_volume_update_repeat():
    
    while True:
        if PrivateCache.should_update_volume:
            try:
                PrivateCache.should_update_volume = False
                MasterHandler.tv_get_volume()
            except:
                pass

        time.sleep(1)
    return

def main():
    init()    


    # Create a Socket.IO client
    

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


    # Connect to the Flask-SocketIO server
    #sio.connect('http://localhost:5000')
    
    if utils.get_env() == 'prod':
        PrivateCache.sio.connect('http://eatoomuch.com:5000')    
    else:
        PrivateCache.sio.connect('http://localhost:5000')    
    # PrivateCache.sio.disconnect()

    # Send a message to the server
    PrivateCache.sio.emit('client_event', {'data': 'Hello from Python client!'})

    thread_heartbeat = threading.Thread(target=tv_send_heartbeat_repeat)
    thread_heartbeat.start()


    thread_tv_volume_update = threading.Thread(target=tv_volume_update_repeat)
    thread_tv_volume_update.start()

    # Keep the client running
    PrivateCache.sio.wait()    

   
if __name__ == '__main__':
    main()



    
    
    