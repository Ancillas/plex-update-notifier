import requests
import json
import getpass
import xml.etree.ElementTree as ET

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


if __name__ == "__main__":
    user = raw_input('Username: ') 
    password = getpass.getpass()
    plex = Plex(user, password, 'Plex Update Notifier')
    servers = plex.servers()
    for server in servers:
        print "{0} Update Available?: {1}".format(server["name"],
                                                  plex.update_available(server['address'], server['port'])) 
