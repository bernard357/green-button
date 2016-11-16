#!/usr/bin/env python

import unittest
import logging
import os
import random
import sys
import time
import mock

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

    def test_get_room(self):

        print('***** Test get room ***')

        from hook import configure, load_button, get_room

        settings = configure('settings.yaml')
        context = load_button(settings, name='request')
        self.assertTrue(isinstance(context, dict))

        get_room(context)

    @mock.patch('hook.send_sms', return_value='pumpkins')
    @mock.patch('hook.phone_call', return_value='pumpkins')
    def test_incident(self, send_sms_patch, phone_call_patch):

        print('***** Test incident script ***')

        from hook import configure, load_button, handle_button
        settings = configure('settings.yaml')
        context = load_button(settings, name='incident')
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['count'], 0)

        handle_button(context)

        self.assertEqual(context['count'], 1)

        handle_button(context)

        self.assertEqual(context['count'], 2)

        handle_button(context)

        self.assertEqual(context['count'], 3)

        handle_button(context)

        self.assertEqual(context['count'], 4)

    @mock.patch('hook.send_sms', return_value='pumpkins')
    @mock.patch('hook.phone_call', return_value='pumpkins')
    def test_request(self, send_sms_patch, phone_call_patch):

        print('***** Test request script ***')

        from hook import configure, load_button, handle_button
        settings = configure('settings.yaml')
        context = load_button(settings, name='request')
        self.assertTrue(isinstance(context, dict))

        self.assertEqual(context['count'], 0)

        handle_button(context)

        self.assertEqual(context['count'], 1)

        handle_button(context)

        self.assertEqual(context['count'], 2)


if __name__ == '__main__':
    logging.getLogger('').setLevel(logging.DEBUG)
    sys.exit(unittest.main())
