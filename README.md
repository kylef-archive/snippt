# Snippt

Snippt is an easy to use paste site inspired by [sprunge](http://sprunge.us) and [dpaste](http://dpaste.de).

## Usage

There are two ways to use snippt:

    *Web UI
    *Command-line interface

To use the web UI simply navigate to http://s.drk.sc (or http://snippt.herokuapp.com if that doesn't resolve).

To use the command line tool, use `<command> | curl -F 'paste=<-' http://s.drk.sc`.

### Why not alias?

You can also add that command to your bash/zsh alias file so that you can use it easier:

Simply add `alias snippt="curl -F 'paste=<-' http://s.drk.sc"`. This will allow you to use `<command> | snippt`.

See [here](http://s.drk.sc/man/) for more information.
