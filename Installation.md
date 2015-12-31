# Installation #

To run Uykfe:

  * Make sure that you are running Python 3.2 or later (see http://www.python.org)
  * Make sure that you have virtualenv3 installed (see http://pypi.python.org/pypi/virtualenv3/1.3.4.2)
  * Register for the [Last.fm API](http://www.last.fm/api/intro)
  * Download the [source](http://code.google.com/p/uykfe/source/checkout)
```
> svn checkout http://code.google.com/p/uykfe/source/checkout uykfe
```
  * In the top directory that you download, run **`setup-env.sh`** to create the virtualenv and install any packages
```
> cd uykfe
> ./setup-env.sh
```

**Important:**

Whenever you use Uykfe you must first enable the virtualenv installation (this is a separate Python installation that Uykfe uses so that it doesn't change the main Python install on your computer).

To do this you must remember to run
```
> . env/bin/activate
```