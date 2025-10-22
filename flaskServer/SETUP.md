# Setup

## Instance type
- t2.medium
- ubuntu 20.04

## Install python3
```bash
sudo apt update
sudo apt install python3
sudo apt install python3-pip
```
## Install requirements
```bash
pip install -r requirements.txt
```

## Install gunicorn
```bash
sudo apt-get install gunicorn
```

## Run
```bash
ps aux | grep gunicorn
```
```bash
nohup /home/ubuntu/.local/bin/gunicorn -b 0.0.0.0:8000 -w 1 app:app
```

## Kill
```bash
kill {PID}
```

## Check memory
```bash
free -h
```