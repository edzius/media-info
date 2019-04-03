
import os
import json
import logging

OMDB_CACHE_INDEX = "/var/run/omdb/fetch.index"
OMDB_CACHE_DIR = "/var/run/omdb/fetch-cache"

omdb_index = None
omdb_ignore = None

def init():
    if os.path.exists(OMDB_CACHE_DIR):
        return
    os.makedirs(OMDB_CACHE_DIR)

def load():
    global omdb_index
    global omdb_ignore

    if omdb_index:
        return

    omdb_index = {}
    omdb_ignore = {}
    try:
        fp = open(OMDB_CACHE_INDEX)
    except:
        return

    for line in fp:
        line = line.strip()
        if not line:
            logging.warning("Empty omdb cache index line")
            continue
        mid, _, mname = line.partition('=')
        if not mid:
            logging.warning("Invalid omdb cache index line: %s", line)
            continue

        if mid == 'X':
            omdb_ignore[mname.strip()] = True
        else:
            omdb_index[mname.strip()] = mid.strip()

    fp.close()

def get(name):
    global omdb_index

    load()

    name = name.strip()
    if name not in omdb_index:
        logging.debug("Cache get '%s' failed - not in index", name)
        return

    mid = omdb_index[name].strip()

    init()
    try:
        fp = open("%s/%s" % (OMDB_CACHE_DIR, mid,))
    except Exception as e:
        logging.error("Failed omdb cache get '%s' (%s): %s", name, mid, e)
        return
    data = json.load(fp)
    fp.close()
    return data

def set(data, name):
    global omdb_index

    if not data:
        return

    mtitle = ''
    if 'title' in data:
        mtitle = data['title']
    if 'season' in data:
        mtitle = "%s-%s" % (mtitle, data['season'],)

    mid = ''
    if 'imdb_id' in data:
        mid = data['imdb_id']
    elif 'episodes' in data:
        if 'imdb_id' in data['episodes'][0]:
            mid = data['episodes'][0]['imdb_id']
    if not mid:
        mid = mtitle

    mname = name or mtitle

    mid = mid.strip()
    mname = mname.strip()
    if mname in omdb_index:
        logging.debug("Cache set '%s' skipped - already in index", mname)
        return

    init()
    try:
        fp = open("%s/%s" % (OMDB_CACHE_DIR, mid,), "w")
    except Exception as e:
        logging.error("Failed omdb cache set '%s' (%s): %s", mname, mid, e)
        return

    json.dump(data, fp)
    fp.close()

    try:
        fp = open(OMDB_CACHE_INDEX, "a")
    except Exception as e:
        logging.error("Failed omdb cache index update '%s' (%s): %s", mname, mid, e)
        return

    fp.write("%s=%s\n" % (mid, mname,))
    fp.close()

    omdb_index[mname] = mid

def miss(name):
    global omdb_ignore

    if not name:
        return

    name = name.strip()
    if name in omdb_ignore:
        logging.debug("Ignore set '%s' skipped - already in ignore index", name)
        return

    try:
        fp = open(OMDB_CACHE_INDEX, "a")
    except Exception as e:
        logging.error("Failed omdb ignore index update '%s': %s", name, e)
        return

    fp.write("%s=%s\n" % ('X', name,))
    fp.close()

    omdb_ignore[name] = True

def ignored(name):
    global omdb_ignore

    if not name:
        return False

    return name in omdb_ignore

def convert(data):
    if not data:
        return
    return json.loads(data)
