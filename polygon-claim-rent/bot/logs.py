import datetime

# according to this: https://12factor.net/logs
# you should always direct to stdout

def print_verbose(level, message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")
