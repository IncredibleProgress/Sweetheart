
def init_sources():
    # tested on Ubuntu 22.04 LTS

    os.run("sudo apt update -qq && sudo apt upgrade -q -y")

    # get distro infos
    os_release = freedesktop_os_release()
    distrib = os_release['ID'].lower()

    try:
        codename = os_release['UBUNTU_CODENAME'].lower()
    except:
        raise NotImplementedError("UBUNTU_CODENAME not found in /etc/os-release")

    if not os.stdout("apt policy unit"): #FIXME

        os.run(["sudo","gpg","--dearmor","-o","/usr/share/keyrings/nginx-keyring.gpg"],
            input=urlget("https://unit.nginx.org/keys/nginx-keyring.gpg"))

        os.run(["sudo","tee","/etc/apt/sources.list.d/unit.list"],text=True,
            input=f"deb [signed-by=/usr/share/keyrings/nginx-keyring.gpg]\
                https://packages.nginx.org/unit/{distrib}/ {codename} unit")

    if not os.stdout("apt policy rethinkdb"): #FIXME

        op.run(["sudo","gpg","--dearmor","-o","/usr/share/keyrings/rethinkdb-archive-keyrings.gpg"],
            input=urlget("https://download.rethinkdb.com/repository/raw/pubkey.gpg"))

        os.run(["sudo","tee","/etc/apt/sources.list.d/rethinkdb.list"],text=True,
            input=f"deb [signed-by=/usr/share/keyrings/rethinkdb-archive-keyrings.gpg]\
                https://download.rethinkdb.com/repository/{distrib}-{codename} {codename} main")

    os.run("sudo apt update -qq") #FIXME
