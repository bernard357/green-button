# Frequently asked questions

## About project governance

### Where is this project coming from?

The Green Button project is an initiative from European teams of Dimension Data. It is supported by experts in collaboration systems and in cloud architecture.

### Is this software available to anyone?

Yes. The software and the documentation have been open-sourced from the outset, so that it can be useful to the global community of IoT and of digital practioners. The Green Button project is based on the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

### Do you accept contributions to this project?

Yes. There are multiple ways for end-users and for non-developers to contribute to this project. For example, if you hit an issue, please report it at GitHub. This is where we track issues and report on corrective actions.

And if you know [how to clone a GitHub project](https://help.github.com/articles/cloning-a-repository/), we are happy to consider [pull requests](https://help.github.com/articles/about-pull-requests/) with your modifications. This is the best approach to submit additional reference configuration files, or updates of the documentation, or even evolutions of the python code.

## About project design

### What is needed to deploy a button?

* a green button that can trigger a web link, like one of [the smart products from bt.tn](https://bt.tn/shop/) for example
* a server to run the bot, for example a small Cloud Server at the [Managed Cloud Platform](http://www.dimensiondata.com/Global/Solutions/Cloud/) from Dimension Data
* a token for your bot, provided by [Cisco Spark for Developers](https://developer.ciscospark.com/index.html)
* credentials at [Twilio](https://www.twilio.com) to use their communication services (SMS and voice)
* some [instructions](setup.md) and goodwill :-)

Please note that it is not required to use cloud services from Dimension Data. Instructions to install the bot at any Ubuntu box are also provided. On the other hand, if you have MCP credentials, then you can deploy the bot at more than 15 data centres world-wide, in 10 minutes. Check [the orchestration file](../fittings.yaml) for more details.

If you are a Dimension Data employee, you can benefit directly from the back-end that has been put in place for the project. Acquire a connected button and contact the Green Force group in Yammer.

### Can the bot support multiple buttons?

Yes, a single web server can handle many buttons. Each button has its own separate configuration file, and is given a separate
web address. So with this bot you can spread dozens of buttons and customize the behaviour of each of them separately from the others.

### Has information security been integrated in the design?

Yes. Actions triggered by remote buttons are protected and authenticated by security tokens. Check and  [the setup page](setup.md) and [the configuration page](configuration.md) for more details.

## About project deployment

### How to install the full system?

Use [detailed instructions](setup.md) that explain what you have to do step by step.

We are making the setup as easy as possible for Dimension Data employees, thanks to the back-end that has been put in place for the project. All you really need is a physical button. For the rest, contact the Green Force group in Yammer.

### Is it required to know python?

Fortunately not. The software robot uses separate configuration files that can be modified at will.

Each button has its own configuration file in the directory `buttons`. The system is provided with
two sample files named `buttons\incident.yaml` and `buttons\request.yaml`.
You can modify these files, or create a separate file for a new button.

Check the configuration file `settings.yaml` to specify general parameters, such the port used by the web server, etc.

### Is it easy to configure a button?

Yes, since the behaviour of each button is described in a separate configuration file.
Some [examples](../buttons) are provided so that you have something to start with.

Configuration files are plain text files, where you describe in sequence what to do
on first push of the button, on second push, etc.

The Green Button can handle following actions:
* create Cisco Spark rooms
* add moderators and participants
* upload binary files
* post messages formatted in Markdown
* send SMS over Twilio
* call phone numbers over Twilio and say something

Ready to go? Check [the configuration page](configuration.md) for more details

## About troubleshooting

### How to check the web interface?

The bare web server can be checked with the `/ping` token.
For example, if the bot runs on a server that has been given the address `168.123.45.67`, the test link would be:

`http://168.123.45.67/ping`

The browser should display `pong` as a successful response from the server.

For actual button links you will connect to the server over SSH and list security tokens, for example:

```bash
$ python tokens.py
incident: aW5jaWRlbnQ6WHFUWXBoc0tvV2toMkdTM1dQTHpIZz09
incident-call: aW5jaWRlbnQtY2FsbDpuQmNETks2a1I3NnpITGNRQ1pKNGpRPT0=
incident-delete: aW5jaWRlbnQtZGVsZXRlOldWSGk4anBsZ1ZUUlhFSDVHejJrMUE9PQ==
request: cmVxdWVzdDpGT2krUDJpM0lJY0hEbFYxZ2R6UGZ3PT0=
request-call: cmVxdWVzdC1jYWxsOlFwZkpqNVFvbTNjemVmOU8zaU5DWlE9PQ==
request-delete: cmVxdWVzdC1kZWxldGU6L292TlJRZTJaNmIxcW4rUEZLS1lpUT09
```

If the bot runs on the server at the address `168.123.45.67`, then the link given to the button `incident` would be:

`http://168.123.45.67/aW5jaWRlbnQ6WHFUWXBoc0tvV2toMkdTM1dQTHpIZz09`

You can put that link in a browser to simulate the push of the button, and to check the response displayed by the server:

`OK 1'

If you reload the page in the browser this will be considered a second push:

`OK 2'

### How to run the server interactively?

Go to the server over SSH, and launch the server from the command-line:

```bash
$ python hook.py
Bottle v0.12.10 server starting up (using AutoServer())...
Listening on http://0.0.0.0:8080/
Hit Ctrl-C to quit.
```

If the server cannot be started, ensure that no service is already doing the job in the background:

`sudo stop bttn_spark`

Once the server has been started, then read previous question: "How to check the web interface?" You will simulate a button push, but within a browser, and see how the server is reacting. If an error occurs it should be reported in the server window.

### How to read logs from the bot running as a service?

If plumbery has been used for the deployment of the server then the bot is running as a service. Check logs generated by the service with following commands:

```bash
$ cd /var/log/upstart
$ sudo cat bttn_spark.log
```

