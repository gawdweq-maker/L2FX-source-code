import http.client
import json
import os.path
import sys

import config
from telemetry import DEFAULT_CORE_URL


def send_windows_info():
    return send_as_json('/stat/win', sys.getwindowsversion())


def send_server_info(image_path: str):
    exe_dir = os.path.dirname(image_path)
    parent_dir = os.path.dirname(exe_dir)

    server_info = {
        'client_path': image_path,
        'root_dir': os.listdir(parent_dir)
    }

    return send_as_json('/stat/server', server_info)


def send_l2fx_client_info():
    exe_dir = os.getcwd()
    client_info = {
        'client_path': exe_dir,
        'content': os.listdir(exe_dir)
    }
    if config.CLIENT_VER:
        client_info['client_ver'] = config.CLIENT_VER
    return send_as_json('/stat/client', client_info)


def send_as_json(endpoint: str, payload):
    if config.IS_TEST:
        return

    host = config.SERVER_URL if config.SERVER_URL else DEFAULT_CORE_URL
    url = f'{host}{endpoint}'

    # Split the URL into host and path
    if url.startswith('http://'):
        url = url[7:]
        secure = False
    elif url.startswith('https://'):
        url = url[8:]
        secure = True
    else:
        raise ValueError('Url must start with http:// or https://')

    host, _, path = url.partition('/')
    path = '/' + path

    # Prepare headers and fields
    headers = {
        "Content-Type": "application/json"
    }
    if config.LICENSE is not None:
        headers['hash-id'] = config.LICENSE
    if config.APP_ID is not None:
        headers['app-id'] = config.APP_ID

    # Send the request
    if secure:
        connection = http.client.HTTPSConnection(host)
    else:
        connection = http.client.HTTPConnection(host)

    body = json.dumps(payload, ensure_ascii=False)

    try:
        connection.request('POST', path, body=body.encode('utf-8'), headers=headers)
        response = connection.getresponse()

        # Read response
        response_data = response.read()
        if response.status != 200:
            print(f'StatReport error: {response.status}')

        connection.close()
        return response.status, response_data
    except ConnectionRefusedError as e:
        print(f'StatReport error: {e}')
