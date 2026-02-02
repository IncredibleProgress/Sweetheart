if status is-interactive
    # Commands to run in interactive sessions

    if [ $SHLVL -eq 1 ]

        # Welcome message
        set fish_greeting 'Sweetheart Coding Prompt'
        alias clear "clear && echo $fish_greeting"

        # Sweetheart environment
        set -x SWS_OPERATING_STATE 'development'
        set -x SWS_PYTHON_ENV '/home/nico/.cache/pypoetry/virtualenvs/sweetheart-5MmbPb1c-py3.12'

    else 
        set fish_greeting ''
        functions -e clear
    end

    # Abbreviations

    abbr -a home 'cd ~'
    abbr -a mycode 'cd ~/My_code'
    abbr -a mydoc 'cd ~/My_code/documentation/src'
    abbr -a mypy 'cd ~/My_code/python'
    abbr -a myapp 'cd ~/My_code/webapp'
    abbr -a myts 'cd ~/My_code/webapp/typescript'

    abbr -a cl clear
    abbr -a bat batcat
    abbr -a ipy $SWS_PYTHON_ENV/bin/ipython3
    abbr -a mdbook ~/.cargo/bin/mdbook

    abbr -a config 'vi ~/My_code/configuration/config.json'
    abbr -a config.fish 'vi  ~/.config/fish/config.fish'
    abbr -a config.unit 'sudo curl --unix-socket /var/run/control.unit.sock http://localhost/config/ | batcat --paging=never --language=json'
    abbr -a dbschema 'code ~/My_code/database/dbschema/default.gel'

    abbr -a ui 'powershell.exe -Command start brave http://localhost:8080'
    abbr -a doc 'powershell.exe -Command start brave http://localhost:3000'

    # Alias

    alias gel "$SWS_PYTHON_ENV/bin/python3 -m gel"
    alias sws "$SWS_PYTHON_ENV/bin/python3 -m sweetheart.cmdline"

end
