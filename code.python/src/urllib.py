import urllib.parse
import urllib.request
from typing import NamedTuple


def urlparse(url:str,*args,**kwargs) -> NamedTuple:
    """ convenient way for using urllib.parse.urlparse """
    return urllib.parse.urlparse(url,*args,**kwargs)


def urlparse_qs(url:str,*args,**kwargs) -> dict:
    """ convenient way for using urllib.parse.parse_qs """

    params = urllib.parse.parse_qs(
        urlparse(url, allow_fragments=False ).query,
        *args,**kwargs)

    return {k: v[0] if len(v)==1 else v for k,v in params.items()}


def urlretrieve(url:str,*args,**kwargs) -> tuple:
    """ convenient way for using urllib.request.urlretrieve """
    return urllib.request.urlretrieve(url,*args,**kwargs)


def urlgetb(url:str,*args,**kwargs) -> bytes:
    """ convenient way for using urllib.request.urlopen 
        for downloading bytes through the get method """

    with urllib.request.urlopen(url,*args,**kwargs) as file_like_object:
        fileo_content = file_like_object.read()
    
    assert isinstance(fileo_content,bytes)
    return fileo_content
