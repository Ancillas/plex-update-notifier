import requests
import json
import getpass
import xml.etree.ElementTree as ET
import logging

class Plex:
    """A class for managing a small subset of Plex API calls"""
    api_url = "https://plex.tv" 

    def __init__(self, username, password, app_name):
        self.x_plex_client_identifier = app_name
        self.headers = { 'X-Plex-Client-Identifier': self.x_plex_client_identifier, 'Accept': 'application/json' }
        self.x_plex_token = self.token(username, password) 
        self.headers['X-Plex-Token'] = self.x_plex_token

    def token(self, username, password):
        url = ''.join([self.api_url, "/users/sign_in.json"]) 
        r = requests.post(url, auth=(username, password), headers=self.headers)
        body = r.json()
        return body['user']['authentication_token']

    def servers(self):
        url = ''.join([self.api_url, '/pms/servers'])
        r = requests.get(url, headers=self.headers)
        logger.debug(r.text)
        root = ET.fromstring(r.text)
        servers = [] 
        for child in root:
            servers.append({ 'name': child.get('name'),
                             'address': child.get('address'),
                             'port': child.get('port'),
                             'version': child.get('version') })
        return servers

    def update_available(self, address, port):
        url = "http://{0}:{1}/updater/status".format(address, port)
        r = requests.get(url, headers=self.headers)
        body = r.json()
        return len(body['_children']) > 0

    def server_available(self, address, port):
        url = "http://{0}:{1}/identity".format(address, port)
        try:
            r = requests.get(url)
            return r.status_code == 200
        except:
            return False

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)


if __name__ == "__main__":
    logger.info('Starting script')
    user = raw_input('Username: ') 
    password = getpass.getpass()
    logger.info('Creating Plex object')
    plex = Plex(user, password, 'Plex Update Notifier')
    logger.info('Getting list of plex servers')
    servers = plex.servers()
    logger.debug(servers)
    for server in servers:
        server['online'] = plex.server_available(server['address'], server['port'])

        if server['online']:
            server['update_available'] = plex.update_available(server['address'], server['port'])
        else:
            server['update_available'] = None

    print "{0} Update Available?: {1}".format(server["name"], server["update_available"])


