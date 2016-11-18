#!/usr/bin/env python

import unittest
import logging
import os
import random
import sys
import time
import mock
from requests import ConnectionError
import base64
import yaml


sys.path.insert(0, os.path.abspath('..'))

class HookTests(unittest.TestCase):

    def test_configure(self):

        print('***** Test configure ***')

        from hook import configure
        settings = configure()
        self.assertTrue(isinstance(settings, dict))

        settings = configure('settings.yaml')
        self.assertTrue(isinstance(settings, dict))

        self.assertTrue(len(settings['spark']['CISCO_SPARK_BTTN_BOT']) > 5)

        self.assertTrue(len(settings['twilio']['customer_service_number']) > 5)
        self.assertTrue(len(settings['twilio']['TWILIO_ACCOUNT_SID']) > 5)
        self.assertTrue(len(settings['twilio']['TWILIO_AUTH_TOKEN']) > 5)

        self.assertTrue(settings['server']['default'] == 'incident')

    def test_load_button(self):

        print('***** Test load button ***')

        from hook import configure, load_button
        settings = configure('settings.yaml')

        context = load_button(settings)
        context['count'] = 0
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['count'], 0)

        self.assertTrue(isinstance(context['bt.tn'], list))

        self.assertTrue(len(context['spark']['room']) > 1)
        self.assertTrue(len(context['spark']['CISCO_SPARK_BTTN_BOT']) > 5)

        self.assertTrue(len(context['twilio']['customer_service_number']) > 5)
        self.assertTrue(len(context['twilio']['TWILIO_ACCOUNT_SID']) > 5)
        self.assertTrue(len(context['twilio']['TWILIO_AUTH_TOKEN']) > 5)

        self.assertTrue(context['server']['default'] == 'incident')

        context = load_button(settings, name='incident')
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['name'], 'incident')
        self.assertEqual(context['count'], 0)

        self.assertTrue(isinstance(context['bt.tn'], list))

        self.assertTrue(len(context['spark']['room']) > 1)
        self.assertTrue(len(context['spark']['CISCO_SPARK_BTTN_BOT']) > 5)

        self.assertTrue(len(context['twilio']['customer_service_number']) > 5)
        self.assertTrue(len(context['twilio']['TWILIO_ACCOUNT_SID']) > 5)
        self.assertTrue(len(context['twilio']['TWILIO_AUTH_TOKEN']) > 5)

        self.assertTrue(context['server']['default'] == 'incident')

        context = load_button(settings, name='request')
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['name'], 'request')
        self.assertEqual(context['count'], 0)

        self.assertTrue(isinstance(context['bt.tn'], list))

        self.assertTrue(len(context['spark']['room']) > 1)
        self.assertTrue(len(context['spark']['CISCO_SPARK_BTTN_BOT']) > 5)

        self.assertTrue(len(context['twilio']['customer_service_number']) > 5)
        self.assertTrue(len(context['twilio']['TWILIO_ACCOUNT_SID']) > 5)
        self.assertTrue(len(context['twilio']['TWILIO_AUTH_TOKEN']) > 5)

        self.assertTrue(context['server']['default'] == 'incident')

    def test_load_buttons(self):

        print('***** Test load buttons ***')

        from hook import configure, load_buttons

        settings = configure('settings.yaml')
        buttons = load_buttons(settings)

        keys = buttons.keys()
        self.assertTrue('incident' in keys)
        self.assertTrue('request' in keys)


    def test_get_room(self):

        print('***** Test get room ***')

        from hook import configure, load_button, get_room

        settings = configure('settings.yaml')
        context = load_button(settings, name='request')
        self.assertTrue(isinstance(context, dict))

        try:
            get_room(context)
        except ConnectionError:
            pass

    @mock.patch('hook.send_sms', return_value='pumpkins')
    @mock.patch('hook.phone_call', return_value='pumpkins')
    def test_incident(self, send_sms_patch, phone_call_patch):

        print('***** Test incident script ***')

        from hook import configure, load_button, handle_button, delete_room
        settings = configure('settings.yaml')
        context = load_button(settings, name='incident')
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['count'], 0)

        try:
            handle_button(context)

            self.assertEqual(context['count'], 1)

            handle_button(context)

            self.assertEqual(context['count'], 2)

            handle_button(context)

            self.assertEqual(context['count'], 3)

            handle_button(context)

            self.assertEqual(context['count'], 4)

            delete_room(context)
        except ConnectionError:
            pass

    @mock.patch('hook.send_sms', return_value='pumpkins')
    @mock.patch('hook.phone_call', return_value='pumpkins')
    def test_request(self, send_sms_patch, phone_call_patch):

        print('***** Test request script ***')

        from hook import configure, load_button, handle_button, delete_room
        settings = configure('settings.yaml')
        context = load_button(settings, name='request')
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['count'], 0)

        try:
            handle_button(context)

            self.assertEqual(context['count'], 1)

            handle_button(context)

            self.assertEqual(context['count'], 2)

            delete_room(context)
        except ConnectionError:
            pass

    def test_token(self):

        print('***** Test security token ***')

        from hook import encode, decode

        settings = {'name': 'button_123', 'server': {}}
        self.assertEqual(encode(settings), 'button_123')
        self.assertEqual(decode(settings, 'button_123'), 'button_123')

        self.assertEqual(decode(settings, ''), '')
        self.assertEqual(decode(settings, 'YnV0dG9uXzEyMzo50BCcIslRbBiMjVU16EkT'), 'YnV0dG9uXzEyMzo50BCcIslRbBiMjVU16EkT')

        settings = {'name': 'button_123', 'server': {'key': 'a_secret'}}
        self.assertEqual(encode(settings), 'YnV0dG9uXzEyMzpPZEFRbkNMSlVXd1lqSTFWTmVoSkV3PT0=')
        self.assertEqual(decode(settings, 'YnV0dG9uXzEyMzpPZEFRbkNMSlVXd1lqSTFWTmVoSkV3PT0='), 'button_123')

        settings = {'name': 'button_456', 'server': {'key': 'a_secret'}}
        self.assertEqual(encode(settings), 'YnV0dG9uXzQ1Njp4UEVzZVdNTmJDUEY1aDdnWXh5Q0t3PT0=')
        self.assertEqual(decode(settings, 'YnV0dG9uXzQ1Njp4UEVzZVdNTmJDUEY1aDdnWXh5Q0t3PT0='), 'button_456')

        settings = {'name': 'button_123', 'server': {'key': 'another_secret'}}
        self.assertEqual(encode(settings), 'YnV0dG9uXzEyMzo5c1duS2hCTjRTQTl5eVUvUTFsNUFRPT0=')
        self.assertEqual(decode(settings, 'YnV0dG9uXzEyMzo5c1duS2hCTjRTQTl5eVUvUTFsNUFRPT0='), 'button_123')

        with self.assertRaises(Exception):
            decode(settings, '')

        with self.assertRaises(Exception):
            decode(settings, settings['name'])

        with self.assertRaises(Exception):
            decode(settings, base64.b64encode(settings['name']))

        with self.assertRaises(Exception):
            hash = 'forged_hash'
            decode(settings, base64.b64encode(settings['name']+':'+hash))

    def test_generate_tokens(self):

        print('***** Test generate tokens ***')

        from hook import generate_tokens, decode

        settings = {'server': {}}
        tokens = generate_tokens(settings, ('incident', 'request'))
        self.assertEqual(tokens, {})

        settings = {'server': {'key': 'a_secret'}}
        tokens = generate_tokens(settings, ('incident', 'request'))
        self.assertEqual(tokens.keys(), ['incident', 'request'])
        self.assertEqual(tokens['incident'], 'aW5jaWRlbnQ6WHFUWXBoc0tvV2toMkdTM1dQTHpIZz09')
        self.assertEqual(decode(settings, tokens['incident']), 'incident')
        self.assertEqual(tokens['request'], 'cmVxdWVzdDpGT2krUDJpM0lJY0hEbFYxZ2R6UGZ3PT0=')
        self.assertEqual(decode(settings, tokens['request']), 'request')

        with open(os.path.abspath(os.path.dirname(__file__))+'/../.tokens', 'r') as handle:
            tokens2 = yaml.load(handle)

        self.assertEqual(tokens, tokens2)


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
