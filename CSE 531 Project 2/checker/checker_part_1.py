import json
import sys

if len(sys.argv) < 2:
    print("Input argument?")
    exit()

filename = sys.argv[1]
# Read the JSON data from a file
# with open('customer_events.json', 'r') as file:
with open(filename, 'r') as file:
    json_data = file.read()

# Parse the JSON data
parsed_data = json.loads(json_data)

# Initialize counters
correct_answers = 0
total_answers = 0

# Check if logical clocks are incremental for each customer
for customer_data in parsed_data:
    customer_id = customer_data["id"]
    events = customer_data["events"]
    logical_clock = 0  # Initialize logical clock for the customer
    
    print(f"Customer ID: {customer_id}")
    for event in events:
        request_id = event["customer-request-id"]
        event_logical_clock = event["logical_clock"]
        
        if event_logical_clock > logical_clock:
            print(f"  Event ID: {request_id}, Logical Clock: {event_logical_clock} (OK)")
            logical_clock = event_logical_clock
            correct_answers += 1
        else:
            print(f"  Event ID: {request_id}, Logical Clock: {event_logical_clock} (Error: Not incremental)")
        
        total_answers += 1

# Print the summary message
print(f"\nSummary: {correct_answers} out of {total_answers} answers are correct.")
