# Configuration #

Run Uykfe for the first time. Use the `scan-mp3s.py` script (note that you must activate the virtualenv first):
```
> . env/bin/activate
> PYTHONPATH=src python src/uykfe/scan_mp3s.py
ERROR:uykfe.support.config:No configuration at .../.uykferc.
ERROR:uykfe.support.config:Writing default; edit and restart.
```

Edit the configuration file.  This will look like:
```
{
  "lastfm": {
    "secret": "lastfm api secret", 
    "proxy": "optional proxy url"
  }, 
  "mp3_dirs": [
    "add directories", 
    "with mp3 files"
  ], 
  "server": {
    "player": "player name", 
    "port": 9090, 
    "address": "address of squeeze server"
  }
}
```