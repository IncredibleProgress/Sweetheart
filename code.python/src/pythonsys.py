import urllib as _urllib_
from typing import NamedTuple


class urllib:

    @staticmethod
    def parse(url:str,*args,**kwargs) -> NamedTuple:
        """ convenient way for using urllib.parse.urlparse """

        return _urllib_.parse.urlparse(url,*args,**kwargs)

    @staticmethod
    def join(base:str,*args,**kwargs) -> str:
        """ convenient way for using urllib.request.urljoin """

        # avoid unexpected behavior with urljoin
        if not base.endswith('/'):
            base += '/'

        return _urllib_.parse.urljoin(base,*args,**kwargs)

    @staticmethod
    def get_bytes(url:str,*args,**kwargs) -> bytes:
        """ convenient way for using urllib.request.urlopen """

        with _urllib_.request.urlopen(url,*args,**kwargs) as file_like_object:
            fileo_content = file_like_object.read()
            assert isinstance(fileo_content,bytes)
        
        return fileo_content

    @staticmethod
    def retrieve(url:str,*args,**kwargs) -> tuple:
        """ convenient wait for using urllib.request.urlretrieve """

        return _urllib_.request.urlretrieve(url,*args,**kwargs)
