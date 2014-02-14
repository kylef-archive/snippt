# Snippt

Snippt is an easy to use paste site inspired by [sprunge](http://sprunge.us) and [dpaste](http://dpaste.de).

## Usage

There are two ways to use snippt:

* Web UI
* Command-line interface

To use the web UI simply navigate to http://s.drk.sc (or http://s.drk.sc if that doesn't resolve).

To use the command line tool, use `<command> | curl -F 'paste=<-' http://s.drk.sc`.

### Why not alias?

You can also add that command to your bash/zsh alias file so that you can use it easier:

Simply add `alias snippt="curl -F 'paste=<-' http://s.drk.sc"`. This will allow you to use `<command> | snippt`.

See [here](http://s.drk.sc/man/) for more information.

### Setting up the development environment

Firstly, you will need to clone the source code. This can be done via:

```bash
$ git clone https://github.com/kylef/snippt
$ cd snippt
```

While there are many ways to set up one’s development environment, following is
a method that uses virtualenv. If you don’t have virtualenv installed, you can
install it via:

```bash
$ pip install virtualenv
```

Virtual environments allow you to work on Python projects which are isolated
from one another so you can use different packages (and package versions) with
different projects.

To create and activate a virtual environment, use the following syntax:

```
$ virtualenv venv
$ source venv/bin/activate
```

To install the development dependencies:

```
$ pip install -r requirements.txt
```

Now, you can setup your local database:

```
$ python manage.py syncdb
```

And then run the development server with the following:

```
$ python manage.py runserver
```

