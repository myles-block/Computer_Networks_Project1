import subprocess
import json
import time

def run_traceroute(host, output_file):
    try:
        # Start the traceroute process
        traceroute_process = subprocess.Popen(['traceroute', host], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        hop_data = []

        while True:
            line = traceroute_process.stdout.readline().decode('utf-8').strip()
            if not line:
                break

            # Parse the traceroute output to capture hop information
            hop_info = line.split()
            hop_number = int(hop_info[0])
            hop_ip = hop_info[1]
            hop_data.append({'hop_number': hop_number, 'hop_ip': hop_ip})

            # Append the current hop data to the JSON file
            with open(output_file, 'a') as file:
                json.dump({'traceroute_data': hop_data}, file)
                file.write('\n')  # Add a newline to separate JSON objects

    except subprocess.CalledProcessError as e:
        print("Error:", e)
    except KeyboardInterrupt:
        print("Traceroute stopped by user.")
    finally:
        if traceroute_process.poll() is None:
            traceroute_process.terminate()
            traceroute_process.wait()

if __name__ == "__main__":
    host = "10.0.0.1"
    output_file = "traceroute_data.json"
    run_traceroute(host, output_file)
