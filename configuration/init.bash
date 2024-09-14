#!/bin/bash

echo "SWEETHEART Initialization"
printf "\033[0;31m%s\033[0m\n" "warn: for dev purposes only using Ubuntu 22.04 LTS and more"

# system update
sudo apt-get update -q && sudo apt-get upgrade -q -y

# ubuntu version codename
# FIXME: lunar is set here instead of noble waiting for updates
codename=$(grep -w UBUNTU_CODENAME /etc/os-release | cut -d'=' -f2 | tr -d '"')
if [[ "$codename" == "noble" ]]; then codename="lunar"; fi

# set official RethinkDB repository 
if [[ -z "$(apt-cache policy rethinkdb)" ]]; then

    wget -qO- https://download.rethinkdb.com/repository/raw/pubkey.gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/rethinkdb-archive-keyrings.gpg

    printf "%s %s\n"\
      "deb [signed-by=/usr/share/keyrings/rethinkdb-archive-keyrings.gpg]"\
      "https://download.rethinkdb.com/repository/ubuntu-$codename $codename main"\
    | sudo tee /etc/apt/sources.list.d/rethinkdb.list
fi

# set official Nginx Unit repository 
if [[ -z "$(apt-cache policy unit)" ]]; then

    wget -qO- https://unit.nginx.org/keys/nginx-keyring.gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/nginx-keyring.gpg

    printf "%s %s\n"\
      "deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg]"\
      "https://packages.nginx.org/unit/ubuntu/ $codename unit"\
    | sudo tee /etc/apt/sources.list.d/unit.list
fi

# install required packages for Sweetheart dev
packages=""
which -s git || packages="$packages git"
# which npm || packages="$packages npm"
# which cargo || packages="$packages cargo"
which -s rethinkdb || packages="$packages rethinkdb"
# version=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
which -s unitd || packages="$packages unit unit-python3.11"
which -s poetry || packages="$packages python3-poetry"

sudo apt-get update -q && sudo apt-get install -q -y $packages || exit 1

# clone whole Sweetheart sources from Github
cd ~ && git clone https://github.com/IncredibleProgress/Sweetheart.git || exit 1

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

if ! grep -q "export SWS_PYTHON_ENV=" ~/.bashrc; then
  # set Sweetheart python env into .bashrc
  printf "\n%s"\
    "# Sweetheart settings"\
    "export SWS_PYTHON_ENV=$SWS_PYTHON_ENV"\
    "alias sws=$SWS_PYTHON_ENV/bin/python3 -m sweetheart.cmdline $*"\
  >> ~/.bashrc
  # shellcheck disable=SC1090
  source ~/.bashrc
fi
