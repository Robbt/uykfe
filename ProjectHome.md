_When you have many mp3 files it can be hard to know what to listen to.  You might have some favourite artists, but be unsure who else sounds similar.  Uykfe solves this problem - it starts from a tune you like and plays similar music, using tags from Last.fm as a guide.  It's also a useful way of listening to "random" music without sudden changes in style - your mp3s become a personal radio station._

This is a simpler, lighter, faster, follow-up to [Uykfd](https://code.google.com/p/uykfd/).  A set of Python 3.2 scripts that:
  * Scans your mp3 directories, reading ID3 tags
  * Uses the Last.fm API to "normalize" artist names (optional)
  * Uses the Last.fm API to read tags for artists
  * Joins artists according to the tag weights
  * **Constructs playlists based on the Last.fm tags**
  * **Controls your SqueezePlayer based on the Last.fm tags**
  * Dumps the graph to a GEXF format file for import into [gephi](http://gephi.org/)

![http://cdn.last.fm/flatness/badges/lastfm_red_small.gif](http://cdn.last.fm/flatness/badges/lastfm_red_small.gif) - powered by data from [Last.fm](http://last.fm).  This project is (c) Andrew Cooke, 2011.  Released under the BSD licence.

For more background see [this blog post](http://www.acooke.org/cute/UsingLastf0.html).

# Documentation #

  * [Requirements](Requirements.md)
  * [Installation](Installation.md)
  * [Configuration](Configuration.md)
  * [DatabasePreparation](DatabasePreparation.md)
  * [UsingUykfe](UsingUykfe.md)

# Support #

You can comment on Wiki pages, but I can't work how to be alerted of that, so you would be better emailing me - andrew@acooke.org.