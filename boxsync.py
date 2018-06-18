# -*- coding: utf-8 -*-

import config
import redirect_server

from boxsdk import OAuth2, Client
import math
import sys
import json
import os

_tokens_file = os.environ.get('HOME') + '/.boxsync/tokens.json'
_sync_dir = os.environ.get('HOME') + '/Box Sync'

def authenticate():
    if os.path.exists(_tokens_file):
        tokens = json.load(open(_tokens_file, 'r'))
        oauth = OAuth2(
                client_id=config.client_id,
                client_secret=config.client_secret,
                store_tokens=store_tokens,
                access_token=tokens['access_token'],
                refresh_token=tokens['refresh_token'],
                )
    else:
        oauth = OAuth2(
                client_id=config.client_id,
                client_secret=config.client_secret,
                store_tokens=store_tokens,
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
    directory = os.path.dirname(_tokens_file)
    mkdir(directory)
    json.dump({'access_token': access_token, 'refresh_token': refresh_token}, open(_tokens_file, 'w'))

def mkdir(dir_name):
    try:
        os.stat(dir_name)
    except:
        os.mkdir(dir_name)

def get_tree(folder_id):
    tree = {}
    folder = client.folder(folder_id).get()
    for page in range(math.ceil(int(folder.item_collection['total_count'])/1000)):
        for item in folder.get_items(limit=1000, offset=page*1000, fields=['type', 'id', 'name', 'sync_state', 'modified_at']):
            if item.type == 'folder' and item.sync_state in ['synced', 'partially_synced']:
                tree[item.name] = get_tree(item.id)
            elif item.type == 'file':
                tree[item.name] = item
    return tree

def sync():
    mkdir(_sync_dir)
    _sync_sub(_sync_dir, get_tree('0'))

def _sync_sub(dir_path, tree):
    for name, item in tree.items():
        path = dir_path + '/' + name
        if isinstance(item, dict):
            mkdir(path)
            _sync_sub(path, item)
        else:
            with open(path, 'wb') as f:
                f.write(item.content())

client = Client(authenticate())
