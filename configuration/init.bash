#!/bin/bash

echo "Sweetheart Initialization"
printf "\033[0;31m%s\033[0m\n" \
  "WARN: for dev purposes only using Ubuntu 22.04 LTS and more"

# manage system update
reload="disabled"
sudo apt-get update -qq && sudo apt-get upgrade -q -y

# get current ubuntu codename and python version
codename=$(grep -w UBUNTU_CODENAME /etc/os-release | cut -d'=' -f2 | tr -d '"')
version=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
unit_python="unit-python$version"

if [[ -z "$codename" ]]; then
  echo "ERR: Ubuntu is required as OS for Sweetheart"
  exit 1
elif [[ "$codename" == "noble" ]]; then
  #FIXME: waiting for updates in official repositories
  # mantic is set here instead of noble for RethinkDB and Nginx Unit
  codename="mantic"
  # unit_python="libpython3.11 unit-python3.11"
  # # set repository for libpython3.11
  # sudo add-apt-repository --yes ppa:deadsnakes/ppa
fi

# get candidates for RethinkDB and Nginx Unit
redb_candidate=$(apt-cache policy rethinkdb | awk '/Candidate/ {print $2}')
unit_candidate=$(apt-cache policy unit | awk '/Candidate/ {print $2}')

# set official RethinkDB repository
if [[ -z "$redb_candidate" || "$redb_candidate" == "(none)" ]]; then

    wget -qO- https://download.rethinkdb.com/repository/raw/pubkey.gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/rethinkdb-archive-keyrings.gpg

    printf "%s %s\n"\
      "deb [signed-by=/usr/share/keyrings/rethinkdb-archive-keyrings.gpg]"\
      "https://download.rethinkdb.com/repository/ubuntu-$codename $codename main"\
    | sudo tee /etc/apt/sources.list.d/rethinkdb.list

    # Mark to reload the package list
    reload="enabled"
fi

# set official Nginx Unit repository 
if [[ -z "$unit_candidate" || "$unit_candidate" == "(none)" ]]; then

    wget -qO- https://unit.nginx.org/keys/nginx-keyring.gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/nginx-keyring.gpg

    printf "%s %s\n"\
      "deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg]"\
      "https://packages.nginx.org/unit/ubuntu/ $unit_codename unit"\
    | sudo tee /etc/apt/sources.list.d/unit.list

    # Mark to reload the package list
    reload="enabled"
fi

# reload the package list if required
if [[ "$reload" == "enabled" ]]; then
    sudo apt-get update -qq || exit 1; fi

# install required packages for Sweetheart dev
packages="git rethinkdb"
which -s unitd || packages="$packages unit $unit_python"
which -s poetry || packages="$packages python3-poetry"
# shellcheck disable=SC2086
sudo apt-get install -q $packages || exit 1

# set root directoty for Sweetheart project
mkdir --parents ~/.sweet/sweetheart

# set default directories for building Sweetheart projects
cd ~/.sweet/sweetheart &&
mkdir -v application configuration documentation my_code

# set default directories for custom python and react code
mkdir application/typescript my_code/python
ln --symbolic ../application/typescript my_code/react

# init default python env set for using RethinkDB and Jupyter kernel
poetry --directory=my_code/python --no-ansi -n -q init --name=my_code
poetry --directory=my_code/python --no-ansi -n -q add rethinkdb ipykernel

# clone whole Sweetheart sources from Github
#FIXME: to implement getting only the python source code
cd ~ && git clone https://github.com/IncredibleProgress/Sweetheart.git

# set github python sources as sweetheart module into python env
SWS_CMDLINE='sweetheart.cmdline $@'
SWS_PYTHON_ENV=$(poetry --directory=.sweet/sweetheart/my_code/python env info --path)
ln --symbolic ~/Sweetheart/code.python/src "$SWS_PYTHON_ENV/lib/python$version/site-packages/sweetheart"

if ! grep -q "export SWS_PYTHON_ENV=" ~/.bashrc; then
  # set Sweetheart python env into .bashrc
  printf "\n%s"\
    "# Sweetheart settings"\
    "export SWS_PYTHON_ENV=$SWS_PYTHON_ENV"\
    "alias sws='$SWS_PYTHON_ENV/bin/python3 -m $SWS_CMDLINE'"\
  >> ~/.bashrc
  # shellcheck disable=SC1090
  source ~/.bashrc
else
  echo "Sweetheart python env update in .bashrc"
  sed -i "s|^export SWS_PYTHON_ENV=.*|export SWS_PYTHON_ENV=$SWS_PYTHON_ENV|" ~/.bashrc
  # shellcheck disable=SC1090
  source ~/.bashrc
fi

# set exit message
echo "all done, Sweetheart prerequisites are ready"
echo "use 'sws --help' for more information"
