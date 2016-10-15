#!/usr/bin/env python
import json
import logging
import os
import requests
from requests_toolbelt import MultipartEncoder
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

        post_message(room_id=room_id, message=message)

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
        if settings['room'] in item['title']:
            print("- found it")
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

    print("Purging room {}".format(room_id))

    url = 'https://api.ciscospark.com/v1/messages'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    payload = {'roomId': room_id }
    response = requests.get(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
        print("- deleting message {}".format(item['id']))

        url = 'https://api.ciscospark.com/v1/messages/{}'.format(item['id'])
        headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
        response = requests.delete(url=url, headers=headers)

        if response.status_code != 204:
            raise Exception("Received error code {}".format(response.status_code))

def delete_room():
    """
    Deletes the target Cisco Spark room

    """

    print("Deleting Cisco Spark room '{}'".format(settings['room']))
    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    actual = False
    for item in response.json()['items']:
        if settings['room'] in item['title']:
            print("- found it")
            print("- DELETING IT")

            url = 'https://api.ciscospark.com/v1/rooms/{}'.format(item['id'])
            headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

            actual = True

    if actual:
        print("- room will be re-created in Cisco Spark on next button depress")
    else:
        print("- no room with this name yet - it will be created on next button depress")

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
    :rtype: ``str`` or ``dict`

    """
    print("Building message")

    items = settings['bt.tn']
    if settings['count'] < len(items):
        print("- using item {}".format(settings['count']))
        item = items[ settings['count'] ]

        message = {}

        if 'markdown' in item:

            text = 'using markdown content'
            message['markdown'] = item['markdown']

        elif 'message' in item:

            text = item['message']
            message['text'] = item['message']

        if 'file' in item:

            print("- attaching file {}".format(item['file']))

            if 'label' in item:
                text = item['label']

                if 'text' not in message:
                    message['text'] = text

            else:
                text = item['file']

            if 'type' in item:
                type = item['type']
            else:
                type = 'application/octet-stream'

            message['files'] = (text, open(item['file'], 'rb'), type)

    else:
        text = 'ping {}'.format(settings['count'])
        message = text

    settings['count'] += 1

    print("- '{}'".format(text))
    return message

def post_message(room_id, message):
    """
    Updates a Cisco Spark room

    :param room_id: identify the target room
    :type room_id: ``str``

    :param message: content of the update to be posted there
    :type message: ``str`` or ``dict``

    If the message is a simple string, it is sent as such to Cisco Spark.
    Else if it a dictionary, then it is encoded as MIME Multipart.
    """

    print("Posting message to Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/messages'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_TOKEN']}

    if isinstance(message, dict):
        message['roomId'] = room_id
        payload = MultipartEncoder(fields=message)
        headers['Content-Type'] = payload.content_type
    else:
        payload = {'roomId': room_id, 'text': message }

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

    Sample configuration file to illustrate capabilities of the program:

        port: 8080

        room: "Green Forge"

        bt.tn:

          - markdown: |
                Green Power has been invoked again
                ==================================

                The [green button](https://d2jaw3pqpetn6l.cloudfront.net/app/uploads/2016/05/27125600/product-images-bttn-normal-green-600x600.jpg) has been pressed, so there is a need for urgent action.

                Some context to this event: *Italic*, **bold**, and `monospace`.
                Itemized lists look like this:

                  * this one
                  * that one
                  * the other one

                Unicode is supported. \xe2 And [Incident Management](https://en.wikipedia.org/wiki/Incident_management_(ITSM)) too.
                Call Global Service Center at [+44 12 34 56 78](tel:+44-12-34-56-78) if people are late to join this room.
                We will continue to feed this room with information.



          - file: IncidentReportForm.pdf
            type: "application/pdf"
            label: "Print and fill this report"

          - file: bt.tn.png
            type: "image/png"
            label: "European buttons that rock"

          - file: spark.png
            type: "image/png"
            label: "Cisco Spark joins things with human beings"

          - file: dimension-data.png
            type: "image/png"
            label: "Build new integrated systems and manage them"

    """

    print("Initialising the configuration")

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

    settings['count'] = 0

    return settings

if __name__ == "__main__":

    settings = initialize()

    delete_room()

    print("Preparing for web requests")
    run(host='0.0.0.0',
        port=settings['port'],
        debug=settings['DEBUG'],
        server=os.environ.get('SERVER', "auto"))
