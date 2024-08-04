import json
import os
import time
import asyncio
import csv
from datetime import datetime, timedelta
import aiohttp

SERVER_URL = os.getenv("SERVER_URL", "https://api.moecki.online/")
OUTPUT_DIR = "/app/output"
REQUESTS_FILE = "requests.json"
DATA_FILE_PATH = os.path.join(OUTPUT_DIR, "results.csv")
STATS_FILE_PATH = os.path.join(OUTPUT_DIR, "statistics.csv")
EXEC_INTERVAL_HOURS = 1  # in hours
WAIT_TIME_SECONDS = 5  # in seconds


async def perform_http_request(method, params):
    async with aiohttp.ClientSession() as session:
        json_data = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        headers = {"Content-Type": "application/json"}
        start_time = time.perf_counter()
        try:
            async with session.request("POST", SERVER_URL, json=json_data, headers=headers) as response:
                response_json = await response.json()  # Warte auf die vollständige Antwort
                if response.status != 200 or "error" in response_json:
                    raise Exception(f"Error response: {response_json}")
        except Exception as e:
            end_time = time.perf_counter()
            duration = None
            error_message = str(e)
            return duration, error_message
        end_time = time.perf_counter()
        duration = end_time - start_time
        return duration, None


async def main():
    with open(REQUESTS_FILE) as file:
        methods = json.load(file)

    end_time = datetime.now() + timedelta(days=1)
    interval = timedelta(hours=EXEC_INTERVAL_HOURS)

    with open(DATA_FILE_PATH, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["timestamp", "method", "duration", "error"])
        file.flush()

        while datetime.now() < end_time:
            for request in methods:
                name = request["name"]
                method = request["method"]
                params = request["params"]
                duration, error_message = await perform_http_request(method, params)
                # print(f"Method {name} took {duration:.4f} seconds")
                writer.writerow([datetime.now(), name, duration, error_message])
                await asyncio.sleep(WAIT_TIME_SECONDS)
                # break
            file.flush()
            await asyncio.sleep(interval.total_seconds())
            # break


# Berechnung der maximalen, minimalen und durchschnittlichen Zeiten
def calculate_statistics():
    durations = {}
    with open(DATA_FILE_PATH) as file:
        reader = csv.DictReader(file)
        for row in reader:
            method_name = row["method"]
            duration = float(row["duration"])
            if duration:
                duration = float(duration)
                if method_name not in durations:
                    durations[method_name] = []
                durations[method_name].append(duration)

    with open(STATS_FILE_PATH, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["method", "max_time", "min_time", "avg_time(ms)"])

        for method_name, times in durations.items():
            max_time = int(max(times) * 1000)
            min_time = int(min(times) * 1000)
            avg_time = int((sum(times) / len(times)) * 1000)
            writer.writerow([method_name, max_time, min_time, avg_time])
            # print(f"Method {method_name}: Max = {max_time:.4f}, Min = {min_time:.4f}, Avg = {avg_time:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
    calculate_statistics()
