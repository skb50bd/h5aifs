import requests
import os
from urllib.parse import quote, unquote

class H5aiClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299',
            'Accept': '*/*'
        })

    def get_file_content(self, rel_path):
        response = self.session.get(self.base_url + quote(rel_path))
        response.raise_for_status()
        return response.content

    def get_file_info(self, rel_path):
        response = self.session.head(self.base_url + quote(rel_path))
        if not response.ok:
            return None

        name = os.path.basename(unquote(rel_path))
        length = response.headers.get('Content-Length')
        last_modified = response.headers.get('Last-Modified')
        is_directory = 'text/html' in response.headers.get('Content-Type', '')

        return {
            'name': name,
            'rel_path': rel_path,
            'last_modified': last_modified,
            'length': int(length) if length else 0,
            'is_directory': is_directory
        }

    def download_file(client, rel_path, output_path):
        try:
            # Get the streamed content
            content_stream = client.get_file_content(rel_path)
            with open(output_path, 'wb') as f:
                for chunk in content_stream:
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
            print(f"Download of {rel_path} to {output_path} completed.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def create_request_body_json_for_path(self, rel_path):
        return "{ action: \"get\", items: { href: \"" + quote(rel_path) + "\", what: 1 } }"

    def get_directory_content(self, rel_path):
        quoted_rel_path = quote(rel_path)
        
        response = self.session.post(self.base_url + quoted_rel_path, json={
            'action': 'get',
            'items': {
                'href': quoted_rel_path,
                'what': 1
            }
        })
        response.raise_for_status()
        content = response.json()

        return [{
            'name': unquote(item['href']).removeprefix(rel_path),
            'rel_path': unquote(item['href']),
            'last_modified': item['time'],
            'length': item.get('size', 0),
            'is_directory': 0 if item.get('size', 1) else 1
        } for item in content['items'] if item['href'].startswith(quoted_rel_path)][1:]

    def exists(self, rel_path):
        response = self.session.head(self.base_url + quote(rel_path))
        return response.ok

    def is_file(self, rel_path):
        response = self.session.head(self.base_url + quote(rel_path))
        return response.ok and 'text/html' not in response.headers.get('Content-Type', '')

    def is_directory(self, rel_path):
        response = self.session.head(self.base_url + quote(rel_path))
        return response.ok and 'text/html' in response.headers.get('Content-Type', '')
