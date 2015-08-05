from urllib2 import Request, urlopen, URLError, HTTPError
from os import path, makedirs
from datetime import datetime, timedelta
import re
import httplib
import logging

logging.basicConfig(filename='jmasat.log',level=logging.DEBUG)

DATADIR = 'data'
series = {}
series['infra-NW'] = {'imglist': 'http://www.jma.go.jp/en/gms/hisjs/infrared-0.js',
                      'baseurl': 'http://www.jma.go.jp/en/gms/imgs/1/infrared/1/',
                  }
series['infra-Full'] = {'imglist': 'http://www.jma.go.jp/en/gms/hisjs/infrared-6.js',
                        'baseurl': 'http://www.jma.go.jp/en/gms/imgs/6/infrared/1/',
                    }
series['water-NW'] = {'imglist': 'http://www.jma.go.jp/en/gms/hisjs/watervapor-0.js',
                      'baseurl': 'http://www.jma.go.jp/en/gms/imgs/1/watervapor/1/',
                  }
series['water-Full'] = {'imglist': 'http://www.jma.go.jp/en/gms/hisjs/watervapor-6.js',
                        'baseurl': 'http://www.jma.go.jp/en/gms/imgs/6/watervapor/1/',
                    }

class HeadRequest(Request):
    def get_method(self):
        return "HEAD"

def getSatImage(series, baseurl, filename):
    dirpath = path.join(DATADIR, series)
    if not path.exists(dirpath):
        makedirs(dirpath)
    outpath = path.join(dirpath, filename)

    url = baseurl + filename

    download = True
    if path.isfile(outpath):
        ondisk_size = path.getsize(outpath)
        headers = urlopen(HeadRequest(url)).info().dict
        onweb_size = int(headers['content-length'])
        logging.debug("%s web filesize: %d" %(filename, onweb_size))
        if ondisk_size == onweb_size:
            download = False
            logging.debug("%s already exists locally with same filesize" %(filename))

    if download:
        req = Request(url)
        try:
            response = urlopen(req)
        except HTTPError as e:
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        except URLError as e:
            print 'We failed to reach a server.'
            print 'Reason: ', e.reason
        else:
            output = open(outpath,'wb')
            output.write(response.read())
            output.close()
            logging.debug("%s finished downloading." %(filename))

if __name__ == "__main__":
    p = re.compile(ur'ImageInfo\(\"(.*)\",')

    for s in series:
        info = series[s]
        baseurl = info['baseurl']
        req = Request(info['imglist'])
        logging.info("Getting image list for %s" %(s))
        res = urlopen(req)
        imglist = res.read()
        find = p.findall(imglist)
        filelist = find
        for f in filelist:
            logging.info("Getting %s: %s" %(s, f))

            getSatImage(s, info['baseurl'], f)
