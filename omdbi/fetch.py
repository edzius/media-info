
import os
import logging
import omdb
from . import cache


def read_key_config(file_name):
    try:
        fh = open(file_name, 'r')
    except Exception as e:
        logging.debug("Cannot read key file '%s': %s", file_name, e)
        return ''

    key = fh.readline() or ''
    fh.close()
    return key.strip()


def read_key_env(env_name):
    try:
        return os.environ[env_name]
    except Exception as e:
        logging.debug("Cannot get key env '%s': %s", env_name, e)
        return ''


key = read_key_env('OMDB_KEY') or read_key_config('./omdb-key') or read_key_config('~/.config/guessit/omdb-key') or read_key_config('/etc/omdb-key')
if not key:
    logging.error("No OMDB key configured")
omdb.set_default('apikey', key or '')


def verify(data):
    if not data:
        return False

    if 'Response' in data and data['Response'] != "True":
        return False

    if 'response' in data and data['response'] != "True":
        return False

    return True


def receive(title, year=None, kind=None, season=None, episode=None):
    name = ' '.join([str(title),
                     str(year) if year else 'year0',
                     str(kind) if kind else 'video',
                     str('S%s' % season) if season else '',
                     str('E%s' % episode) if episode else '']).strip()

    try:
        data = cache.get(name)
        if data:
            logging.debug("OMDB cache '%s' found", name)
            return data

        if cache.ignored(name):
            logging.info("OMDB fetch '%s' ignored", name)
            return data

        if not key:
            logging.warning("OMDB fetch '%s' skipped; KEY not set", name)
            return data

        logging.debug("OMDB fetch '%s' new data", name)
        data = omdb.get(title=title,year=year,media_type=kind,season=season,episode=episode)

        if verify(data):
            logging.debug("OMDB fetch '%s' success", name)
            cache.set(data, name)
            return data

        cache.miss(name)
        logging.warning("OMDB fetch '%s' failed; response: %s", name, data)
    except Exception as e:
        logging.warning("OMDB fetch '%s' failed: %s", name, e)


def inspect(title, year=None, kind=None, season=None, episode=None):
    if not season and not episode:
        data = receive(title, year, kind or "movie", season, episode)
    else:
        data = receive(title, year, "series")
        if data and season:
            data['series'] = receive(title, year, "series", season)
            if 'series' in data and data['series'] and episode:
                if 'episodes' in data['series'] and len(data['series']['episodes']) >= int(episode):
                    data['show'] = data['series']['episodes'][int(episode)]

    return data
