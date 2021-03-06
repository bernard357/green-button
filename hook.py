#!/usr/bin/env python
import json
import logging
import os
import requests
from requests_toolbelt import MultipartEncoder
import socket
import sys
import time
from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
import twilio.twiml
import yaml
import copy
import base64
import hmac

#
# web services
#

from bottle import Bottle, route, run, request, abort, response, static_file, template
web = Bottle()

@web.route("/ping", method=['GET', 'POST'])
def web_ping():
    """
    Tests the web service
    """
    return 'pong'

@web.get('/files/<filename:path>')
def serve_file(filename):
    logging.info("Serving '{}'".format(filename))
    return static_file(filename, root='./files')

@web.route("/index", method=['GET', 'POST'])
@web.route("/index/<token>", method=['GET', 'POST'])
def web_index(token=None):
    """
    provides an index of buttons

    This function is called from far far away, over the Internet
    """

    logging.info('Serving index page')

    try:
        if 'key' not in settings['server']:
            pass

        elif decode_token(settings, token) != 'index':
            raise ValueError('Invalid label in token')

    except Exception as feedback:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.error("Unable to serve the index page")
            raise
        else:
            logging.error(str(feedback))
            response.status = 400
            return 'Invalid request'

    items = []
    global buttons
    for button in buttons:
        items.append({
            'label': button,
            'delete-url': '/delete/'+settings['tokens'].get(button+'-delete'),
            'initialise-url': '/initialise/'+settings['tokens'].get(button+'-initialise'),
            'push-url': '/'+settings['tokens'].get(button),
            })
    logging.debug('Buttons: {}'.format(items))

    return template('views/list_items', prefix=settings['server']['url'], items=items)

#
# invoked from bt.tn
#

@web.route("/", method=['GET', 'POST'])
@web.route("/<button>", method=['GET', 'POST'])
def web_press(button=None):
    """
    Processes the press of a bt.tn device

    This function is called from far far away, over the Internet
    """

    if button is None:
        button = settings['server']['default']

    try:

        button = decode_token(settings, button)

        context = load_button(settings, button)

        return handle_button(context)

    except socket.error as feedback:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.error("Unable to push '{}'".format(button))
            raise
        else:
            logging.error(str(feedback))
            response.status = 500
            return 'Internal error'

    except Exception as feedback:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.error("Unable to push '{}'".format(button))
            raise
        else:
            logging.error(str(feedback))
            response.status = 400
            return 'Invalid request'

def handle_button(context):
    """
    Handles the press of a button

    :param context: button state and configuration
    :type context: ``dict``

    """

    logging.info("Handling button '{}'".format(context['name']))

    context['spark']['id'] = get_room(context)

    process_push(context)

    return "OK {}\n".format(context['count'])

def process_push(context):
    """
    Processes one push of the button

    :param context: button state and configuration
    :type context: ``dict``

    This function monitors the number of button pushes, and uses the appropriate
    action as defined in the configuration file, under the `bt.tn:` keyword.

    The action can be either:

    * send a text message to the room with `text:` statement
    * send a Markdown message to the room with `markdown:` statement
    * upload a file with `file:`, `label:` and `type:`
    * arrange a conference with numbers under the 'conference:' statement
    * a combination of any previous

    """

    logging.info("Processing push")

    context['count'] += 1

    if 'time' in context:
        elapsed = time.time() - context['time']
    else:
        elapsed = 0

    if 'reset' in context['spark']:
        reset = int(context['spark']['reset']) * 60
        if elapsed > reset:
            context['count'] = 1

    update, phone = get_push_details(context)

    if 'sms' in phone:
        send_sms(context, phone['sms'])

    if 'call' in phone:
        phone_call(context, phone['call'])

    post_update(context, update)

    context['time'] = time.time()

def get_push_details(context):
    """
    Provides actions for current push

    :param context: button state and configuration
    :type context: ``dict``

    The action can be either:

    * send a text message to the room with `text:` statement
    * send a Markdown message to the room with `markdown:` statement
    * upload a file with `file:`, `label:` and `type:`
    * arrange a conference with numbers under the 'conference:' statement
    * a combination of any previous

    """

    logging.info("Getting push details")

    update = {'text': ''}
    phone = {}

    items = context['bt.tn']
    if context['count'] < len(items)+1:
        logging.info("- using item {}".format(context['count']))
        item = items[ context['count']-1 ]

        # textual message
        #
        if 'markdown' in item:
            update['markdown'] = item['markdown']

        elif 'message' in item:
            update['text'] += item['message']+'\n'

        # file upload
        #
        if 'file' in item:

            logging.info("- attaching file '{}'".format(item['file']))

            if 'label' in item:
                text = item['label']
                update['text'] += "'{}'".format(item['label'])+'\n'

            else:
                text = item['file']

            if 'type' in item:
                type = item['type']
            else:
                type = 'application/octet-stream'

            update['files'] = (text, open(os.path.abspath(os.path.dirname(__file__))+'/'+item['file'], 'rb'), type)

        # send a SMS
        #
        if 'sms' in item:
            phone = { 'sms': item['sms'] }

        # phone call
        #
        if 'call' in item:
            phone = { 'call': item['call'] }

    # ping message
    #
    else:
        update['text'] = 'push {}'.format(context['count'])

    return update, phone

#
# Handle Cisco Spark API
#

def get_room(context):
    """
    Looks for a suitable Cisco Spark room

    :param context: button state and configuration
    :type context: ``dict``

    :return: the id of the target room
    :rtype: ``str``

    This function creates a new room if necessary
    """

    logging.info("Looking for Cisco Spark room '{}'".format(context['spark']['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+context['spark']['CISCO_SPARK_BTTN_BOT']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        logging.info(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    for item in response.json()['items']:
        if context['spark']['room'] in item['title']:
            logging.info("- found it")
            context['spark']['id'] = item['id']
            return item['id']

    logging.info("- not found")

    return create_room(context)

def create_room(context):
    """
    Creates a new Cisco Spark room

    :param context: button state and configuration
    :type context: ``dict``

    :return: the id of the target room
    :rtype: ``str``

    This function also adds appropriate audience to the room
    """

    logging.info("Creating Cisco Spark room '{}'".format(context['spark']['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+context['spark']['CISCO_SPARK_BTTN_BOT']}
    payload = {'title': context['spark']['room'] }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        logging.info(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    logging.info("- done")
    room_id = response.json()['id']
    context['spark']['id'] = get_room(context)

    add_audience(context)

    return room_id

@web.route("/initialise", method=['GET', 'POST'])
@web.route("/initialise/<button>", method=['GET', 'POST'])
def web_initialise(button=None):
    """
    Initialises a room

    This function is called from far far away, over the Internet
    """

    if button is None:
        button = settings['server']['default']

    logging.info("Initialising button '{}'".format(button))

    try:
        button = decode_token(settings, button, action='initialise')

        context = load_button(settings, button)
        delete_room(context)

        global buttons
        buttons.pop(button, None)

        context = load_button(settings, button)
        context['spark']['id'] = get_room(context)

        return 'OK'

    except Exception as feedback:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.error("Unable to initialise '{}'".format(button))
            raise
        else:
            logging.error(str(feedback))
            response.status = 400
            return 'Invalid request'

@web.route("/delete", method=['GET', 'POST'])
@web.route("/delete/<button>", method=['GET', 'POST'])
def web_delete(button=None):
    """
    Deletes a room

    This function is called from far far away, over the Internet
    """

    if button is None:
        button = settings['server']['default']

    logging.info("Deleting button '{}'".format(button))

    try:
        button = decode_token(settings, button, action='delete')

        context = load_button(settings, button)
        delete_room(context)

        global buttons
        buttons.pop(button, None)

        return 'OK'

    except Exception as feedback:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.error("Unable to delete '{}'".format(button))
            raise
        else:
            logging.error(str(feedback))
            response.status = 400
            return 'Invalid request'

def delete_room(context):
    """
    Deletes the target Cisco Spark room

    :param context: button state and configuration
    :type context: ``dict``

    This function is useful to restart a clean demo environment
    """

    logging.info("Deleting Cisco Spark room '{}'".format(context['spark']['room']))

    url = 'https://api.ciscospark.com/v1/rooms'
    headers = {'Authorization': 'Bearer '+context['spark']['CISCO_SPARK_BTTN_BOT']}
    response = requests.get(url=url, headers=headers)

    if response.status_code != 200:
        logging.info(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    actual = False
    for item in response.json()['items']:

        if context['spark']['room'] in item['title']:
            logging.info("- DELETING IT")

            url = 'https://api.ciscospark.com/v1/rooms/{}'.format(item['id'])
            headers = {'Authorization': 'Bearer '+context['spark']['CISCO_SPARK_BTTN_BOT']}
            response = requests.delete(url=url, headers=headers)

            if response.status_code != 204:
                raise Exception("Received error code {}".format(response.status_code))

            actual = True

    if actual:
        logging.info("- room will be re-created in Cisco Spark on next button depress")
    else:
        logging.info("- no room with this name yet - it will be created on next button depress")

def add_audience(context):
    """
    Gives a chance to some listeners to catch updates

    :param context: button state and configuration
    :type context: ``dict``

    This function adds pre-defined listeners to a Cisco Spark room
    """

    logging.info("Adding moderators to the Cisco Spark room")

    for item in context['spark'].get('moderators', ()):
        logging.info("- {}".format(item))
        add_person(context, person=item, isModerator='true')

    logging.info("Adding participants to the Cisco Spark room")

    for item in context['spark'].get('participants', ()):
        logging.info("- {}".format(item))
        add_person(context, person=item)

def add_person(context, person=None, isModerator='false'):
    """
    Adds a person to a room

    :param context: button state and configuration
    :type context: ``dict``

    :param person: e-mail address of the person to add
    :type person: ``str``

    :param isModerator: for moderators
    :type isModerator: `true` or `false`

    """

    url = 'https://api.ciscospark.com/v1/memberships'
    headers = {'Authorization': 'Bearer '+context['spark']['CISCO_SPARK_BTTN_BOT']}
    payload = {'roomId': context['spark']['id'],
               'personEmail': person,
               'isModerator': isModerator }
    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        logging.info(response.json())
        raise Exception("Received error code {}".format(response.status_code))

def post_update(context, update):
    """
    Updates a Cisco Spark room

    :param context: button state and configuration
    :type context: ``dict``

    :param update: content of the update to be posted there
    :type update: ``str`` or ``dict``

    If the update is a simple string, it is sent as such to Cisco Spark.
    Else if it a dictionary, then it is encoded as MIME Multipart.
    """

    logging.info("Posting update to Cisco Spark room")

    url = 'https://api.ciscospark.com/v1/messages'
    headers = {'Authorization': 'Bearer '+context['spark']['CISCO_SPARK_BTTN_BOT']}

    if isinstance(update, dict):
        update['roomId'] = context['spark']['id']
        payload = MultipartEncoder(fields=update)
        headers['Content-Type'] = payload.content_type
    else:
        payload = {'roomId': context['spark']['id'], 'text': update }

    response = requests.post(url=url, headers=headers, data=payload)

    if response.status_code != 200:
        logging.info(response.json())
        raise Exception("Received error code {}".format(response.status_code))

    logging.info('- done, check the room with Cisco Spark client software')

#
# handle Twilio API
#

def send_sms(context, details):
    """"
    Sends a SMS to target people

    :param context: button state and configuration
    :type context: ``dict``

    :param details: what to send and to which numbers
    :type details: ``list``

    This function uses the Twilio API to send a SMS message to target people
    """
    logging.info("- sending a SMS")

    handle = TwilioRestClient(context['twilio']['TWILIO_ACCOUNT_SID'],
                              context['twilio']['TWILIO_AUTH_TOKEN'])

    message = ''
    from_number = context['twilio']['customer_service_number']
    to_numbers = []

    for line in details:
        if not isinstance(line, dict):
            logging.error("Invalid statement: '{}'".format(str(line)))
            update = { 'markdown': 'Error: Unable to send a SMS - check configuration'}
            post_update(context, update)
            return

        if line.keys()[0] == 'message':
            message = line['message']

        if line.keys()[0] == 'from':
            from_number = line['from']

        if line.keys()[0] == 'number':
            to_numbers.append(line['number'])

    if len(message) < 4:
        logging.error("Message should have at least 4 characters: '{}'".format(str(message)))
        update = { 'markdown': 'Error: No SMS message to send - check configuration'}
        post_update(context, update)
        return

    logging.info("- sending '{}'".format(message))

    if len(to_numbers) < 1:
        logging.error("No phone number has been defined")
        update = { 'markdown': 'Error: No target phone number for SMS - check configuration'}
        post_update(context, update)
        return

    if from_number is None:
        from_number = to_numbers[0]

    for number in to_numbers:
        logging.info("- sending to '{}'".format(number))

        try:
            pass
            handle.messages.create(body=message,
                                   to=number,
                                   from_=from_number)

        except socket.error as feedback:
            logging.error("Unable to communicate with Twilio API endpoint")
            logging.error(str(feedback))
            update = { 'markdown': 'Error: Unable to communicate with Twilio API endpoint'}
            post_update(context, update)
            return

        except TwilioRestException as feedback:
            logging.error("Receive Exception from Twilio API")
            logging.error(str(feedback))
            update = { 'markdown': 'Error: Receive Exception from Twilio API'}
            post_update(context, update)
            return

    update = { 'markdown': "SMS '{}' has been sent to '{}'".format(message,
                                                   ', '.join(to_numbers))}
    post_update(context, update)

def phone_call(context, details):
    """"
    Calls people

    :param context: button state and configuration
    :type context: ``dict``

    :param details: what to send and to which numbers
    :type details: ``list``

    This function uses the Twilio API to send a SMS message to target people
    """
    logging.info("- passing a phone call")

    handle = TwilioRestClient(context['twilio']['TWILIO_ACCOUNT_SID'],
                              context['twilio']['TWILIO_AUTH_TOKEN'])

    url = ''
    from_number = context['twilio']['customer_service_number']
    to_numbers = []
    say = ''

    for line in details:
        if not isinstance(line, dict):
            logging.error("Invalid statement: '{}'".format(str(line)))
            update = { 'markdown': 'Error: Unable to call - check configuration'}
            post_update(context, update)
            return

        if line.keys()[0] == 'url':
            url = line['url']

        if line.keys()[0] == 'say':
            context['twilio']['say'] = line['say']

        if line.keys()[0] == 'from':
            from_number = line['from']

        if line.keys()[0] == 'number':
            to_numbers.append(line['number'])

    if len(url) < 4:
        if context['server']['url'] is None:
            logging.error("Missing url: configuration information")
            update = { 'markdown': 'Error: No URL for the call - check configuration'}
            post_update(context, update)
            return
        url = context['server']['url'].rstrip('/')+'/call/'+encode_token(context, context['name'], action='call')

    logging.info("- using '{}'".format(url))

    if len(to_numbers) < 1:
        logging.error("No phone number has been defined")
        update = { 'markdown': 'Error: No target phone number for call - check configuration'}
        post_update(context, update)
        return

    if from_number is None:
        from_number = to_numbers[0]

    for number in to_numbers:
        logging.info("- calling '{}'".format(number))

        try:
            handle.calls.create(to=number,
                                from_=from_number,
                                url=url)

            update = { 'markdown': "Calling '{}'".format(number)}
            post_update(context, update)

        except socket.error as feedback:
            logging.error("Unable to communicate with Twilio API endpoint")
            logging.error(str(feedback))
            update = { 'markdown': 'Error: Unable to communicate with Twilio API endpoint'}
            post_update(context, update)
            return

        except TwilioRestException as feedback:
            logging.error("Receive Exception from Twilio API")
            logging.error(str(feedback))
            update = { 'markdown': 'Error: Receive Exception from Twilio API'}
            post_update(context, update)
            return

@web.route("/call", method=['GET', 'POST'])
@web.route("/call/<button>", method=['GET', 'POST'])
def web_inbound_call(button=None):
    """
    Handles an inbound phone call

    This function is called from twilio cloud back-end
    """

    if button is None:
        button = settings['server']['default']

    logging.info("Receiving inbound call for button '{}'".format(button))

    try:
        button = decode_token(settings, button, action='call')

        context = load_button(settings, button)
        update, twilio_action = get_push_details(context)

        response.content_type = 'text/xml'
        behaviour = twilio.twiml.Response()

        say = None
        if 'call' in twilio_action:
            for line in twilio_action['call']:
                if line.keys()[0] == 'say':
                    say = line['say']
                    break

        if say is None:
            say = "What's up Doc?"

        behaviour.say(say)
        return str(behaviour)

    except Exception as feedback:
        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            logging.error("Unable to handle inbound call for '{}'".format(button))
            raise
        else:
            logging.error(str(feedback))
            response.status = 400
            return 'Invalid request'

#
# the collection of buttons that we manage
#

buttons = {}

def load_buttons(settings):

    global buttons
    buttons = {}

    for there, unused, files in os.walk(os.path.abspath(os.path.dirname(__file__))+'/buttons'):
        logging.debug("Walking %s", there)

        for file in files:
            logging.debug("Found file %s", file)
            button, extension = file.split('.', 1)
            if extension == 'yaml':
                buttons[ button ] = load_button(settings, button)

    return buttons

def load_button(settings, name='incident'):
    """
    Loads settings that are specific to a button

    :param settings: generic settings
    :type settings: ``dict``

    :param name: the button identifier
    :type name: ``str``

    :return: button settings
    :rtype: ``dict``

    This function uses generic settings, and adds any settings from the file
    that is specific to the button.

    In other terms, if the button ``hello`` is loaded, then the software
    uses the file ``buttons/hello.yaml`` in combination with ``settings.yaml``

    """

    # memoization
    #
    global buttons
    if name in buttons:
        return buttons[ name ]

    # this button was unknown so far
    #
    context = copy.deepcopy(settings)

    context['name'] = name

    name = 'buttons/'+name+'.yaml'

    try:
        logging.info('Loading configuration from {}'.format(name))
        with open(os.path.abspath(os.path.dirname(__file__))+'/'+name, 'r') as stream:
            additions = yaml.load(stream)
    except Exception as feedback:
        logging.error(str(feedback))
        raise

    if not isinstance(additions, dict):
        logging.error('No configuration information in {}'.format(name))
        return context

    for key in additions.keys():
        if additions[key] is None:
            pass

        elif key not in context:
            context[key] = additions[key]

        elif isinstance(context[key], list):
            context[key] += additions[key]

        elif isinstance(context[key], dict):
            context[key].update(additions[key])

        else:
            context[key] = additions[key]

    if "bt.tn" not in context:
        logging.error("Missing bt.tn: configuration information")

    if len(context['bt.tn']) < 1:
        logging.error("Missing bt.tn: actions in configuration")

    if "room" not in context['spark']:
        logging.error("Missing room: configuration information")

    if "moderators" not in context['spark']:
        logging.error("Missing moderators: configuration information")

    # first push of this button
    #
    context['count'] = 0

    # save button state and security token
    #
    buttons[ context['name'] ] = context
    generate_tokens(settings, buttons.keys())

    return context

#
# server management
#

def configure(name="settings.yaml"):
    """
    Reads configuration information

    :param name: the file that contains generic configuration information
    :type name: ``str``

    :return: generic settings
    :rtype: ``dict``

    The function loads configuration from the file and from the environment.
    Port number can be set from the command line.

    """

    logging.info('Loading configuration from {}'.format(name))

    with open(os.path.abspath(os.path.dirname(__file__))+'/'+name, 'r') as stream:
        try:
            settings = yaml.load(stream)
        except Exception as feedback:
            logging.error(str(feedback))
            sys.exit(1)

    if "spark" not in settings:
        logging.error("Missing spark: configuration information")

    if settings['spark'] is None:
        settings['spark'] = {}

    if 'CISCO_SPARK_BTTN_BOT' not in settings['spark']:
        token = os.environ.get('CISCO_SPARK_BTTN_BOT')
        if token is None:
            logging.error("Missing CISCO_SPARK_BTTN_BOT in the environment")
        settings['spark']['CISCO_SPARK_BTTN_BOT'] = token


    if "twilio" not in settings:
        logging.error("Missing twilio: configuration information")

    if "customer_service_number" not in settings['twilio']:
        logging.error("Missing customer_service_number: configuration information")

    if 'TWILIO_ACCOUNT_SID' not in settings['twilio']:
        token = os.environ.get('TWILIO_ACCOUNT_SID')
        if token is None:
            logging.error("Missing TWILIO_ACCOUNT_SID in the environment")
        settings['twilio']['TWILIO_ACCOUNT_SID'] = token

    if 'TWILIO_AUTH_TOKEN' not in settings['twilio']:
        token = os.environ.get('TWILIO_AUTH_TOKEN')
        if token is None:
            logging.error("Missing TWILIO_AUTH_TOKEN in the environment")
        settings['twilio']['TWILIO_AUTH_TOKEN'] = token


    if "server" not in settings:
        logging.error("Missing server: configuration information")

    if len(sys.argv) > 1:
        try:
            port_number = int(sys.argv[1])
        except:
            logging.error("Invalid port_number specified")
    elif "port" in settings['server']:
        port_number = int(settings['server']['port'])
    else:
        port_number = 80
    settings['server']['port'] = port_number

    if 'url' not in settings['server']:
        url = os.environ.get('BTTN_URL')
        if url is None:
            logging.warning("Missing BTTN_URL in the environment")
        settings['server']['url'] = url

    if 'default' not in settings['server']:
        settings['server']['default'] = 'incident'

    return settings

def encode_token(settings, label=None, action=None):
    """
    Provides a security token for a button
    """

    if label is None:
        label = settings['name']

    if 'key' not in settings['server']:
        return label

    if action is not None:
        label += '-'+action

    hash = base64.b64encode(hmac.new(settings['server']['key'], label).digest())

    return base64.b64encode(label+':'+hash)

def decode_token(settings, token, action=None):
    """
    Decodes button name from a security token
    """

    if 'key' not in settings['server']:
        return token

    try:
        label, hash = base64.b64decode(token).split(':', 1)
    except TypeError as feedback:
        logging.error('Incorrect encoding of the security token')
        raise Exception('Invalid security token')
    except ValueError as feedback:
        logging.error('No hash in security token')
        raise Exception('Invalid security token')

    expected = base64.b64encode(
        hmac.new(settings['server']['key'], label).digest())

    if hash != expected:
        logging.error('Incorrect hash in security token')
        raise Exception('Invalid security token')

    if action is None:
        return label

    items = label.split('-', 1)

    if len(items) < 2:
        logging.error('Missing action in security token')
        raise Exception('Invalid security token')

    if items[1] != action:
        logging.error('Incorrect action in security token')
        raise Exception('Invalid security token')

    return items[0]

def generate_tokens(settings, buttons):

    tokens = {}
    for button in buttons:

        tokens[button] = encode_token(settings, button)

        tokens[button+'-call'] = encode_token(settings, button, action='call')

        tokens[button+'-delete'] = encode_token(settings, button, action='delete')

        tokens[button+'-initialise'] = encode_token(settings, button, action='initialise')

    tokens['index'] = encode_token(settings, 'index')

    settings['tokens'] = tokens

    with open(os.path.abspath(os.path.dirname(__file__))+'/.tokens', 'w') as handle:
        yaml.dump(tokens, handle, default_flow_style=False)

    return tokens

#
# launched from the command line
#

if __name__ == "__main__":

    # uncomment only one
    #
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    #logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    # read configuration file, look at the environment
    #
    settings = configure()
    logging.debug('Settings: {}'.format(settings))

    # pre-load all available buttons
    #
    load_buttons(settings)
    logging.debug('Tokens: {}'.format(settings['tokens']))

    # wait for button pushes and other web requests
    #
    logging.info("Preparing for web requests")
    web.run(host='0.0.0.0',
        port=settings['server']['port'],
        debug=(logging.getLogger().getEffectiveLevel() == logging.DEBUG),
        server=os.environ.get('SERVER', "auto"))
