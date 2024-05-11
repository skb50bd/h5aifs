from fuse import FUSE, FuseOSError, Operations
from h5aiclient import H5aiClient
import requests
import errno

class HttpFS(Operations):
    def __init__(self, url_base):
        self.client = H5aiClient(url_base)

    def getattr(self, path, fh=None):
        print("getting attribute of: " + path)

        if path == "/" or path.endswith("/"):
            return {
                'st_mode': (0o755 | 0o040000),
                'st_nlink': 2,
                'st_size': 0
            }

        file_info = self.client.get_file_info(path)
        if file_info is None:
            raise FuseOSError(errno.ENOENT)

        mode = 0o755 if file_info['is_directory'] else 0o444
        return {
            'st_mode': (mode | 0o040000 if file_info['is_directory'] else 0o100000),
            'st_nlink': 2 if file_info['is_directory'] else 1,
            'st_size': file_info['length']
        }

    def read(self, path, size, offset, fh):
        # Attempt to get the content stream for a file
        try:
            content = self.client.get_file_content(path)
            content.seek(offset)  # Move to the offset
            return content.read(size)  # Read the desired size
        except requests.exceptions.RequestException as e:
            raise FuseOSError(errno.EIO) from e

    def readdir(self, path, fh):
        path = path if path[-1] == "/" else path + "/"
        print("reading dir: " + path)
        try:
            directory_content = self.client.get_directory_content(path)
            print("Found these files: ")
            entries = ['.', '..'] + [item['name'].strip('/') for item in directory_content]

            for x in entries:
                print(x)

            return entries
        except requests.exceptions.RequestException as e:
            raise FuseOSError(errno.ENOENT) from e

    def open(self, path, flags):
        # Validate that the file can be opened
        file_info = self.client.get_file_info(path)
        if file_info is None or file_info['is_directory']:
            raise FuseOSError(errno.EACCES)
        return 0  # File handle not used, return a dummy

    def exists(self, path):
        return self.client.exists(path)

    def is_file(self, path):
        return self.client.is_file(path)

    def is_directory(self, path):
        return self.client.is_directory(path)
