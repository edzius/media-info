#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import logging
from logging.handlers import RotatingFileHandler
from argparse import ArgumentParser

from flask import Flask, make_response
from flask_cors import CORS  # pylint:disable=no-name-in-module,import-error
from flask_restful import Api, Resource, reqparse

import guessit
from guessit.jsonutils import GuessitEncoder

import local
import omdbi


class MisOmdb(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('title', action='store', required=True, help='Title to search', location=location)
        parser.add_argument('season', action='store', help='Season info', location=location)
        parser.add_argument('episode', action='store', help='Episode info', location=location)
        parser.add_argument('type', action='store', help='Video type', location=location)
        parser.add_argument('year', action='store', help='Video year', location=location)
        args = parser.parse_args()

        return omdbi.inspect(args.title, args.year, args.type, args.season, args.episode)

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


class MisFile(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='store', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()

        return guessit.guessit(args.filename, args.options)

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


def take(obj, key):
    if key in obj:
        return obj[key]
    return None


def want(guess, title=None):
    if not guess:
        return
    return omdbi.inspect(title or take(guess, 'title'),
                         take(guess, 'year'),
                         take(guess, 'type'),
                         take(guess, 'season'),
                         take(guess, 'episode'))


class MisInfo(Resource):
    def _impl(self, location):
        parser = reqparse.RequestParser()
        parser.add_argument('filename', action='store', required=True, help='Filename to parse', location=location)
        parser.add_argument('options', action='store', help='Guessit options', location=location)
        args = parser.parse_args()

        guess = guessit.guessit(args.filename, args.options)
        value = want(guess)
        if value:
            return value
        guessLocal = local.inspect(args.filename)
        value = want(guessLocal)
        if value:
            return value

        value = want(guess, local.modContractionsGeneric(guess['title'])) or \
                want(guess, local.modContractionsWere(guess['title'])) or \
                want(guess, local.modPossesiveSingular(guess['title'])) or \
                want(guess, local.modPossesivePlural(guess['title']))
        if value:
            return value

        if guessLocal:
            value = want(guessLocal, local.modContractionsGeneric(guess['title'])) or \
                    want(guessLocal, local.modContractionsWere(guess['title'])) or \
                    want(guessLocal, local.modPossesiveSingular(guess['title'])) or \
                    want(guessLocal, local.modPossesivePlural(guess['title']))
        if value:
            return value

        guessFile = local.inspect(args.filename, true)
        value = want(guessFile)
        if value:
            return value

        if guessFile:
            value = want(guessFile, local.modContractionsGeneric(guess['title'])) or \
                    want(guessFile, local.modContractionsWere(guess['title'])) or \
                    want(guessFile, local.modPossesiveSingular(guess['title'])) or \
                    want(guessFile, local.modPossesivePlural(guess['title']))
        if value:
            return value

        if guessLocal and guessLocal['type'] == 'episode':
            value = omdbi.inspect(take(guess, 'title'),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(take(guessLocal, 'title'),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modContractionsGeneric(take(guess, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modContractionsGeneric(take(guessLocal, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modContractionsWere(take(guess, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modContractionsWere(take(guessLocal, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modPossesiveSingular(take(guess, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modPossesiveSingular(take(guessLocal, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modPossesivePlural(take(guess, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode')) or \
                    omdbi.inspect(local.modPossesivePlural(take(guessLocal, 'title')),
                                  take(guess, 'year'),
                                  take(guessLocal, 'type'),
                                  take(guessLocal, 'season'),
                                  take(guessLocal, 'episode'))

        return value

    def get(self):
        return self._impl('args')

    def post(self):
        return self._impl('json')


opts = ArgumentParser()

opts.add_argument('-l', '--listening-adress', dest='listening_adress', default='0.0.0.0',
                  help='Listening IP Adress of the HTTP Server.')
opts.add_argument('-p', '--listening-port', dest='listening_port', default=None,
                  help='Listening TCP Port of the HTTP Server.')

parsed_opts = opts.parse_args()

app = Flask('MIS')
CORS(app)
api = Api(app)
app.debug = os.environ.get('DEBUG', False)

@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=GuessitEncoder, ensure_ascii=False), code)
    resp.headers.extend(headers or {})
    return resp

if not app.debug:
    handler = RotatingFileHandler('guessit-rest.log', maxBytes=5 * 1024 * 1024, backupCount=5)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

api.add_resource(MisInfo, '/')
api.add_resource(MisFile, '/file/')
api.add_resource(MisOmdb, '/omdb/')

app.run(host=parsed_opts.listening_adress, port=parsed_opts.listening_port)
