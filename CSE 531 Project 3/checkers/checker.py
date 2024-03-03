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

def compare_last_query_and_first_query(json_data):
    branch_last_query = {}
    correct = 0
    incorrect = 0
    total = 0

    for i in range(len(json_data) - 1):
        current_branch = json_data[i]["recv"][0]["branch"]
        next_branch = json_data[i + 1]["recv"][0]["branch"]

        # Check if both entries are 'query' interfaces
        if (
            json_data[i]["recv"][0].get("interface") == "query"
            and json_data[i + 1]["recv"][0].get("interface") == "query"
        ):
            # last_query_balance = branch_last_query.get(current_branch)
            
            total += 1

            last_query_balance = json_data[i]["recv"][0].get("balance")
            next_query_balance = json_data[i + 1]["recv"][0].get("balance")

            # print(f"current_branch: {current_branch}, last_query_balance: {last_query_balance}, next_query_balance: {next_query_balance}")

            # if last_query_balance is not None and last_query_balance != next_query_balance:
            if last_query_balance is not None:
                if last_query_balance != next_query_balance:
                    print(
                        f"Inconsistency detected between branch {current_branch} and branch {next_branch}: "
                        f"{last_query_balance} != {next_query_balance}"
                    )

                else:
                    correct += 1
                    print(
                        f"Consistent balance between branch {current_branch} and branch {next_branch}. Balance={next_query_balance}"
                    )
                    
            # Update last query balance
            branch_last_query[current_branch] = json_data[i]["recv"][0].get("balance")

    # score = (correct / total)
    print(f"{correct} out of {total} cross-branch query events are correct.")

    
compare_last_query_and_first_query(parsed_data)
