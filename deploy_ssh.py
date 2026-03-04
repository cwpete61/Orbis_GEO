import paramiko
import time
import sys
import os
from dotenv import load_dotenv

load_dotenv()

host = "147.93.183.4"
password = os.getenv("SERVER_PASSWORD")
api_key = os.getenv("OPENAI_API_KEY")

print(f"Connecting to {host}...")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    client.connect(hostname=host, username="root", password=password, timeout=10)
    print("Connected successfully!")
    
    command = f"cd ~/Orbis_GEO && git pull && echo 'OPENAI_API_KEY={api_key}' > .env && echo 'NODE_ENV=production' >> .env && docker compose up -d --build"
    
    print(f"Executing deployment sequence...")
    stdin, stdout, stderr = client.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    out = stdout.read().decode('utf-8').strip()
    err = stderr.read().decode('utf-8').strip()
    
    if out: print(f"Output: {out}")
    if err: print(f"Error: {err}")
        
    print("Deployment completed successfully!")
except Exception as e:
    print(f"Deployment failed: {e}")
finally:
    client.close()
