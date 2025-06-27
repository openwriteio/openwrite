![logo](https://github.com/user-attachments/assets/5a0dc36c-1b62-40ba-b740-fe3b941b67fa)
openwrite is a minimalist blogging platform built for writing freely, hosting independently, and publishing without noise.

![version](https://img.shields.io/badge/version-0.6.0-purple) 

---

## Features

- Multiple blogs per user(limit defined in .env)
- Supports sqlite and mysql databases
- Upload images to local storage or bunny cdn
- Simple markdown editor in posting
- Discover section
- Privacy: 
    - Set if blog should be indexed in search engines
    - Set if post should be listed in "Discover" section
- Lightweight
- No tracking, only data collected is anonymized(hashed) IP for post view counting and likes
- Custom CSS per blog
- Federation using ActivityPub protocol: Follow and Like
- Likes system
- Posts importing from xml/csv
- Blog themes
- Gemini protocol

## In progress

- Lemmy federation
- Admin panel features

## TODO

- More security tests, patching
- Install for one blog
- Tests for building

## Installation

For now, *openwrite* is in development phase. Make sure to understand that the project can have security vulnerabilities at the moment. 

If you want to install the package now for testing or contributing:

1. Clone this repository
2. `pip install .` for installation 
3. `openwrite init` for initialization of .env
4. `openwrite run` for testing, `openwrite run -d` for deamonized run

