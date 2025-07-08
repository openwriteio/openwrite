import click
import subprocess
import os
import shutil
import requests
import time
import sys
from multiprocessing import Process
from dotenv import load_dotenv
from .utils.create_db import init_db
from contextlib import redirect_stdout, redirect_stderr
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timezone
import bcrypt

load_dotenv()
f_abs_path = os.path.abspath(__file__)
lib_cwd = "/".join(f_abs_path.split("/")[:-1])
cwd = os.getcwd()
env = f"{cwd}/.env"

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
    if os.path.exists(env):
        click.confirm(f"{env} already exists. Overwrite?", abort=True)

    mode = click.prompt("How are you willing to run openwrite?\n1. Multi-user\n2. Single user\n", type=int, default=1)
    domain = click.prompt("Choose a domain (ex. openwrite.io)")
    key = os.urandom(16).hex()
    upload = click.confirm("Enable media upload?", default=True)
    if upload:
        upload_storage = click.prompt("Storage type: bunny / local", default="local")
        if upload_storage == "bunny":
            bunny_api = click.prompt("Bunny.net API key")
            bunny_storagezone = click.prompt("Bunny.net storage zone")
            bunny_storageurl = click.prompt("Bunny.net storage URL")
        else:
            upload_path = click.prompt("Path to save files?", default=f"{cwd}/uploads")
            os.makedirs(upload_path, exist_ok=True)
    if mode == 1:
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
    blog_limit = 0
    if mode == 1:
        blog_limit = click.prompt("Limit blogs per user? Set to 0 for no limit", default="3")
    gemini = click.confirm("Run gemini service too?", default=True)
    if gemini:
        gemini_host = click.prompt("What IP gemini should listen on?", default="0.0.0.0")
        gemini_port = click.prompt("What port gemini should listen on?", default="1965")
        click.echo("[+] Generating certificate for Gemini...\n\n")
        os.makedirs(f"{cwd}/gemini", exist_ok=True)
        os.makedirs(f"{cwd}/gemini/mod", exist_ok=True)
        os.makedirs(f"{cwd}/gemini/.certs", exist_ok=True)
        subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:4096", "-keyout", f"{cwd}/gemini/.certs/key.pem", "-out", f"{cwd}/gemini/.certs/cert.pem", "-days", "365", "-nodes", "-subj", f"/CN={domain}"], check=True)
        if mode == 1:
            os.rename(f"{lib_cwd}/gemini_multi.py", f"{cwd}/gemini/mod/10_openwrite.py")
        elif mode == 2:
            os.rename(f"{lib_cwd}/gemini_single.py", f"{cwd}/gemini/mod/10_openwrite.py")

    logs_enabled = click.confirm("Enable logging?", default=True)
    if logs_enabled:
        logs_dir = click.prompt("Path to save logs", default=f"{cwd}/logs/")
    captcha_enabled = click.confirm("Enable captcha (Friendly catpcha)?", default=False)
    if captcha_enabled:
        captcha_sitekey = click.prompt("Friendly captcha sitekey")
        captcha_apikey = click.prompt("Friendly captcha API key")

        
    

    with open(env, "w") as f:
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
            else:
                f.write(f"UPLOAD_PATH={upload_path}\n")
        f.write("BLOG_LIMIT=3\n")
        if mode == 1:
            f.write(f"SELF_REGISTER={'yes' if register else 'no'}\n")
        f.write(f"DB_TYPE={dbtype}\n")
        f.write(f"DB_PATH={dbpath}\n")
        if mode == 1:
            f.write(f"MODE=multi\n")
        else:
            f.write(f"MODE=single\n")

        f.write(f"GEMINI={'yes' if gemini else 'no'}\n")
        if gemini:
            with open(f"{cwd}/gemini.ini", "w") as gem:
                gem.write("[server]\n")
                gem.write(f"host = {domain}\n")
                gem.write(f"address = {gemini_host}\n")
                gem.write(f"port = {gemini_port}\n")
                gem.write(f"certs = {cwd}/gemini/.certs\n")
                gem.write(f"modules = {cwd}/gemini/mod\n")
        f.write(f"LOGS={'yes' if logs_enabled else 'no'}\n")
        if logs_enabled:
            f.write(f"LOGS_DIR={logs_dir}")
        f.write(f"CAPTCHA_ENABLED={'yes' if captcha_enabled else 'no'}\n")
        if captcha_enabled:
            f.write(f"FRIENDLY_CAPTCHA_SITEKEY={captcha_sitekey}\n")
            f.write(f"FRIENDLY_CAPTCHA_APIKEY={captcha_apikey}\n")

    click.echo("[+] .env file created")
    click.echo("[*] Initializing database..")
    init_db(dbtype, dbpath)
    click.echo("[+] Database initialized")
    click.echo("[*] Adding admin user...")
    from .utils.models import User, Blog, Post, Settings
    from .utils.db import init_engine, SessionLocal
    init_engine(dbtype, dbpath)
    from .utils.db import SessionLocal
    admin_password = os.urandom(16).hex()
    hashed = bcrypt.hashpw(admin_password.encode("utf-8"), bcrypt.gensalt())
    admin_user = User(username="admin", email="", password_hash=hashed.decode("utf-8"), verified=1, admin=1)
    SessionLocal.add(admin_user)
    SessionLocal.commit()
    SessionLocal.close()
    click.echo(f"[+] Admin user added! Your credentials:\n\nLogin: admin\nPassword: {admin_password}")
    if logs_enabled and not os.path.exists(logs_dir):
        os.makedirs(logs_dir, exist_ok=True)
    
    if mode == 2:
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        private_pem = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()

        public_pem = key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        now = datetime.now(timezone.utc)

        new_blog = Blog(
            owner=1, 
            name="default", 
            title=domain, 
            index="on", 
            access="domain",
            description_raw=f"![hello](https://openwrite.b-cdn.net/hello.jpg =500x258)\n\n# Hello there! 👋\n\nYou can edit your blog description in [dashboard](http://{domain}/dashboard/edit/default)",
            description_html=f"<p><img src=\"https://openwrite.b-cdn.net/hello.jpg\" width=\"500\" height=\"258\"></p><h1>Hello there! 👋</h1><p>You can edit your blog description in <a href=\"http://{domain}/dashboard/edit/default\">dashboard</a></p>",
            css="",
            pub_key=public_pem,
            priv_key=private_pem,
            theme="default",
            created=now
        )

        new_setting = Settings(name="logo", value="/static/logo.png")

        SessionLocal.add(new_blog)
        SessionLocal.add(new_setting)
        SessionLocal.commit()

@cli.command()
@click.option("-d", "--daemon", is_flag=True, help="Run in background (daemon)")
def run(daemon):
    print_banner()

    ip = os.getenv("IP", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    gemini = os.getenv("GEMINI", "yes").lower() == "yes"
    gemini_port = int(os.getenv("GEMINI_PORT", 1965))
    gemini_proxy = os.getenv("GEMINI_PROXY", "no").lower() == "yes"

    logs_enabled = os.getenv("LOGS", "no").lower() == "yes"
    logs_dir = os.getenv("LOGS_DIR", "./logs")

    os.makedirs(logs_dir, exist_ok=True)

    gunicorn_access_log = os.path.join(logs_dir, "openwrite_access.log")
    gunicorn_error_log = os.path.join(logs_dir, "openwrite_error.log")

    gunicorn_cmd = [
        "gunicorn",
        "-w", "4",
        "openwrite:create_app()",
        "--bind", f"{ip}:{port}"
    ]

    gunicorn_logs = [
        "--access-logfile", f"{gunicorn_access_log}",
        "--error-logfile", f"{gunicorn_error_log}"
    ]

    gemini_cmd = [
        "gmcapsuled", "-c", f"{cwd}/gemini.ini"
    ]

    gemini_log = open(os.path.join(logs_dir, "gemini.log"), "a") if logs_enabled else subprocess.PIPE
    
    if gemini_proxy:
        gemini_cmd = gemini_cmd + ["proxy"]

    if logs_enabled:
        gunicorn_cmd = gunicorn_cmd + gunicorn_logs


    if daemon:
        click.echo(f"[+] Openwrite listening on {ip}:{port}")
        subprocess.Popen(gunicorn_cmd + ["--daemon"])

        if gemini:
            click.echo(f"[+] Gemini listening on {ip}:{gemini_port}")

            subprocess.Popen(gemini_cmd, stdout=gemini_log, stderr=subprocess.STDOUT)

    else:
        gunicorn_proc = subprocess.Popen(
            gunicorn_cmd
        )

        if gemini:
            click.echo(f"[+] Gemini started on {ip}:{gemini_port}")
            gemini_proc = subprocess.Popen(gemini_cmd, stdout=gemini_log)

        try:
            gunicorn_proc.wait()
            gemini_proc.wait()
        except KeyboardInterrupt:
            gunicorn_proc.terminate()
            gemini_proc.terminate()

@cli.command()
def debugrun():
    from openwrite import create_app
    print_banner()
    ip = os.getenv("IP", "0.0.0.0")
    port = int(os.getenv("PORT", 8080))
    app = create_app()
    app.run(host=ip, port=port)


@cli.command()
def install_service():
    service_name = "openwrite"
    service_file = f"""[Unit]
Description=openwrite instance
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
@click.option("--service", is_flag=True, help="Stop systemd service")
def stop(service):
    if service:
        click.echo("[*] Stopping systemd service: openwrite")
        os.system("sudo systemctl stop openwrite")
    else:
        click.echo("[*] Searching Gunicorn processes")
        try:
            out = subprocess.check_output(["pgrep", "-f", "gunicorn.*openwrite:create_app"], text=True)
            out_gemini = subprocess.check_output(["pgrep", "-f", "gemini\.py"], text=True)
            pids = out.strip().splitlines()
            pids_gemini = out_gemini.strip().splitlines()
            for pid in pids:
                click.echo(f"[*] Killing {pid}")
                os.kill(int(pid), 15)
            for gemini_pid in pids_gemini:
                click.echo(f"[*] Killing {gemini_pid}")
                os.kill(int(gemini_pid), 15)
            click.echo("[+] Gunicorn stopped")
            click.echo("[+] Gemini stoppted")
        except subprocess.CalledProcessError:
            click.echo("[-] Could not find any openwrite processes")


if __name__ == "__main__":
    cli()

