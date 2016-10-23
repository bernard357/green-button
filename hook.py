#!/usr/bin/env python
import json
import logging
import os
import requests
from requests_toolbelt import MultipartEncoder
import sys
import time
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
import yaml
from bottle import route, run, request, abort


# from bt.tn -- index page is triggered by the button itself
#
@route("/", method=['GET', 'POST'])
def from_bttn():
    """
    Processes the press of a bt.tn device

    This function is called from far far away, over the Internet
    """

    print("Button has been pressed")

    try:

        # step 1 - get a room, or create one if needed
        #
        room_id = get_room()

        # step 2 - ensure they are some listeners here
        #
        add_audience(room_id)

        # step 3 - process the action
        #
        process_push(room_id)

        print("Cisco Spark has been updated")
        return "OK\n"

    except Exception as feedback:
        print("ABORTED: fatal error has been encountered")
        print(str(feedback))
        raise

#
# Handle Cisco Spark API
#

def get_room():
    """
    Looks for a suitable Cisco Spark room

    :return: the id of the target room
    :rtype: ``str``

    This function creates a new room if necessary
    """

    print("Looking for Cisco Spark room '{}'".format(settings['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_BTTN_BOT']}
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
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_BTTN_BOT']}
    payload = {'title': settings['room'] }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")
    return response.json()['id']

def delete_room():
    """
    Deletes the target Cisco Spark room

    This function is useful to restart a clean demo environment
    """

    print("Deleting Cisco Spark room '{}'".format(settings['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_BTTN_BOT']}
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
            headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_BTTN_BOT']}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

            actual = True

    if actual:
        print("- room will be re-created in Cisco Spark on next button depress")
    else:
        print("- no room with this name yet - it will be created on next button depress")

    settings['shouldAddModerator'] = True

def add_audience(room_id):
    """
    Gives a chance to some listeners to catch updates

    :param room_id: identify the target room
    :type room_id: ``str``

    This function adds pre-defined listeners to a Cisco Spark room if necessary
    """

    if settings['shouldAddModerator'] is False:
        return

    print("Adding moderator to the Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_BTTN_BOT']}
    payload = {'roomId': room_id,
               'personEmail': settings['CISCO_SPARK_BTTN_MAN'],
               'isModerator': 'true' }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print("- done")

    settings['shouldAddModerator'] = False

def post_update(room_id, update):
    """
    Updates a Cisco Spark room

    :param room_id: identify the target room
    :type room_id: ``str``

    :param update: content of the update to be posted there
    :type update: ``str`` or ``dict``

    If the update is a simple string, it is sent as such to Cisco Spark.
    Else if it a dictionary, then it is encoded as MIME Multipart.
    """

    print("Posting update to Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/messages'
    headers = {'Authorization': 'Bearer '+settings['CISCO_SPARK_BTTN_BOT']}

    if isinstance(update, dict):
        update['roomId'] = room_id
        payload = MultipartEncoder(fields=update)
        headers['Content-Type'] = payload.content_type
    else:
        payload = {'roomId': room_id, 'text': update }

    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        print(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    print('- done, check the room with Cisco Spark client software')

#
# handle Twilio API
#

def call_conference(room_id, numbers):
    """"
    Triggers a conference call

    :param room_id: identify the target room
    :type room_id: ``str``

    :param numbers: a list of phone numbers to call
    :type numbers: ``list``

    This function creates a conference call and adds phone participants
    """
    print("- adding a conference call")
    update = { 'markdown': 'Arranging a conference call'}
    post_update(room_id, update)

    time.sleep(3)

    update = { 'markdown': 'Call [+44 12 34 56 78](tel:+44-12-34-56-78) to join the conference call from any phone.'}
    post_update(room_id, update)

    for line in numbers:
        print("- calling '{}'".format(line))
        update = { 'markdown': 'Adding {} to the conference call'.format(line)}
        post_update(room_id, update)

    time.sleep(5)
    return "Conference call will end when all participants will leave it"

def send_sms(room_id, details):
    """"
    Sends a SMS to target people

    :param room_id: identify the target room
    :type room_id: ``str``

    :param details: what to send and to which numbers
    :type details: ``list``

    This function uses the Twilio API to send a SMS message to target people
    """
    print("- sending a SMS")

    handle = TwilioRestClient(settings['TWILIO_ACCOUNT_SID'],
                              settings['TWILIO_AUTH_TOKEN'])

    message = ''
    from_number = None
    to_numbers = []

    for line in details:
        if not isinstance(line, dict):
            print("- invalid statement: '{}'".format(str(line)))
            update = { 'markdown': 'Unable to send a SMS - check configuration'}
            post_update(room_id, update)
            return

        if line.keys()[0] == 'message':
            message = line['message']

        if line.keys()[0] == 'from':
            from_number = line['from']

        if line.keys()[0] == 'number':
            to_numbers.append(line['number'])

    if len(message) < 4:
        print("- message should have at least 4 characters: '{}'".format(str(message)))
        update = { 'markdown': 'No SMS message to send - check configuration'}
        post_update(room_id, update)
        return

    print("- sending '{}'".format(message))

    if len(to_numbers) < 1:
        print("- no phone number has been defined")
        update = { 'markdown': 'No target phone number for SMS - check configuration'}
        post_update(room_id, update)
        return

    if from_number is None:
        from_number = to_numbers[0]

    for number in to_numbers:
        print("- sending to '{}'".format(number))

        try:
            handle.messages.create(body=message,
                                   to=number,
                                   from_=from_number)

        except TwilioRestException as feedback:
            print("- {}".format(str(feedback)))
            return

    update = { 'markdown': "SMS '{}' has been sent to '{}'".format(message,
                                                   ', '.join(to_numbers))}
    post_update(room_id, update)

def phone_call(room_id, details):
    """"
    Calls people

    :param room_id: identify the target room
    :type room_id: ``str``

    :param details: what to send and to which numbers
    :type details: ``list``

    This function uses the Twilio API to send a SMS message to target people
    """
    print("- passing a phone call")

    handle = TwilioRestClient(settings['TWILIO_ACCOUNT_SID'],
                              settings['TWILIO_AUTH_TOKEN'])

    url = ''
    from_number = None
    to_numbers = []

    for line in details:
        if not isinstance(line, dict):
            print("- invalid statement: '{}'".format(str(line)))
            update = { 'markdown': 'Unable to send a SMS - check configuration'}
            post_update(room_id, update)
            return

        if line.keys()[0] == 'url':
            url = line['url']

        if line.keys()[0] == 'from':
            from_number = line['from']

        if line.keys()[0] == 'number':
            to_numbers.append(line['number'])

    if len(url) < 4:
        print("- url should have at least 4 characters: '{}'".format(str(message)))
        update = { 'markdown': 'No URL for the call - check configuration'}
        post_update(room_id, update)
        return

    print("- using '{}'".format(url))

    if len(to_numbers) < 1:
        print("- no phone number has been defined")
        update = { 'markdown': 'No target phone number for call - check configuration'}
        post_update(room_id, update)
        return

    if from_number is None:
        from_number = to_numbers[0]

    for number in to_numbers:
        print("- calling '{}'".format(number))

        try:
            handle.calls.create(to=number,
                                from_=from_number,
                                url=url)

            update = { 'markdown': "Calling '{}'".format(number)}
            post_update(room_id, update)

        except TwilioRestException as feedback:
            print("- {}".format(str(feedback)))
            return

#
# behaviour of this software robot
#

def process_push(room_id):
    """
    Processes one push of the button

    :param room_id: identify the target room
    :type room_id: ``str``

    This function monitors the number of button pushes, and uses the appropriate
    action as defined in the configuration file, under the `bt.tn:` keyword.

    The action can be either:

    * send a text message to the room with `text:` statement
    * send a Markdown message to the room with `markdown:` statement
    * upload a file with `file:`, `label:` and `type:`
    * arrange a conference with numbers under the 'conference:' statement
    * a combination of any previous

    """

    print("Building update")

    items = settings['bt.tn']
    if settings['count'] < len(items):
        print("- using item {}".format(settings['count']))
        item = items[ settings['count'] ]

        update = {'text': ''}

        # textual message
        #
        if 'markdown' in item:

            text = 'using markdown content'
            update['markdown'] = item['markdown']

        elif 'message' in item:

            text = "'{}".format(item['message'])
            update['text'] += item['message']+'\n'

        # file upload
        #
        if 'file' in item:

            print("- attaching file {}".format(item['file']))

            if 'label' in item:
                text = item['label']
                update['text'] += "'{}'".format(item['label'])+'\n'

            else:
                text = item['file']

            if 'type' in item:
                type = item['type']
            else:
                type = 'application/octet-stream'

            update['files'] = (text, open(item['file'], 'rb'), type)

        # conference call
        #
        if 'conference' in item:
            call_conference(room_id, item['conference'])

        # send a SMS
        #
        if 'sms' in item:
            send_sms(room_id, item['sms'])

        # phone call
        #
        if 'call' in item:
            phone_call(room_id, item['call'])

    else:
        text = 'ping {}'.format(settings['count'])
        update = text

    settings['count'] += 1

    print("- {}".format(text))
    post_update(room_id, update)

def configure(name="settings.yaml"):
    """
    Reads configuration information

    :param name: the file that contains configuration information
    :type name: ``str``

    The function loads configuration from the file and from the environment.
    Port number can be set from the command line.

    Sample configuration file to illustrate capabilities of the program::

        room: "Green Forge"

        CISCO_SPARK_BTTN_BOT: "YWM2OEG4OGItNTQ5YS00MDU2LThkNWEtMJNkODk3ZDZLOGQ0OVGlZWU1NmYtZWyY"
        CISCO_SPARK_BTTN_MAN: "foo.bar@acme.com"

        port: 8080

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
            label: "Cisco Spark brings things and human beings together"

          - file: dimension-data.png
            type: "image/png"
            label: "Build new integrated systems and manage them"

    """

    print("Loading the configuration")

    with open(name, 'r') as stream:
        try:
            settings = yaml.load(stream)
            print("- from '{}'".format(name))
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

    if 'CISCO_SPARK_BTTN_BOT' not in settings:
        token = os.environ.get('CISCO_SPARK_BTTN_BOT')
        if token is None:
            logging.error("Missing CISCO_SPARK_BTTN_BOT in the environment")
            sys.exit(1)
        settings['CISCO_SPARK_BTTN_BOT'] = token

    if 'CISCO_SPARK_BTTN_MAN' not in settings:
        emails = os.environ.get('CISCO_SPARK_BTTN_MAN')
        if emails is None:
            logging.error("Missing CISCO_SPARK_NTTN_MAN in the environment")
            sys.exit(1)
        settings['CISCO_SPARK_BTTN_MAN'] = emails

    if 'TWILIO_ACCOUNT_SID' not in settings:
        token = os.environ.get('TWILIO_ACCOUNT_SID')
        if token is None:
            logging.error("Missing TWILIO_ACCOUNT_SID in the environment")
            sys.exit(1)
        settings['TWILIO_ACCOUNT_SID'] = token

    if 'TWILIO_AUTH_TOKEN' not in settings:
        token = os.environ.get('TWILIO_AUTH_TOKEN')
        if token is None:
            logging.error("Missing TWILIO_AUTH_TOKEN in the environment")
            sys.exit(1)
        settings['TWILIO_AUTH_TOKEN'] = token

    settings['count'] = 0

    return settings

# the program launched from the command line
#
if __name__ == "__main__":

    # read configuration file, look at the environment
    #
    settings = configure()

    # create a clean environment for the demo
    #
    delete_room()

    # wait for button pushes and other web requests
    #
    print("Preparing for web requests")
    run(host='0.0.0.0',
        port=settings['port'],
        debug=settings['DEBUG'],
        server=os.environ.get('SERVER', "auto"))
