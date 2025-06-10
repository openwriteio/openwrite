import click
import subprocess
import os
import shutil
import requests
import time
from dotenv import load_dotenv
from .utils.create_db import init_db

load_dotenv()
cwd = os.getcwd()

def print_banner():
    click.secho(r"""


                                      _ _       
                                     (_) |      
   ___  _ __   ___ _ ____      ___ __ _| |_ ___ 
  / _ \| '_ \ / _ \ '_ \ \ /\ / / '__| | __/ _ \
 | (_) | |_) |  __/ | | \ V  V /| |  | | ||  __/
  \___/| .__/ \___|_| |_|\_/\_/ |_|  |_|\__\___|
       | |                                      
       |_|                                      


                  quiet place for loud thoughts
""", fg="cyan")


@click.group()
def cli():
    pass


@cli.command()
def init():
    if os.path.exists(".env"):
        click.confirm(".env already exists. Overwrite?", abort=True)

    domain = click.prompt("Choose a domain (ex. openwrite.io)")
    key = os.urandom(16).hex()
    upload = click.confirm("Enable media upload?", default=True)
    if upload:
        upload_storage = click.prompt("Storage type: bunny / local", default="local")
        if upload_storage == "bunny":
            bunny_api = click.prompt("Bunny.net API key")
            bunny_storagezone = click.prompt("Bunny.net storage zone")
            bunny_storageurl = click.prompt("Bunny.net storage URL")
    register = click.prompt("Allow self-register?", default=True)
    dbtype = click.prompt("Choose database type: sqlite / mysql", default="sqlite")
    if dbtype == "mysql":
        mysql_user = click.prompt("MySQL user")
        mysql_password = click.prompt("MySQL password")
        mysql_host = click.prompt("MySQL host IP")
        mysql_database = click.prompt("MySQL database name")
        dbpath = f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_database}"
    else:
        dbpath = click.prompt("sqlite database path", default=f"{cwd}/db.sqlite")
    listen_ip = click.prompt("What IP should openwrite listen on?", default=str("0.0.0.0"))
    listen_port = click.prompt("What port should openwrite listen on?", default="8081")
    blog_limit = click.prompt("Limit blogs per user? Set to 0 for no limit", default="3")
    

    with open(".env", "w") as f:
        f.write(f"IP={listen_ip}\n")
        f.write(f"PORT={listen_port}\n")
        f.write(f"BLOG_LIMIT={blog_limit}\n")
        f.write(f"DOMAIN={domain}\n")
        f.write(f"SECRET_KEY={key}\n")
        f.write(f"MEDIA_UPLOAD={'yes' if upload else 'no'}\n")
        if upload:
            f.write(f"UPLOAD_STORAGE={upload_storage}\n")
            if upload_storage == "bunny":
                f.write(f"BUNNY_API_KEY={bunny_api}\n")
                f.write(f"BUNNY_STORAGE_ZONE={bunny_storagezone}\n")
                f.write(f"BUNNY_STORAGEURL={bunny_storageurl}\n")
        f.write("BLOG_LIMIT=3\n")
        f.write(f"SELF_REGISTER={'yes' if register else 'no'}\n")
        f.write(f"DB_TYPE={dbtype}\n")
        f.write(f"DB_PATH={dbpath}\n")

    click.echo("[+] .env file created")
    click.echo("[*] Initializing database..")
    init_db(dbtype, dbpath)
    click.echo("[+] Database initialized")

@cli.command()
@click.option("-d", "--daemon", is_flag=True, help="Run in background (daemon)")
def run(daemon):
    from openwrite import create_app
    print_banner()
    ip = os.getenv("IP", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    if daemon:
        click.echo(f"[+] Openwrite listening on {ip}:{port}")
        subprocess.Popen(["gunicorn", "openwrite:create_app()", "--bind", f"{ip}:{port}", "--daemon"])
    else:
        app = create_app()
        app.run(host=ip, port=port)


@cli.command()
def install_service():
    service_name = "openwrite"
    service_file = f"""[Unit]
Description=OpenWrite Blog
After=network.target

[Service]
WorkingDirectory={os.getcwd()}
ExecStart={shutil.which('openwrite')} run
Restart=always
User={os.getenv("USER") or os.getlogin()}

[Install]
WantedBy=multi-user.target
"""

    path = f"/etc/systemd/system/{service_name}.service"
    if not os.geteuid() == 0:
        click.echo("[-] You need to run command as root: sudo openwrite install-service")
        return

    with open(path, "w") as f:
        f.write(service_file)

    os.system(f"systemctl daemon-reexec")
    click.echo(f"[+] Service {service_name} installed")


@cli.command()
def check_update():
    click.echo("[*] Checking for updates..")
    # np. na podstawie jakiegoś endpointu z wersją lub tagów GitHuba
    try:
        response = requests.get("https://raw.githubusercontent.com/twojuser/openwrite/main/version.txt")
        remote = response.text.strip()
        local = "0.1.0"  # TODO: dynamicznie z pakietu
        if remote != local:
            click.echo(f"[*] New version available: {remote} (current {local})")
        else:
            click.echo("[+] Openwrite is in latest version")
    except Exception as e:
        click.echo(f"Update-check error: {e}")


@cli.command()
def update():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    click.echo("[*] Backuping current directory")
    backup_dir = f"backup-{timestamp}"
    shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns("backup-*", "__pycache__", "*.pyc"))
    click.echo(f"[+] Backup initialized at {backup_dir}")

    click.echo("[*] Pulling newest code")
    os.system("git pull")
    click.echo("[+] Update completed")

@cli.command()
@click.option("--service", is_flag=True, help="Stop systemd service")
def stop(service):
    if service:
        click.echo("[*] Stopping systemd service: openwrite")
        os.system("sudo systemctl stop openwrite")
    else:
        click.echo("[*] Searching Gunicorn processes")
        try:
            out = subprocess.check_output(["pgrep", "-f", "gunicorn.*openwrite:create_app"], text=True)
            pids = out.strip().splitlines()
            for pid in pids:
                click.echo(f"[*] Killing {pid}")
                os.kill(int(pid), 15)
            click.echo("[+] Gunicorn soppted")
        except subprocess.CalledProcessError:
            click.echo("[-] Could not find Gunicorn processes")


if __name__ == "__main__":
    cli()

