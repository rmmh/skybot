import socket
import re
import locale

import hook

locale.setlocale(locale.LC_ALL, "")

def recv_basic(the_socket):
    total_data=[]
    while True:
        data = the_socket.recv(8192)
        if not data: break
        total_data.append(data)
    return ''.join(total_data)


def tinyurlparse(url):
    id = url[(url.rfind("/",8)+1):]
    ts = socket.socket()
    ts.connect(("tinyurl.com", 80))
    ts.send("GET /redirect.php?num=%s HTTP/1.1\r\n" % id)
    ts.send("Host: tinyurl.com\r\n\r\n");
    tresult = recv_basic(ts);
    for tline in tresult.split("\n"):
       if tline[:10] == "Location: ":
           return tline[10:]

tinyurl_re = re.compile(r'http://(www\.)?tinyurl.com/([A-Za-z0-9\-]+)', flags=re.IGNORECASE)

@hook.command(hook=r'(.*)', prefix=False)
def tinyurl(inp):
    tumatch = tinyurl_re.search(inp)
    if (tumatch is not None):
        return tinyurlparse(tumatch.group())
