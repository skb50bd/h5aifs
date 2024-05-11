from fuse import FUSE
from httpfs import HttpFS

def main(mountpoint, url_base):
    FUSE(HttpFS(url_base), mountpoint, nothreads=True, foreground=True, ro=True)

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('usage: {} <url_base> <mountpoint>'.format(sys.argv[0]))
        exit(1)

    # from h5aiclient import H5aiClient
    # client = H5aiClient(sys.argv[1])
    # movies = client.get_file_info("/Movies/")
    # print(movies)
    # file_info = client.get_file_info("/Softwares/emby-theater-win64-(free)-stream.dflix.live.zip")
    # print(file_info)

    main(sys.argv[2], sys.argv[1])
