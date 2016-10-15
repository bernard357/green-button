# bt.tn-spark
Press a bt.tn, multiple times, to foster digital interactions in Cisco Spark. This project implements a software robot (a bot) that turn signals received from the button to meaningful updates for the human beings.

![Architecture](docs/architecture.png)

## What do you need to run this bot?

* a green button that can trigger a web link, like one of [the smart products from bt.tn](https://bt.tn/shop/) for example
* a server to run the bot, for example a small Cloud Server at the Managed Cloud Platform from Dimension Data
* a token for your bot, provided by [Cisco Spark for Developers](https://developer.ciscospark.com/index.html)
* some instructions and goodwill :-)

## What can this bot really do?

The sample configuration file below provides a rather good idea of what this bot is capable of.

```yaml
# the port from which this bot is getting requests from the internet
#
port: 8080

# the name of the Cisco Spark room handled by this bot
#
room: "Green Forge"

# the token that has been created for this bot should normally be set in
# the environment but you can override the configuration below
#
# CISCO_SPARK_BTTN_BOT: "YWM2OEG4OGItNTQ5YS00MDU2LThkNWEtMJNkODk3ZDZLOGQ0OVGlZWU1NmYtZWyY"

# the mail address of the first moderator should normally be set in
# the environment but you can override the configuration below
#
# CISCO_SPARK_BTTN_MAN: "foo.bar@acme.com"

# the sequence of responses given to each button press
#
bt.tn:

  # first press of bt.tn
  #
  - markdown: |
        Green Power has been invoked again
        ==================================

        The [green button](https://d2jaw3pqpetn6l.cloudfront.net/app/uploads/2016/05/27125600/product-images-bttn-normal-green-600x600.jpg) has been pressed, so there is a need for urgent action.

        Some context to this event: *Italic*, **bold**, and `monospace`.
        Itemized lists look like this:

          * this one
          * that one
          * the other one

        Unicode is supported. ㋡

        And [Incident Management](https://en.wikipedia.org/wiki/Incident_management_(ITSM)) too.

        Call Global Service Center at [+44 12 34 56 78](tel:+44-12-34-56-78) if people are late to join this room. We will continue to provide information so stay tuned.


  # second press of bt.tn
  #
  - file: files/IncidentReportForm.pdf
    type: "application/pdf"
    label: "Print and fill this report"

  # third press of bt.tn
  #
  - file: files/bt.tn.png
    type: "image/png"
    label: "European buttons that rock"

  # fourth press of bt.tn
  #
  - file: files/spark.png
    type: "image/png"
    label: "Cisco Spark brings things and human beings together"

  # fifth press of bt.tn
  #
  - file: files/dimension-data.png
    type: "image/png"
    label: "Build new integrated systems and manage them"

```

## Ok, tell me the sequence of operations

### Step 1. Get a physical button that can generate web requests.

I acquired a large green button from bt.tn,
and then paired it with my smartphone over private WiFi.

![1-bt.tn](docs/1-bt.tn.png)

### Step 2. Declare a bot at Cisco Spark for Developer, then save the precious token that is given in return.

I saved this token as `CISCO_SPARK_BTTN_BOT` in the environment of my workstation, so that it is not in
any configuration file. To align with the machines, there is also a need to put some human e-mail address
in `CISCO_PARK_BTTN_MAN`. The bot will promote this human to a moderator role of the target Spark room.

![2-cisco](docs/2-cisco.png)

### Step 3. Get and configure a small public web server.

If you have some MCP credentials, you may want to clone this GitHub
repository on your workstation, and then run plumbery: `python -m plumbery fittings.yaml deploy`

![3-plumbery](docs/3-plumbery.png)

Else if you have to go the manual way, then first secure a Ubuntu machine and consider following steps.

```bash
$ sudo apt-get install -y ntp git python-pip
$ cd /home/ubuntu/
$ git clone https://github.com/bernard357/bt.tn-spark.git
$ cd bt.tn-spark/
$ pip install -r requirements.txt
$ export CISCO_SPARK_BTTN_BOT="<whatever_your_token_is>"
$ export CISCO_SPARK_BTTN_MAN="<email_address_of_room_moderator>"
$ python hook.py
```

### Step 4. Activate the bot.

If you have used plumbery at the previous step, just follow instructions on screen.
Connect to your server over SSH in a terminal window, then run the server in the foreground:
`python hook.py` Log messages are pretty comprehensive, so it should easy to monitor how things are going.

![4-bot](docs/4-bot.png)

### Step 5. Configure the button to use the public IP address of the web server.

For this I used the straightforward console provided by bt.tn. It took me about 1 minute or 2.

![5-my.bt.tn](docs/5-my.bt.tn.png)


### Step 6. Now launch Cisco Spark and press the button.

After some seconds you should get a new room on screen, and a first update in Markdown.
The button should return to quiet state (no led), and the log of the server should report that everything is ok.

![6-spark](docs/6-spark.png)

Congratulations! Hit the button again, to demonstrate how the bot can cleverly manage multiple states.

![7-pushes](docs/7-pushes.png)

## Feedback: Help! This is not working as expected

Of course, it would have been too easy otherwise. As an engineer, you expect some brain activity and creativity, right? Please check in sequence the transmission chain to spot the culprit, and fix it.

## Feedback: This does provide a comprehensive demonstration in 25 minutes or less. Awesome

Good news :-)  After the demonstration, destroy cloud resources with: `python -m plumbery fittings.yaml destroy` and bring the precious button with you.

We are glad to receive contributions and comments via GitHub. Thanks for cloning this repository and for the submission of your next pull request.
