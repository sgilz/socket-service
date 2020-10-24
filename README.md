# socket-server-client-service
This is a server/client service programmed with socket in python for understanding bases of TCP/IP.

## How to run this projects
1. Create a python virtual environment.
```bash
python -m venv <env_path>
```
2. Activate the privious created virtual env. 
```bash
source <env_path>/bin/activate
```
3. Clone this repo and go to its directory:
```bash
git clone <repo_url>
cd <repo_root_dir>
```
4. Add the project to your virtual env python path.
```bash
pip install -e . #Do not dismiss the dot (.)
```

5. Go to the **server** directory and run it.

```bash
cd server
python server.py [buckets_root_dir]
```
6. From another terminal, go to the **client** directory and run it.

```bash
cd client
python client.py [buckets_root_dir]
```