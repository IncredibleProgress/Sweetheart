
from urllib.parse import urljoin as __urljoin
from urllib.request import urlopen,urlretrieve

def urljoin(base:str,*args,**kwargs) -> str:
    # avoid unexpected behavior with urljoin
    if not base.endswith('/'): base+='/'
    return __urljoin(base,*args,**kwargs)

def urlget(url:str) -> bytes:
    with urlopen(url) as file_like_object:
        #FIXME: should return bytes in most cases
        return file_like_object.read()
