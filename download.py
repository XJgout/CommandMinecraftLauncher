import requests

def download_file(url, filename, path):
    response = requests.get(url, stream=True)
    with open(path + filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)