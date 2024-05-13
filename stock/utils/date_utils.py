import subprocess


def get_time_offset():
    try:
        process = subprocess.Popen(["date", "-R"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, _ = process.communicate()
        if process.returncode == 0:
            time_offset = int(output.decode().split()[-1])/100
            return time_offset
        else:
            print("Error:", process.stderr.decode())
    except Exception as e:
        print("Error:", e)
    return 0

if __name__ == "__main__":
    print(get_time_offset())
