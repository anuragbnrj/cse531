import json
import sys

if len(sys.argv) < 2:
    print("Input argument?")
    exit()

filename = sys.argv[1]


# Define a function to check if events meet the specified conditions
def check_event_conditions(event, branch_data):
    global total_events  # Use the global variable
    total_events += 1
    current_clock = event["logical_clock"]
    branch_logical_clock, propagate_event_occurred = branch_data

    # Check if logical clock is incremental within the same branch
    if current_clock <= branch_logical_clock:
        return False

    print(f"Customer Request Id: {event['customer-request-id']}\t  event interface: {event['interface']}\t propagate_event_occurred: {propagate_event_occurred} ")
    # Check if non-propagate events are before propagate events
    if not event["interface"].startswith("propagate_") and propagate_event_occurred:
        return False

    if event["interface"].startswith("propagate_"):
        propagate_event_occurred = True
        print(f"Customer Request Id: {event['customer-request-id']}\t  event interface: {event['interface']}\t propagate_event_occurred: {propagate_event_occurred} ")

    branch_logical_clock = current_clock

    return True


# Initialize a global variable for total events
total_events = 0

# Read the JSON data from a file
with open(filename, 'r') as file:
    json_data = file.read()

# Parse the JSON data
parsed_data = json.loads(json_data)

# Create a dictionary to group events by branch ID
branch_events = {}

# Initialize counters for correct and incorrect events
correct_events = 0
incorrect_events = 0

# Group the events by branch ID and perform checks
for branch_data in parsed_data:
    branch_id = branch_data["id"]
    events = branch_data["events"]

    if branch_id not in branch_events:
        branch_events[branch_id] = {"events": events, "logical_clock": -1, "propagate_event_occurred": False}

    # Check events within each branch
    for event in events:
        branch_data = (branch_events[branch_id]["logical_clock"], branch_events[branch_id]["propagate_event_occurred"])
        if check_event_conditions(event, branch_data):
            print(f"Branch ID: {branch_id}, Event ID: {event['customer-request-id']} - Conditions Met (OK)")
            correct_events += 1
        else:
            print(f"Branch ID: {branch_id}, Event ID: {event['customer-request-id']} - Conditions Not Met (Error)")
            incorrect_events += 1

        # Update the logical clock
        branch_events[branch_id]["logical_clock"] = event["logical_clock"]

# Print the total number of events

# Print a summary of correct and incorrect events
print("\nSummary:")
print(f"\nTotal Events: {total_events}")
print(f"Correct Events: {correct_events}")
print(f"Incorrect Events: {incorrect_events}")
