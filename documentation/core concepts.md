# Sweetheart
### core concepts *provisional* 

## Low level

* Ubuntu Server LTS is the base os
* Nginx Unit serves React app as statics
* Nginx Unit serves data via Python ASGI
* Sweetheart handles directly the ASGI, Http and headers
* Nginx/Nginx Unit are set for Https2
* Rust is used for increasing performances and security
* Sweetheart a RethinkDB server as default database solution
* Sweetheart integrates an installer for rust,node,python,rdb
* N-1 stable/lts releases are used for production

## Python envs

* Sweetheart package runs in a dedicated venv with few dependencies
* Specific calculations and data processing are made in specifics venvs
* Jupyterlab must run in a dedicated venv too
* Sweetheart integrates Poetry and facilities for managing envs
* Sweetheart manages strictly authorized python packages and sources

## Apps 

* UI are coded with React and Typescript
* Sweetheart proposes some facilities for using py-script too
* Data exchanges are executed with websocket or fetch
* Calculations and data processing are managed with Python
* Styles are managed with TailwindCss instead of Css/Saas
* Sweetheart manages strictly authorized node modules and sources