#!/usr/bin/env python
import json
import logging
import os
import requests
import sys
import time
import yaml
from bottle import route, run, request, abort


@route("/", method=['GET', 'POST'])
def from_bttn():
    """
    Processes the press of a bt.tn device

    This function is called when the button is pressed
    """

    print("Button has been pressed")
    try:

        room_id = get_room()

        add_audience(room_id)

        message = build_message()

        post_message(room_id, message)

        print("Cisco Spark has been updated")
        return "OK\n"

    except Exception as feedback:
        return str(feedback)+'\n'


def get_room():
    """
    Looks for a suitable Cisco Spark room

    :return: the id of the target room
    :rtype: ``str``

    This function creates a new room if necessary
    """

    print("Looking for Cisco Spark room '{}'".format(settings['room']))
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
#        print("- {}".format(item['title']))
        if settings['room'] in item['title']:
            print("- found it")
#            purge_room(item['id'])
            return item['id']

    print("- not found")
    print("Creating Cisco Spark room")
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    payload = {'title': settings['room'] }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")
    return response.json()['id']

def purge_room(room_id):
    """
    Purges the target Cisco Spark room

    :param room_id: identify the target room
    :type room_id: ``str``

    """

    print("Purging room")
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
        if settings['room'] not in item['title']:
            print("- {}".format(item['title']))
        else:
            print("- DELETING {}".format(item['title']))

            url = 'https://api.ciscospark.com/v1/rooms/{}'.format(item['id'])
            headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

def delete_room():
    """
    Deletes the target Cisco Spark room

    """

    print("Looking for Cisco Spark room '{}'".format(settings['room']))
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
        if settings['room'] not in item['title']:
            print("- {}".format(item['title']))
        else:
            print("- DELETING {}".format(item['title']))

            url = 'https://api.ciscospark.com/v1/rooms/{}'.format(item['id'])
            headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

def add_audience(room_id):
    """
    Gives a chance to listeners to catch the message

    :param room_id: identify the target room
    :type room_id: ``str``

    This function adds listeners to a Cisco Spark room if necessary
    """
    pass

def build_message():
    """
    Prepares a message for human beings

    :return: the message to be posted
    :rtype: ``str``

    """
    print("Building message")

    message = settings['bt.tn']
    print("- '{}'".format(message))

    return message

def post_message(room_id, message):
    """
    Updates a Cisco Spark room

    :param room_id: identify the target room
    :type room_id: ``str``

    :param message: content of the update to be posted there
    :type message: ``str``

    """

    print("Posting message to Cisco Spark room")

    payload = {'roomId': room_id, 'text': message }
    url = 'https://api.ciscospark.com/v1/messages'
    headers = {
        'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print('- done, check the room')

def initialize(name="settings.yaml"):
    """
    Reads configuration information

    :param name: the file that contains configuration information
    :type name: ``str``

    The function loads configuration from the file and from the environment.
    Port number can be set from the command line.
    """

    with open(name, 'r') as stream:
        try:
            settings = yaml.load(stream)
        except Exception as feedback:
            logging.error(str(feedback))
            sys.exit(1)

    if "room" not in settings:
        logging.error("Missing room: configuration information")
        sys.exit(1)

    if "bt.tn" not in settings:
        logging.error("Missing bt.tn: configuration information")
        sys.exit(1)

    if len(sys.argv) > 1:
        try:
            port_number = int(sys.argv[1])
        except:
            logging.error("Invalid port_number specified")
            sys.exit(1)
    elif "port" in settings:
        port_number = int(settings["port"])
    else:
        port_number = 80
    settings['port'] = port_number

    if 'DEBUG' in settings:
        debug = settings['DEBUG']
    else:
        debug = os.environ.get('DEBUG', False)
    settings['DEBUG'] = debug
    if debug:
        logging.basicConfig(level=logging.DEBUG)

    if 'CISCO_SPARK_TOKEN' not in settings:
        token = os.environ.get('CISCO_SPARK_TOKEN')
        if token is None:
            logging.error("Missing CISCO_SPARK_TOKEN in the environment")
            sys.exit(1)
        settings['CISCO_SPARK_TOKEN'] = token

    return settings

if __name__ == "__main__":

    settings = initialize()

    run(host='0.0.0.0',
        port=settings['port'],
        debug=settings['DEBUG'],
        server=os.environ.get('SERVER', "auto"))
