import fire
import jadn
import json
import os
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

SBOM_SOURCES = os.path.join('Data', 'sbom-examples.json')
DEVICE_EXAMPLES = os.path.join('Data', 'device-examples.json')

PAR_API = 'https://2uqxczz7pjhcbmzp3ncfehfbdu.appsync-api.us-east-1.amazonaws.com/graphql'
PAR_AUTH = {'x-api-key': os.getenv('ParApiKey')}


def init():
    """
    Delete everything, then create SBOMs and Devices
    """
    print('Init')
    list_devices()


def clear():
    """
    Delete all SBOMs and Devices
    """
    print('Clear')


def devices():
    """
    Create some example Devices
    """
    print('Devices')


def sboms():
    """
    Create SBOMs from OSER list
    """
    print('Sboms')


def list_devices():
    result = client.execute(gql(
        """
        query ListDevices ($limit: Int) {
            listDevices (limit: $limit) {
                nextToken
                items {
                    id
                }
            }
        }
        """
    ), variable_values={'limit': 2})
    print(result)


if __name__ == '__main__':
    transport = AIOHTTPTransport(url=PAR_API, headers=PAR_AUTH)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    fire.Fire({
        'init': init,
        'clear': clear,
        'devices': devices,
        'sboms': sboms
    })