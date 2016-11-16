# The Green Button project

Press a bt.tn, multiple times, to foster digital interactions in Cisco Spark and over Twilio. This project implements a software robot (a bot) that turn signals received from the button to meaningful updates for the human beings.

![Architecture](docs/architecture.png)

## Why this project?

With the Green Button project we show evidence of things and people interacting together.

IoT and digital transformation have been buzzwords for a while.
You can find countless presentations and documents on these topics, but what do they really mean to us?

## How to do this?

This is a contribution to the global community of IoT and digital practitioners. You can use it either to demonstrate what is possible today, or even to provide VIP services to selected clients.

This project has been named 'The Green Button' by reference to the corporate color of Dimension Data, where the project was born. It features a physical button, and four different clouds. We selected a standard button from an European company called [bt.tn](https://bt.tn/). The full project, including the software, documentation and reference configuration files,  have been released as an open-source project on GitHub, so that any person can use it and contribute. Cisco Spark provides the interaction back-end. Twilio is used for SMS and phone calls.

## What do you need to run this bot?

* a green button that can trigger a web link, like one of [the smart products from bt.tn](https://bt.tn/shop/) for example
* a server to run the bot, for example a small Cloud Server at the Managed Cloud Platform from Dimension Data
* a token for your bot, provided by [Cisco Spark for Developers](https://developer.ciscospark.com/index.html)
* credentials at [Twilio](https://www.twilio.com) to use their communication services (SMS and voice)
* some instructions and goodwill :-)

Check [detailed instructions](docs/setup.md) for step-by-step deployment of a running installation. Then edit [configuration files](docs/configuration.md) that control the behaviour of each button connected to the system.

## What can this bot really do?

The bot can:
* create Cisco Spark rooms
* add moderators and participants
* upload binary files
* post messages formatted in Markdown
* send SMS over Twilio
* call phone numbers over Twilio and say something

## Where to find additional assistance?

Well, maybe you would like to check [Frequently asked questions](docs/questions.md) and related responses.
Then you can raise an issue at the GitHub project page.

Last but not least, if you are a Dimension Data employee, reach out the Green Force group at Yammer and engage with
other digital practitioners.
