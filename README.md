Cabot Pushbullet Plugin
=====

Based on: https://github.com/lblasc/cabot-alert-slack

This is an alert plugin for the cabot service monitoring tool. It allows you to alert users by sending them notifications through Pushbullet.

## Installation

Enter the cabot virtual environment.
```
    $ pip install git+git://github.com/richshakespeare/cabot-alert-pushbullet.git
    $ foreman stop
```

Edit `conf/*.env`.

```
CABOT_PLUGINS_ENABLED=cabot_alert_pushbullet==0.1
```

Add cabot_alert_pushbullet to the installed apps in settings.py
```
    $ foreman run python manage.py syncdb
    $ foreman start
```
