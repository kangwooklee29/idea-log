"""
gcp_cloud_functions/get_static_file/main.py
"""

import requests
import gzip
import logging
from flask import make_response


def get_static_file(request):
    """HTTP Cloud Function."""

    logging.basicConfig(level=logging.INFO)

    path = request.path
    base_url = 'https://kangwooklee29.github.io/idea-log/web_client'
    file_url = f'{base_url}{path}'

    try:
        response = requests.get(file_url, stream=True)
        response.raise_for_status()

        if 'gzip' in response.headers.get('Content-Encoding', ''):
            content = gzip.decompress(response.raw.read())
        else:
            content = response.content

        headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() != 'content-encoding'
        }

        return make_response((content, response.status_code, headers))
    except requests.exceptions.RequestException as e:
        logging.error(f'RequestException: {e}')
        return (f'File not found', 404, {'Content-Type': 'text/plain'})
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
        return ('Internal Server Error', 500, {'Content-Type': 'text/plain'})
