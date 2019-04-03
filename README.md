# Media info service

Python based REST service aggregating few mechanisms that tries to extract as much information as possible from video file names.

## Starting

Clone sources from git repository

```shell
    $ git clone https://github.com/edzius/media-info.git
    $ cd media-info
```

Install service dependencies

```shell
    $ pip install omdb guessit flask-restful flask-cors Flask
```

Then run guessit rest API using main module.

```shell
    $ python mis.py
```

Command line options

```
usage: mis.py [-h] [-l LISTENING_ADRESS] [-p LISTENING_PORT]

optional arguments:
  -h, --help            show this help message and exit
  -l LISTENING_ADRESS, --listening-adress LISTENING_ADRESS
                        Listening IP Adress of the HTTP Server.
  -p LISTENING_PORT, --listening-port LISTENING_PORT
```

## Usage

### Setup OMDB key

Required if used with OMDB. Key can be retrieved by submiting request in http://www.omdbapi.com/

OMDB key can be retrieved from:
* OMDB_KEY -- environment variable
* ./omdb-key
* ~/.config/guessit/omdb-key
* /etc/omdb-key

### Extract file name info

Inspects file name and returns detected video file information.

HTTP GET request: `http://localhost:5000/file/?filename=The.100.S05E01.PROPER.HDTV.x264-CRAVERS.mkv`
Params:
* filename -- name of inspecting file or file path.
* options -- as-is guessit options

Response format same as defined in guessit documentation:
https://github.com/guessit-io/guessit#guessit

### Retrieve OMDB movie info

Looks OMDB for requestd movie information.

HTTP GET request: `http://localhost:5000/omdb/?title=Westworld`
Params:
* title -- title to look for
* season -- season number when looking for series (implied type "series")
* episode -- episode number when looking for series episode (implied type "series")
* type -- video type refinement ("movie", "series", "episode")
* year -- video release year refinement

Response similar to one defined in omdb API documentation:
http://www.omdbapi.com/#parameters

### Retrieve file movie info

Inspects file name and returns movie information from OMDB.

HTTP GET request: `http://localhost:5000/?filename=The.100.S05E01.PROPER.HDTV.x264-CRAVERS.mkv`
Params:
* filename -- name of inspecting file or file path.
* options -- as-is guessit options

Response similar to one defined in omdb API documentation:
http://www.omdbapi.com/#parameters
