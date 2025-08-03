from fastapi import FastAPI
import os
from fastapi import FastAPI, HTTPException
import subprocess
import redis
import json

app = FastAPI()


# Connect to Redis container
r = redis.Redis(host='redis', port=6379, decode_responses=True)

@app.get("/redis/{ticker}")
def get_ticker_data(ticker: str):
    value = r.get(ticker)
    if not value:
        raise HTTPException(status_code=404, detail="Ticker not found in Redis")
    return json.loads(value)


SERVICE_MAP = {
    "MarketDataSimulator": "MarketDataSimulator",
    "DataConsumer": "DataConsumer",
    "DataReader": "DataReader"
}

@app.get("/logs/{service_name}")
def get_logs(service_name: str):
    container = SERVICE_MAP.get(service_name)
    if not container:
        raise HTTPException(status_code=404, detail="Service not found")

    try:
        logs = subprocess.check_output(["docker", "logs", "--tail", "50", container], stderr=subprocess.STDOUT)
        return {"logs": logs.decode("utf-8")}
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching logs: {e.output.decode('utf-8')}")



@app.post("/start")
def start_services():
    os.system("docker-compose up -d")
    return {"message": "Simulation started."}



@app.post("/stop")
def stop_services():
    os.system("docker-compose down")
    return {"message": "Simulation stopped."}
