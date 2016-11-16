# Frequently asked questions

## What do you need to run this bot?

* a green button that can trigger a web link, like one of [the smart products from bt.tn](https://bt.tn/shop/) for example
* a server to run the bot, for example a small Cloud Server at the Managed Cloud Platform from Dimension Data
* a token for your bot, provided by [Cisco Spark for Developers](https://developer.ciscospark.com/index.html)
* credentials at [Twilio](https://www.twilio.com) to use their communication services (SMS and voice)
* some [instructions](setup.md) and goodwill :-)

## Can the bot support multiple buttons?

Yes, a single web server can handle many buttons. Each button has its own separate configuration file, and is given a separate
web address. So with this bot you can spread dozens of buttons and customize the behaviour of each of them.

## What can this bot really do?

The bot can:
* create Cisco Spark rooms
* add moderators and participants
* upload binary files
* post messages formatted in Markdown
* send SMS over Twilio
* call phone numbers over Twilio and say something

## How to install the full system?

Use [detailed instructions](setup.md) that explain what you have to do step by step.

You do not need to be a software developer to use this bot. The behaviour of the bot is set in a straightforward configuration file named `settings.yaml`, so have a look at it and adapt it to your needs.
The sample configuration file below provides a rather good idea of what this bot is capable of.

## Is it required to know python?

Fortunately not. The software robot uses separate configuration files that you can modify at will.

Each button has its own configuration file in the directory `buttons`. The system is provided with
two sample files named `buttons\incident.yaml` and `buttons\request.yaml`.
You can modify these files, or create a separate file for a new button.

Check the configuration file `settings.yaml` to specify general parameters, such the port used by the web server, etc.

## Where is this project coming from?

The Green Button project is an initiative from European teams of Dimension Data. It is supported by experts in collaboration systems and in cloud architecture.

## Is this software available to anyone?

Yes. The software and the documentation have been open-sourced from the outset, so that it can be useful to the global community of IoT and of digital practioners. The Green Button project is based on the Apache Licence.

## Do you accept contributions to this project?

Yes. There are multiple ways for end-users and for non-developers to contribute to this project. For example, if you hit an issue, please report it at GitHub. This is where we track issues and report on corrective actions.

And if you know how to clone a GitHub project, we are happy to consider pull requests with your modifications. This is the best approach to submit additional reference configuration files, or updates of the documentation, or even enhancements of the python code.
