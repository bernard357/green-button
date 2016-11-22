#!/usr/bin/env python

from hook import configure, load_buttons, generate_tokens

settings = configure('settings.yaml')
buttons = load_buttons(settings)

if 'key' in settings['server']:
    tokens = generate_tokens(settings, buttons.keys())
    for key in tokens:
        print('{}: {}'.format(key, tokens[key]))

else:
    print('Add a secret key to settings.yaml if you want security')
    print('No security token has been generated')
