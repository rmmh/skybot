import urllib
from xml.etree import ElementTree

def ytdata(id):
    url = 'http://gdata.youtube.com/feeds/api/videos/' + idt
    print url
    data = urllib.urlopen(url).read()
    if len(data) < 50: # it's some error message; ignore
        print data
        return
    global x
    def 
    x = ElementTree.XML(data)


if __name__ == '__main__':
    ytdata('the0KZLEacs')
