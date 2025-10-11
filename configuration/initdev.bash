#!/bin/bash

echo "[SWEETHEART] System Initialization"
printf "\033[0;31m%s\033[0m\n"\
  "WARN: for dev purposes only using Ubuntu 24.04 LTS and more"

# manage system update
reload="disabled"
sudo apt-get update -qq || exit 1

# get current ubuntu codename and python version
codename=$(grep -w UBUNTU_CODENAME /etc/os-release | cut -d '=' -f 2 | tr -d '"')
version=$(python3 --version | awk '{print $2}' | cut -d '.' -f 1,2)
unit_python="unit-python$version"

if [[ -z "$codename" ]]; then
  echo "error: Ubuntu OS is expected for Sweetheart" >&2
  exit 1
# elif [[ "$codename" == "noble" ]]; then
  #[Deprecated] waiting for updates in official repositories
  # mantic is set here instead of noble for Nginx Unit
  # codename="mantic"
  #[Deprecated] set a specific python version for Nginx Unit
  # unit_python="libpython3.11 unit-python3.11"
  # # add a repository for getting libpython3.11
  # sudo add-apt-repository --yes ppa:deadsnakes/ppa
fi

#1. Install System Base Architecture #

printf "\n%s\n" "checking for prerequisites..."
command -v snap || sudo apt-get install -q -y snapd || exit 1
command -v caddy || sudo sudo snap install caddy || exit 1
command -v vault || sudo sudo snap install vault || exit 1
command -v npm || sudo sudo snap install node --classic || exit 1

if ! command -v cargo; then
  #NOTE: snapcraft provides last stable version of Rust
  sudo snap install rustup --classic || exit 1
  rustup default stable || exit 1
fi

if ! command -v ~/.local/bin/gel; then
  #NOTE: install gel cli via official script from geldata
  command -v curl || sudo apt-get install -q -y curl || exit 1
  curl https://www.geldata.com/sh --proto "=https" -sSf1 | sh
  export PATH="$HOME/.local/bin:$PATH" #FIXME
fi

if ! command -v unitd; then

    command -v wget || sudo apt-get install -q -y wget || exit 1
    command -v gpg || sudo apt-get install -q -y gpg || exit 1

    wget -qO- https://unit.nginx.org/keys/nginx-keyring.gpg \
    | sudo gpg --dearmor -o /usr/share/keyrings/nginx-keyring.gpg

    printf "%s %s\n"\
      "deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg]"\
      "https://packages.nginx.org/unit/ubuntu/ $codename unit"\
    | sudo tee /etc/apt/sources.list.d/unit.list

    # Mark to reload the package list
    reload="enabled"
fi

# reload the package list if required
if [[ "$reload" == "enabled" ]]; 
    then sudo apt-get update -qq || exit 1; fi

# install required packages for development and testing
command -v git || sudo apt-get install -q -y git || exit 1
command -v unitd || sudo apt-get install -q -y unit "$unit_python" || exit 1
command -v ~/.cargo/bin/mdbook || cargo install -q mdbook || exit 1
command -v poetry || sudo apt-get install -q -y python3-poetry || exit 1

#2. Set Sweetheart Dev Environment #

# clone whole Sweetheart sources from Github
cd ~ && git clone https://github.com/IncredibleProgress/Sweetheart.git

# provide python env and cli into .bashrc
if ! grep -q "SWS_PYTHON_ENV=" ~/.bashrc; then

  # set Sweetheart python environment
  cd ~/Sweetheart/code.python || exit 1
  poetry --no-ansi -n --no-root install || exit 1 #FIXME
  SWS_PYTHON_ENV=$(poetry env info --path)

  if [[ -z "$SWS_PYTHON_ENV" ]]; then
    echo "error: python env installation failed" >&2
    exit 1; fi

  # link Sweetheart python module into python env
  ln --symbolic ~/Sweetheart/code.python/src "$SWS_PYTHON_ENV/lib/python$version/site-packages/sweetheart"

  printf "\n%s"\
    "# Sweetheart settings"\
    "export SWS_OPERATING_STATE=development"\
    "export SWS_PYTHON_ENV=$SWS_PYTHON_ENV"\
    "alias sws='$SWS_PYTHON_ENV/bin/python3 -m sweetheart.cmdline'"\
  >> ~/.bashrc
fi

#3. Report and Exit #

# installation report for dev purposes
printf "\navailable for dev:\n"
python3 --version || exit 1
echo "node $(node --version)" || exit 1
rustc --version || exit 1

# exit message
echo "all done, start your project in $HOME/My_code"
exit 0