# openwrite

openwrite is a minimalist blogging platform built for writing freely, hosting independently, and publishing without noise.

---

## Features

- Multiple blogs per user(limit defined in .env)
- Supports sqlite and mysql databases
- Built with Flask
- Upload images to local storage or bunny cdn
- Simple markdown editor in posting
- Discover section
- Privacy: 
    - Set if blog should be indexed in search engines
    - Set if post should be listed in "Discover" section
- Lightweight
- No tracking, only data collected is anonymized(hashed) IP for post view counting
- Custom CSS per blog

## TODO

- Federation using ActivityPub protocol
- More security tests, patching
- Increase options in admin panel
- Better file structure

## Installation

For now, *openwrite* is in development phase. Make sure to understand that the project can have security vulnerabilities at the moment. 

If you want to install the package now for testing or contributing:

1. Clone this repository
2. `pip install .` for installation 
3. `openwrite init` for initialization of .env
4. `openwrite run` for testing, `openwrite run -d` for deamonized run
