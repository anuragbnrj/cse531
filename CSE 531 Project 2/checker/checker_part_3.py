import json
import sys

if len(sys.argv) < 2:
    print("Input argument?")
    exit()

filename = sys.argv[1]
# Read JSON data from a file
with open(filename, 'r') as file:
    events = json.load(file)


# Sort the events by the "logical_clock" attribute
sorted_events = sorted(events, key=lambda event: event['logical_clock'])

def check_condition(event, customer_requests):
    request_id = event["customer-request-id"]

    if request_id not in customer_requests:
        customer_requests[request_id] = {"branches": {}}

    customer_request = customer_requests[request_id]
    branch_id = event["id"]

    if branch_id not in customer_request["branches"]:
        customer_request["branches"][branch_id] = {"last_logical_clock": 0}

    current_clock = event["logical_clock"]
    branch = customer_request["branches"][branch_id]

    # Check if logical clock is incremental within the same request and branch
    if current_clock < branch["last_logical_clock"]:
        return False

    branch["last_logical_clock"] = current_clock

    if event["interface"].startswith("propogate"):
        # If the event is a propagate event, store it for later comparison
        customer_request["propagate_events"] = event
    else:
        # Check if non-propagate events happen before propagate events
        if "propagate_events" in customer_request and current_clock > customer_request["propagate_events"]["logical_clock"]:
            return False

    return True


customer_requests = {}
correct_events = 0
total_events = 0
incorrect_events = 0

for event in sorted_events:
    total_events += 1
    if (check_condition(event, customer_requests)):
        correct_events += 1
        print(f"customer-request-id: {event['customer-request-id']} - Condition met (OK)")
    else:
        incorrect_events += 1
        print(f"customer-request-id: {event['customer-request-id']} - Condition not met (Error)")


print("\nSummary:")
print(f"\nTotal Events: {total_events}")
print(f"Correct Events: {correct_events}")
print(f"Incorrect Events: {incorrect_events}")
