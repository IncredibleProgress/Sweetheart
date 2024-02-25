
import configparser
from sweetheart import *

from starlette.applications import Starlette
# from starlette.staticfiles import StaticFiles
from starlette.endpoints import WebSocketEndpoint
from starlette.routing import Route,Mount,WebSocketRoute
from starlette.responses import HTMLResponse,FileResponse,JSONResponse,RedirectResponse


class xWebsocket:

    def set_websocket(self,dbname=None,set_encoding='json'):

        class _WebSocket(WebSocketEndpoint):

            encoding = set_encoding
            route = f"/data/{dbname}"
            receiver = self.on_receive

            async def on_receive(self,websocket,data):
                await self.receiver(websocket,data)

        self.WebSocketEndpoint = _WebSocket
        verbose("new websocket endpoint: ",_WebSocket.route)
        return _WebSocket.route, _WebSocket
    
    def on_receive(self,websocket,data):
        raise NotImplementedError


class xSystemd:

    def set_service(self,
            Description:str = None,
            # filename:str = None,
            **kwargs ) -> configparser.ConfigParser :

        """ create and set config for new systemd service 
            kwargs keys must be supported service options
            
            [Unit]
              Description,After,Before
            [Service]
              ExecStart,ExecReload,Restart,Type,User,Group
            [Install]
              WantedBy,RequiredBy """

        # provide a ConfigParser for setting systemd
        self.sysd = configparser.ConfigParser()
        self.sysd.optionxform = str #! keep case of options 

        # set sections of systemd service file
        self.sysd.add_section('Unit')
        self.sysd.add_section('Service')
        self.sysd.add_section('Install')

        if Description:
            assert 'Description' not in kwargs
            self.sysd['Unit']['Description'] = Description

        # set given options within **kwargs
        for option,value in kwargs.items():

            section = "Service" #! default value
            for sctn in self.allowed_sysd_options:
                if option in self.allowed_sysd_options[sctn]:
                    section = sctn[1:-1]
                    break

            self.sysd[section][option] = value
        
        # debugging output messsage
        verbose("set systemd service:",self.sysd,level=2)

        # if filename:
        #     # enable service when given filename
        #     self.enable_service(filename)
        
        return self.sysd

    def enable_service(self,filename):

        """ write file and enable service within systemd
            it will provide default values when not given """

        # provide some flexibility with filename
        if filename.endswith(".service"): suffix = ""
        else: suffix = ".service"

        default_settings = {
            'Unit': {
                'Description': '[SWEETHEART] Service',
                'After': 'network.target' },
            'Service': {
                'Type': 'simple',
                'User': os.getuser(),
                'ExecStart': f'sh -c "{self.command}"' },
            'Install': {
                'WantedBy': 'default.target' }}
        
        # set the previous default settings if needed
        for section,optdic in default_settings.items():
            for option,value in optdic.items():
                if not self.sysd[section].get(option):
                    self.sysd[section][option] = value

        # write file and enable service in systemd
        tempfile = f"{self.config.root_path}/configuration/{filename}{suffix}"

        with open(tempfile,'w') as file_out:
            #! space_around_delimiters must be set at False
            self.sysd.write(file_out, space_around_delimiters=False )

        sp.sudo("cp",tempfile,self.system_dir)
        sp.sudo("systemctl","enable",tempfile)

        # def update_subproc_file(self,dict):
        #FIXME: add new service within subproc conf file
        # should become a class method provided by sp/BaseConfig/BaseService?
        self.config.subproc['systemd'].append(filename)

        with open(self.config.subproc_file,'r') as file_in:
            subproc_settings = json.load(file_in)
        
        subproc_settings.update({'systemd':self._.systemd})

        with open(self.config.subproc_file,'w') as file_out:
            json.dump(subproc_settings,file_out)
    