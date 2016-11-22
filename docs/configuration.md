# How to configure a button?

If you know how to modify a text file, then you can build the button that is perfectly adpated to your specific needs.

The Green Button supports multiple buttons, each of them having a behaviour different from the others. There is one general configuration file for each button, and then one general configuration file for the bot itself.

All configuration files for buttons are placed in the directory `buttons`. You are encouraged to start with one of the buttons provided there, for example `incident` or `request`.

For example, if you want to create a button named `urgent_123` that is derived from `incident`:
* go to the `buttons` directory
* copy `incident.yaml` to `urgent_123.yaml`
* edit `urgent_123.yaml` and adapt messages, files, people, phone numbers, etc.
* save changes and use the button: `http://<server_url>/urgent_123`

If you are an employee of Dimension Data, you can benefit from the back-end server that has been deployed for the Green Button project. Send configuration instructions for your button over e-mail, and we will deploy these for you. Please join the Green Force group in Yammer and get more support.

General configuration is set in `settings.yaml`, in the main directory of the bot.

## Sample configuration file for the button `incident`

In this use case the button triggers interactions with support and delivery team.
We consider that Alice is on provider side, and Bob is on client side.

Alice says to Bob: "You already know managed services from Dimension Data. Here is a new way to engage with us. Press the button when needed, and our teams will interact over a Cisco Spark room and over mobile phones."

1- Bob has a problem, and presses the button.  This creates a room, adds some people from the teams of Alice and of Bob, and pushes some content to it.  Interactions can start asynchronously with chat and files. When people enter the room they can discuss and move forward.

2- If people in the team of Alice are too busy they may not pop up immediately. In that case, Bob presses the button a second time. This sends SMS to Alice, and that action is recorded in the room.

3- A third press on the button  triggers a phone call to Alice, so that she is invited to join the room immediately.

The configuration file for the button `incident` is `buttons/incident.yaml`

```yaml
bt.tn:

  # first press of bt.tn
  #
  - markdown: |
        Green Power has been invoked again
        ==================================

        The [green button](https://d2jaw3pqpetn6l.cloudfront.net/app/uploads/2016/05/27125600/product-images-bttn-normal-green-600x600.jpg) has been pressed, so there is a need for collective action.

        Some context to this event: *Italic*, **bold**, and `monospace`.
        Itemized lists look like this:

          * this one
          * that one
          * the other one

        Unicode is supported. ㋡ Presss the button again to transition to next level of assistance.

    file: files/dashboard.png
    type: "image/png"
    label: "Current status of the server"

  # second press of bt.tn
  #
  - sms:
      - message: "Check Cisco Spark"
      - number: "+352691496401"

    markdown: |
        The button has been pressed again, so you may need more information on our processes.
        Reference information can be found here: [Incident Management](https://en.wikipedia.org/wiki/Incident_management_(ITSM))

        Aside from information already shared in this room, you may want to capture more facts and share these with us.
        Please print and fill the form below. Call our Global Service Center at [+44 12 34 56 78](tel:+44-12-34-56-78) for any real-time assistance you may need. Press the button again to escalate.

    file: files/IncidentReportForm.pdf
    type: "application/pdf"
    label: "Print and fill this form"

  # third press of bt.tn
  #
  - call:
      - number: "+352691496401"
      - say: "Hello, please check Cisco Spark. There is an on-going escalation"

    markdown: |
        A real-time telephone call is taking place right now.

  # fourth press of bt.tn
  #
  - file: files/dimension-data.png
    type: "image/png"
    label: "Build new integrated systems and manage them"

  # fifth press of bt.tn
  #
  - file: files/spark.png
    type: "image/png"
    label: "Cisco Spark brings things and human beings together"


# Cisco Spark settings
#
spark:

    # the name of the Cisco Spark room
    #
    room: "Green Box for Incidents"

    # pre-defined moderators
    #
    moderators:
      - bernard.paques@dimensiondata.com
      - foo.bar@acme.com

    # pre-defined participants
    #
    participants:
      - laurent.mars@company.com
      - expert1@apache.org

    # number of minutes to reset the full cycle of the button
    #
    reset: 360

```

## Sample configuration file for the button `request`

In this use case the button triggers interactions with sales and pre-sales team.
We consider that Alice is on provider side, and Bob is on client side.

Alice says to Bob: as a client manager I would like to be as close to you as possible. Not only to assist you but to be part of your problems and to advise. Each time you want to share an idea of a concern, press the button and this will start a new thinking thread. The actual activity will take place on a Cisco Spark room.

A permanent room is created in Cisco Spark so that Alice and Bob, and their teams, can interact at will.

When Bob pushes the button a notification is sent to the room, and a SMS to Alice. Bob goes to the room and asks a question or submits an idea. If Alice joins the room on SMS, she can either use the chat area, or engage a virtual meeting with Bob, or both.

When Bob pushes the button a second time within some minutes, then a voice call is made to Alice. Then Alice knows that there is an urgent case to handle. She can either move to the room, send a SMS, or find other ways to satisfy Bob. As soon as possible, Alice will join the room, review its content, and resync with Bob appropriately.

After some minutes the system is reset, ready for next transaction. The room preserves context information over time.

The configuration file for the button `request` is `buttons/request.yaml`

```yaml
bt.tn:

  # first press of bt.tn
  #
  - markdown: |
        Question or request thread
        ==========================

        This is the right place to submit a request, or to post a question.
        Attach any document that may be useful for the swift handling of it.

    file: files/question.png
    type: "image/png"
    label: "question thread"

    sms:
      - message: "Check Cisco Spark"
      - number: "+352691496401"

  # second press of bt.tn
  #
  - call:
      - number: "+352691496401"
      - say: "Hello, there is an immediate question from your client. Please check Cisco Spark"

    markdown: |
        A real-time telephone call is taking place right now.

# Cisco Spark settings
#
spark:

    # the name of the Cisco Spark room
    #
    room: "Green Box for Questions"

    # pre-defined moderators
    #
    moderators:
      - bernard.paques@dimensiondata.com
      - foo.bar@acme.com

    # pre-defined participants
    #
    participants:
      - laurent.mars@company.com
      - expert1@apache.org

    # number of minutes to reset the full cycle of the button
    #
    reset: 20
```

## Sample server configuration

The behaviour of the bot is set in a straightforward configuration file named `settings.yaml`, so have a look at it and adapt it to your needs.  If you run a short-lived demonstration, you may probably use the sample file out of the box. For permanent buttons, you should add a private key and use secured tokens.

```yaml
# Cisco Spark settings
#
spark:

    # the token that has been created for this bot should normally be set in
    # the environment but you can override the configuration below
    #
    # CISCO_SPARK_BTTN_BOT: "<token here hkNWEtMJNkODk3ZDZLOGQ0OVGlZWU1NmYtyY>"


# Twilio settings
#
twilio:

    # customer service number
    #
    customer_service_number: "33644606827"

    # the account sid from https://www.twilio.com/console
    #
    # TWILIO_ACCOUNT_SID: "<sid_here>"

    # the authentication token from https://www.twilio.com/console
    #
    # TWILIO_AUTH_TOKEN: "<token_here>"


# server settings
#
server:

    # the port from which this bot is getting requests from the internet
    #
    port: 8080

    # the url that is used to access this server remotely, e.g. with ngrok
    #
    #url: "http://b2db306e.ngrok.io/"

    # default button id if no information is provided over the wire
    #
    default: incident

    # if you set a secret, use security tokens instead of button names in URL
    #
    #key: "a long and difficult pass phrase"

```

The default `settings.yaml` is suitable only for short-lived demonstrations. For any other usage, you should edit it, uncomment the `key:` line and add a long and random string.

For example, change:

```yaml
    #key: "a long and difficult pass phrase"
```

to:

```yaml
    key: 'cmVxdWVzdC1kZWxldGU6L292TlJRZTJaNmIxcW4rUEZLS1lpUT09'
```

