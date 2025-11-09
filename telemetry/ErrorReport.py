import uuid
import io
from PIL import Image
import http.client
import config
import l2helper
from telemetry import DEFAULT_CORE_URL


def create_multipart_body(fields, files):
    boundary = str(uuid.uuid4())
    body = bytearray()

    for name, value in fields.items():
        body.extend(f'--{boundary}'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend(f'Content-Disposition: form-data; name="{name}"'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend('')
        body.extend(b'\r\n')
        body.extend(value.encode('utf-8') if isinstance(value, str) else value)
        body.extend(b'\r\n')

    for name, (filename, filedata, content_type) in files.items():
        body.extend(f'--{boundary}'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend(f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend(f'Content-Type: {content_type}'.encode('utf-8'))
        body.extend(b'\r\n')
        body.extend('')
        body.extend(b'\r\n')
        body.extend(filedata.encode('utf-8') if isinstance(filedata, str) else filedata)
        body.extend(b'\r\n')

    body.extend(f'--{boundary}--'.encode('utf-8'))
    body.extend(b'\r\n')

    return body, boundary


def send(title: str, message: str, log: str or bytes, img=None):
    host = config.SERVER_URL if config.SERVER_URL else DEFAULT_CORE_URL
    url = f'{host}/report'

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
    headers = {}
    if config.LICENSE is not None:
        headers['hash-id'] = config.LICENSE
    if config.APP_ID is not None:
        headers['app-id'] = config.APP_ID
    fields = {
        'title': title,
        'message': message
    }
    files = {}

    if log:
        if isinstance(log, str):
            log = log.encode("utf-8")
        files['log'] = ('log_file', log.decode('utf-8'), 'text/plain; charset=utf-8')

    if isinstance(img, Image.Image):
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        files['screenshot'] = ('image_file', img_bytes.getvalue(), 'image/png')

    # Create multipart body
    body, boundary = create_multipart_body(fields, files)
    headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
    headers['Content-Length'] = str(len(body))

    # Send the request
    if secure:
        connection = http.client.HTTPSConnection(host)
    else:
        connection = http.client.HTTPConnection(host)

    connection.request('POST', path, body=body, headers=headers)
    response = connection.getresponse()

    # Read response
    response_data = response.read()
    connection.close()

    if response.status != 200:
        l2helper.msg_box(f"Error sending report\nHTTP Error {response.status} {response.reason}\nPlease contact support.", config.APP_NAME, l2helper.MB_ICONERROR)

    return response.status, response_data

