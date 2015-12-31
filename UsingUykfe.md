First, as always, activate the virtualenv:
```
> . env/bin/activate
```

# Playlist Generation #

Playlists can be generated using the `playlist.py` script:
```
> PYTHONPATH=src python src/uykfe/playlists.py -h

usage: playlist.py [-h] [-a ARTIST] [-t TRACK] N

Print a playlist to stdout

positional arguments:
  N                     the number of entries

optional arguments:
  -h, --help            show this help message and exit
  -a ARTIST, --artist ARTIST
                        starting artist
  -t TRACK, --track TRACK
                        starting track
```

# SqueezeCenter Control #

Uykfe can monitor your SqueezeCenter playlist.  Whenever it detects that you are listening to the _last_ track of a playlist, it will append an extra, related track.  This gives "infinite" playlists of related music.  If no playlist is present Uykfe will provide a random starting track (this makes the "clear playlist" button work as "start playlist from new random location").

To enable this, run the `play.py` script:

```
> PYTHONPATH=src python src/uykfe/play.py
```