import urllib.error

import fire
import jadn
import json
import os
import requests
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


SBOM_SOURCES = os.path.join('Data', 'sbom-examples.json')
DEVICE_EXAMPLES = os.path.join('Data', 'device-examples.json')

PAR_API = 'https://2uqxczz7pjhcbmzp3ncfehfbdu.appsync-api.us-east-1.amazonaws.com/graphql'
PAR_AUTH = {'x-api-key': 'da2-didhri6n5jcgnkwssg44szk5yq'}


def init():
    """
    Delete everything, then create SBOMs and Devices
    """
    clear_all()
    create_devices()
    create_sboms()


def clear_all():
    """
    Delete all SBOMs and Devices
    """
    devs = list_items(item_type='listDevices', limit=1000)
    boms = list_items(item_type='listSBOMS', limit=1000)
    print(f'Deleting {len(devs)} Devices and {len(boms)} SBOMs')
    for item in boms:
        r = mutate_item('deleteDevice', 'DeleteDeviceInput!', {'id': item['id']})
    for item in boms:
        r = mutate_item('deleteSBOM', 'DeleteSBOMInput!', {'id': item['id']})


def create_devices():
    """
    Create some example Devices
    """
    with open(DEVICE_EXAMPLES) as fp:
        devices = json.load(fp)
    print(f'Creating {len(devices)} devices')


def create_sboms():
    """
    Create SBOMs from OSER list
    """
    with open(SBOM_SOURCES) as fp:
        sbom_uris = json.load(fp)
    print(f'Creating {len(sbom_uris)} SBOMs')
    for n, fn in enumerate(sbom_uris, start=1):
        response = requests.get(fn)
        data = response.content.decode()
        print(f'{n:>4} data:', fn, len(data))
        r = mutate_item('createSBOM', 'CreateSBOMInput!', {'sbom': {'uri': fn}})
        print(r)


def mutate_item(item_type: str, input_type: str, input_data: dict) -> dict:
    # TODO: Cache compiled commands
    result = client.execute(gql(
        """
        mutation MutateItem ($input_data: $$2) {
            $$1 (input: $input_data) {
                id
            }
        }
        """.replace('$$1', item_type).replace('$$2', input_type)
    ), variable_values={'input_data': input_data})
    return result[item_type]


def list_items(item_type: str, limit: int) -> list:
    items = []
    next_token = None
    while True:
        result = client.execute(gql(
            """
            query ListItems ($nextToken: String, $limit: Int) {
                $$1 (nextToken: $nextToken, limit: $limit) {
                    nextToken
                    count
                    items {
                        id
                    }
                }
            }
            """.replace('$$1', item_type)
        ), variable_values={'nextToken': next_token, 'limit': limit})
        items += result[item_type]['items']
        next_token = result[item_type]['nextToken']
        if not next_token:
            break
    return items


if __name__ == '__main__':
    par_auth = {'x-api-key': os.getenv('ParApiKey')} if os.getenv('ParApiKey') else PAR_AUTH
    transport = AIOHTTPTransport(url=PAR_API, headers=par_auth)
    client = Client(transport=transport, fetch_schema_from_transport=True)
    fire.Fire({
        'init': init,
        'clear': clear_all,
        'devices': create_devices,
        'sboms': create_sboms
    })