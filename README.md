# The Green Button project

Press a [bt.tn](https://bt.tn), multiple times, to foster digital interactions in [Cisco Spark](https://www.ciscospark.com/) and over [Twilio](https://www.twilio.com). This project implements a software robot (a [bot](https://en.wikipedia.org/wiki/Internet_bot)) that turn signals received from the button to meaningful updates for the human beings.

![Architecture](docs/media/architecture.png)

## Why this project?

With the Green Button project we show evidence of things and people interacting together.

IoT and digital transformation have been buzzwords for a while.
You can find countless presentations and documents on these topics, but what do they really mean to us?

This is a contribution to the global community of IoT and digital practitioners. You can use it either to demonstrate what is possible today, or even to provide VIP services to selected clients. The Green Button project is ruled by the [Apache License](https://www.apache.org/licenses/LICENSE-2.0).

This is an open source project, meaning that we rely on volunteers to show up and to contribute. [Contributions and feedback](docs/contributing.md) are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

## How is this done?

The system has one or several physical buttons, and four different clouds. We selected a standard button from an European company called [bt.tn](https://bt.tn/). The full project, including the software, documentation and reference configuration files,  have been released as an open-source project on GitHub, so that any person can use it and contribute. [Cisco Spark](https://www.ciscospark.com/) provides the interaction back-end. [Twilio](https://www.twilio.com) is used for SMS and phone calls.

This project has been named 'The Green Button' by reference to the corporate color of Dimension Data, where the project was born. As you can expect, the deployment of the bot has been fully [orchestrated](fittings.yaml) on the [Managed Cloud Platform](http://www.dimensiondata.com/Global/Solutions/Cloud/) from Dimension Data. So, if you have MCP credentials, you can deploy the bot at more than 15 data centres world-wide, in 10 minutes. Please note that it is not required to use cloud services from Dimension Data. Instructions to install the bot at any Ubuntu box are also provided.

## What is needed to deploy a button?

* a green button that can trigger a web link, like one of [the smart products from bt.tn](https://bt.tn/shop/) for example
* a server to run the bot, for example a small Cloud Server at the [Managed Cloud Platform](http://www.dimensiondata.com/Global/Solutions/Cloud/) from Dimension Data
* a token for your bot, provided by [Cisco Spark for Developers](https://developer.ciscospark.com/index.html)
* credentials at [Twilio](https://www.twilio.com) to use their communication services (SMS and voice)
* some instructions and goodwill :-)

Check [detailed instructions](docs/setup.md) for step-by-step deployment of a running installation. Then edit [configuration files](docs/configuration.md) that control the behaviour of each button connected to the system.

If you are a Dimension Data employee, then you can benefit from the back-end that has been put in place for the project. Acquire a connected button and contact the Green Force group in Yammer.

## Is it easy to configure a button?

Yes, since the behaviour of each button is described in a separate configuration file.
Some [examples](buttons) are provided so that you have something to start with.

Configuration files are plain text files, where you describe in sequence what to do
on first push of the button, on second push, etc.

The Green Button can handle following actions:
* create Cisco Spark rooms
* add moderators and participants
* upload binary files
* post messages formatted in Markdown
* send SMS over Twilio
* call phone numbers over Twilio and say something

Ready to go? Check [the configuration page](docs/configuration.md) for more details

## Where to find additional assistance?

Well, maybe you would like to check [Frequently asked questions](docs/questions.md) and related responses.
Then you can [raise an issue at the GitHub project page](https://github.com/bernard357/bt.tn-spark/issues) and get support from the project team.

If you are a Dimension Data employee, reach out the Green Force group at Yammer and engage with
other digital practitioners.

## How would you like to contribute?

We want you to feel as comfortable as possible with this project, whatever your skills are.
Here are some ways to contribute:

* [use it for yourself](docs/contributing.md#how-to-use-this-project-for-yourself)
* [communicate about the project](docs/contributing.md#how-to-communicate-about-the-project)
* [submit feedback](docs/contributing.md#how-to-submit-feedback)
* [report a bug](docs/contributing.md#how-to-report-a-bug)
* [write or fix documentation](docs/contributing.md#how-to-improve-the-documentation)
* [fix a bug or an issue](docs/contributing.md#how-to-fix-a-bug)
* [implement some feature](docs/contributing.md#how-to-implement-new-features)

Every [contribution and feedback](docs/contributing.md) matters, so thank you for your efforts.


