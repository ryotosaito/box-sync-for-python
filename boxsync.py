# -*- coding: utf-8 -*-

import config
import redirect_server

from boxsdk import OAuth2
import sys
import json
import os

tokens_file = os.environ.get('HOME') + '/.boxsync/tokens.json'

def authenticate():
    if os.path.exists(tokens_file):
        tokens = json.load(open(tokens_file, 'r'))
        oauth = OAuth2(
                client_id=config.client_id,
                client_secret=config.client_secret,
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                )
    else:
        oauth = OAuth2(
                client_id=config.client_id,
                client_secret=config.client_secret,
                )
        auth_url, csrf_token = oauth.get_authorization_url(redirect_server.url)
        print("Access " + auth_url + " and authorize.")
        auth_code = redirect_server.run()
        if auth_code == "":
            print("Aborted.")
            sys.exit(1)
        access_token, refresh_token = oauth.authenticate(auth_code)
        store_tokens(access_token, refresh_token)
    return oauth

def store_tokens(access_token, refresh_token):
    directory = os.path.dirname(tokens_file)
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)
    json.dump({'access_token': access_token, 'refresh_token': refresh_token}, open(tokens_file, 'w'))

def main():
    oauth = authenticate()

if __name__ == '__main__':
    main()
