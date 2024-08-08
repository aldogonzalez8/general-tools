import itertools
import json
from collections import defaultdict
import urllib.parse

SESSION_FOLDER = "session_1723129133"
CONTROL_VERSION = "5.4.5"
TARGET_VERSION = "dev"

REQUESTS_CONTROL_FILE = f"/private/tmp/live_tests_artifacts/{SESSION_FOLDER}/command_execution_artifacts/source-stripe/read-with-state/{CONTROL_VERSION}/http_dump.har"
REQUESTS_TARGET_FILE =  f"/private/tmp/live_tests_artifacts/{SESSION_FOLDER}/command_execution_artifacts/source-stripe/read-with-state/{TARGET_VERSION}/http_dump.har"



def default_factory():
    return {"target": 0, "control": 0}


def get_entries(requests_found, path_file, type):
    with open(path_file, 'r') as file:
        data = json.load(file)
    entries = data["log"]["entries"]
    total = 0
    for entry in entries:
        request_url = entry["request"]["url"]
        decoded_url = urllib.parse.unquote(request_url)
        requests_found[f"{decoded_url}"][type] += 1
        total += 1
    return total

def main():
    requests_found = defaultdict(default_factory)
    control_total = get_entries(requests_found, REQUESTS_CONTROL_FILE, "control")
    target_total = get_entries(requests_found, REQUESTS_TARGET_FILE, "target")

    first_column_width = 150
    control_count_width = 10

    def print_request_with_wrap(request, control_count, target_count):
        while len(request) > first_column_width:
            print(f"{request[:first_column_width]}")
            request = request[first_column_width:]
        print(f"{request:<{first_column_width}}  {control_count:<{control_count_width}} {target_count}")

    only_control = []
    control_and_target = []
    only_target = []

    for request, results in requests_found.items():
        target_count = results["target"]
        control_count = results["control"]
        if control_count and not target_count:
            only_control.append([request, control_count, target_count])
        elif control_count and target_count:
            control_and_target.append([request, control_count, target_count])
        else:
            only_target.append([request, control_count, target_count])

    print(f"{'Requests only in control':<{first_column_width}} {'Control':<{control_count_width}} {'Target'}")
    print(f"{'-' * first_column_width} {'-' * control_count_width} {'-' * 6}")
    for request, control_count, target_count in only_control:
        if control_count > 1:
            control_count = str(control_count) + "*"
        print_request_with_wrap(request, control_count, target_count)

    print(f"\n{'Requests in control and target':<{first_column_width}} {'Control':<{control_count_width}} {'Target'}")
    print(f"{'-' * first_column_width} {'-' * control_count_width} {'-' * 6}")
    for request, control_count, target_count in control_and_target:
        if control_count > 1:
            control_count = str(control_count) + "*"
        if target_count > 1:
            target_count = str(target_count) + "*"
        print_request_with_wrap(request, control_count, target_count)

    print(f"\n{'Requests only in target':<{first_column_width}} {'Control':<{control_count_width}} {'Target'}")
    print(f"{'-' * first_column_width} {'-' * control_count_width} {'-' * 6}")
    for request, control_count, target_count in only_target:
        if control_count > 1:
            control_count = str(control_count) + "*"
        if target_count > 1:
            target_count = str(target_count) + "*"
        print_request_with_wrap(request, control_count, target_count)


    print(f"\nControl Total: {control_total}")
    print(f"Target Total: {target_total}")
    print("======Next are unique calls:=======")
    print(f"Requests only present in Control: {len(only_control)}")
    print(f"Requests in Control and Target: {len(control_and_target)}")
    print(f"Requests only in Target: {len(only_target)}")

    fixed_size = 100

    def print_in_chunks(control_request, target_request, size):
        for chunk1, chunk2 in itertools.zip_longest(
                [control_request[i:i + size] for i in range(0, len(control_request), size)],
                [target_request[i:i + size] for i in range(0, len(target_request), size)],
                fillvalue=''
        ):
            print(f"{chunk1:<{size}} | {chunk2}")

    # Create an iterator that fills missing items with an empty list
    iterator = itertools.zip_longest(only_control, only_target, fillvalue=[''])

    print("\nUnique requests side by side")
    print(f"\n{'Control':<{fixed_size}} | Target")
    print('-' * (fixed_size * 2 + 3)) 
    for item1, item2 in iterator:
        control_request = item1[0] if item1 else ''
        target_request = item2[0] if item2 else ''

        print_in_chunks(control_request, target_request, fixed_size)
        print('-' * (fixed_size * 2 + 3))  


def run():
    # todo: make session, control and target params
    main()
