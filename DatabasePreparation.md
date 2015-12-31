# Database Preparation #

First, as always, activate the virtualenv:
```
> . env/bin/activate
```

Next, run the scripts, in order:
  * **` scan_mp3s.py `** - this creates the database and adds all tracks, reading the ID3 tags
  * **` identify_artists.py `** - this tries to identify popular artist names in the Last.fm database that correspond to your ID3 names (use the command line argument `-i` to skip connecting to Last.fm and re-use your existing artist names)
  * **` tag_artists.py `** - this downloads tags for each artist from Last.fm
  * **` link_artists.py `** - this connects artists with similar tags

Note that some of these may take hours to run, depending on how much music you have and how fast your internet connection is.

To run a script you will need to set the PYTHONPATH correctly.  You might type something like:
```
> PYTHONPATH=src python src/uykfe/scan_mp3s.py 
```

After each stage you can save the database file `uykfe.db`.  You can also stop (Crtl-C) and restart any script (but you cannot run scripts out of order).