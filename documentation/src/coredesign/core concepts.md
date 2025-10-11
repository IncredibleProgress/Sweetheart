# Core concepts *draft*

## Sweetheart targets

* introduce a consistent way for making dev within company
* provide up-to-date and top-rated capabilities, ready-to-use
* intend at the heart to cover specific needs of the industry
* make simple dev integration into company's change strategies
* no commercial dependencies are set and needed in the basement
* encourage the "1 knowledge package that covers all" idea

## Low-level concepts

* Ubuntu Server LTS is the base os
* NginxUnit serves React app as statics
* NginxUnit serves data via Python ASGI
* Sweetheart handles directly Http with ASGI
* Nginx/NginxUnit are set for Https2
* Rust is used for increasing performances and security
* Sweetheart set RethinkDB server as inner database solution
* Sweetheart integrates an installer for rust,node,python and resources
* Sweetheart set relevant configurations and ensure security settings
* N-1 stable/lts releases are used for production
* Documentation is built with mdbook (rust crate)

## Python envs concepts

* Sweetheart package runs in a dedicated env with few dependencies
* Specific calculations and data processing are made in specifics envs
* Jupyterlab must run in another dedicated env too
* Sweetheart integrates Poetry and facilities for managing envs
* Sweetheart manages strictly authorized python packages and sources

## Apps concepts

* UI are coded with React and Typescript
* Sweetheart provides some facilities for using py-script
* Data exchanges are executed with websocket or fetch
* Sweetheart provides tools for structuring and setting data
* Calculations and data processing are managed with Python
* Styles are managed with TailwindCss instead of Css/Saas
* Sweetheart manages strictly authorized node modules and sources
