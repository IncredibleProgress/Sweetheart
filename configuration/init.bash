#!/bin/bash

echo "SWEETHEART Initialization"
printf "\033[0;31m%s\033[0m\n" "warn: for dev purposes only using Ubuntu 22.04 LTS and more"

# system update
sudo apt-get update -qq && sudo apt-get upgrade -qq -y

# ubuntu version codename
# FIXME: lunar is set here instead of noble waiting for updates
codename=$(grep -w UBUNTU_CODENAME /etc/os-release | cut -d'=' -f2 | tr -d '"')
if [[ "$codename" == "noble" ]]; then codename="lunar"; fi

# set official RethinkDB repository 
if ! (apt policy rethinkdb); then

    wget -qO- https://download.rethinkdb.com/repository/raw/pubkey.gpg \|
        sudo gpg --dearmor -o /usr/share/keyrings/rethinkdb-archive-keyrings.gpg

    echo "deb [signed-by=/usr/share/keyrings/rethinkdb-archive-keyrings.gpg]
        https://download.rethinkdb.com/repository/ubuntu-$codename $codename main" \|
        sudo tee /etc/apt/sources.list.d/rethinkdb.list
fi

# set official Nginx Unit repository 
if ! (apt policy unit); then

    wget -qO- https://unit.nginx.org/keys/nginx-keyring.gpg \|
        sudo gpg --dearmor -o /usr/share/keyrings/nginx-keyring.gpg

    echo "deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg] \
        https://packages.nginx.org/unit/ubuntu/ $codename unit" \|
        sudo tee /etc/apt/sources.list.d/unit.list
fi

# install required packages for Sweetheart dev
command="sudo apt-get update -q && sudo apt-get install -q -y"
version=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)

which rethinkdb || command="$command rethinkdb"
which unitd || command="$command unit unit-python$version"

which git || command="$command git"
# which npm || command="$command npm"
# which cargo || command="$command cargo"
which poetry || command="$command python3-poetry"

$command

# clone whole Sweetheart sources from Github
cd ~ && git clone https://github.com/IncredibleProgress/Sweetheart.git

# set root directoty for Sweetheart project
mkdir --parents ~/.sweet/sweetheart

# set default directories for building Sweetheart projects
cd ~/.sweet/sweetheart &&
mkdir -v application configuration documentation my_code

# set default directories for custom python and react code
mkdir application/typescript my_code/python
ln --symbolic application/typescript my_code/react 2>/dev/null

# init default python env set for using RethinkDB and Jupyter kernel
poetry --directory=my_code/python --no-ansi -n -q init --name=sweetheart
poetry --directory=my_code/python --no-ansi -n -q add rethinkdb ipykernel

# set github python sources as sweetheart module into python env
SWS_PYTHON_ENV=$(poetry --directory=my_code/python env info --path)
ln --symbolic ~/Sweetheart/code.python/src "$SWS_PYTHON_ENV/lib/python*/site-packages/sweetheart"

#FIXME:
export SWS_PYTHON_ENV
sed -i "/^export SWS_PYTHON_ENV=/c\export SWS_PYTHON_ENV=$SWS_PYTHON_ENV" ~/.bashrc
