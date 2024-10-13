import urllib
from typing import NamedTuple


def urlparse(url:str,*args,**kwargs) -> NamedTuple:
    """ convenient way for using urllib.parse.urlparse """

    return urllib.parse.urlparse(url,*args,**kwargs)


def urlretrieve(url:str,*args,**kwargs) -> tuple:
    """ convenient wait for using urllib.request.urlretrieve """

    return urllib.request.urlretrieve(url,*args,**kwargs)


def urlgetb(url:str,*args,**kwargs) -> bytes:
    """ convenient way for using urllib.request.urlopen 
        for downloading bytes through the get method """

    with urllib.request.urlopen(url,*args,**kwargs) as file_like_object:
        fileo_content = file_like_object.read()
    
    assert isinstance(fileo_content,bytes)
    return fileo_content


# def urljoin(base:str,*args,**kwargs) -> str:
#     """ convenient way for using urllib.request.urljoin """

#     # avoid unexpected behavior with urljoin
#     if not base.endswith('/'):
#         base += '/'

#     return urllib.parse.urljoin(base,*args,**kwargs)
