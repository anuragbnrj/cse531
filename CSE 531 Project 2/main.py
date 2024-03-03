import argparse
import json
import multiprocessing
import threading
import time
from concurrent import futures

import grpc

import banking_system_pb2_grpc
from branch import Branch
from customer import Customer

# from constants import BASE_PORT, THREAD_POOL_MAX_WORKERS, OUTPUT_FILE_PATH
from constants import *
from logging_util import setup_logger, log

BRANCHES = list()
BRANCH_IDS = list()
BRANCH_SERVER_THREADS = list()

CUSTOMERS = list()
CUSTOMER_PROCESSES = list()

PORT_LIST = list()

FINAL_RESULT = list()

LOGGER = setup_logger("main")


def start_branch(branch):
    port = BASE_PORT + branch.id

    grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS))
    banking_system_pb2_grpc.add_TransferServicer_to_server(branch, grpc_server)

    grpc_server.add_insecure_port("[::]:" + str(port))
    grpc_server.start()

    log(LOGGER, f"Server started for branch with id - {branch.id} at port: {port}")
    grpc_server.wait_for_termination()


def start_branches(transactions):
    for transaction in transactions:
        if transaction["type"] == "branch":
            BRANCH_IDS.append(transaction["id"])

    for transaction in transactions:
        if transaction["type"] == "branch":
            branch = Branch(transaction["id"], transaction["balance"], BRANCH_IDS)
            BRANCHES.append(branch)

    for branch in BRANCHES:
        branch.populate_stub_list()
        server_thread = multiprocessing.Process(name=f"Branch-{branch.id}", target=start_branch, args=(branch,))
        BRANCH_SERVER_THREADS.append(server_thread)
        server_thread.start()

    # Wait for the branch servers to be online
    time.sleep(2.0)


def stop_branches():
    log(LOGGER, "inside stop_branches")
    log(LOGGER, f"Number of servers: {len(BRANCH_SERVER_THREADS)}")
    for server_thread in BRANCH_SERVER_THREADS:
        # log(LOGGER, "inside stop_branches for loop --------------")
        server_thread.terminate()
        # time.sleep(0.2)
    log(LOGGER, "finished stop_branches")


def start_customer(customer):
    log(LOGGER, f"Executing events for customer with id: {customer.id}")
    customer.execute_events()
    curr_customer_outputs = customer.get_customer_messages()

    all_customer_outputs = json.load(open(CUSTOMER_EVENTS_OUTPUT_FILE_PATH))
    all_customer_outputs.append(curr_customer_outputs)

    # log(LOGGER, customer_messages)
    with open(CUSTOMER_EVENTS_OUTPUT_FILE_PATH, 'w') as json_file:
        json_data = json.dumps(all_customer_outputs)
        json_file.write(json_data)


def start_customers(transactions):
    # lock = multiprocessing.Lock()

    for transaction in transactions:
        if transaction["type"] == "customer":
            customer = Customer(transaction["id"], transaction["customer-requests"])
            customer.create_stub(BASE_PORT + customer.id)
            CUSTOMERS.append(customer)

    for customer in CUSTOMERS:
        customer_process = multiprocessing.Process(name=f"Customer-{customer.id}", target=start_customer,
                                                   args=(customer,))
        customer_process.start()

        # Waiting for the customer process to finish
        customer_process.join()


def write_initial_data_to_output_file(output_file_path):
    with open(output_file_path, 'w') as json_file:
        json_data = json.dumps([])
        json_file.write(json_data)


def generate_combined_events_file():
    combined_events = list()

    all_customer_outputs = json.load(open(CUSTOMER_EVENTS_OUTPUT_FILE_PATH))
    for curr_customer_outputs in all_customer_outputs:
        curr_customer_events = curr_customer_outputs["events"]

        for event in curr_customer_events:
            message = event
            message["id"] = curr_customer_outputs["id"]
            message["type"] = "customer"
            combined_events.append(message)

    all_branch_outputs = json.load(open(BRANCH_EVENTS_OUTPUT_FILE_PATH))
    for curr_branch_outputs in all_branch_outputs:
        curr_branch_events = curr_branch_outputs["events"]

        for event in curr_branch_events:
            message = event
            message["id"] = curr_branch_outputs["id"]
            message["type"] = "branch"
            combined_events.append(message)

    with open(COMBINED_EVENTS_OUTPUT_FILE_PATH, 'w') as json_file:
        json_data = json.dumps(combined_events)
        json_file.write(json_data)


if __name__ == "__main__":
    log(LOGGER, "Starting main")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input_file")
    args = argument_parser.parse_args()

    # write_initial_data_to_output_file(OUTPUT_FILE_PATH)
    write_initial_data_to_output_file(CUSTOMER_EVENTS_OUTPUT_FILE_PATH)
    write_initial_data_to_output_file(BRANCH_EVENTS_OUTPUT_FILE_PATH)
    write_initial_data_to_output_file(COMBINED_EVENTS_OUTPUT_FILE_PATH)

    try:
        transactions_input = json.load(open(args.input_file))

        start_branches(transactions_input)

        start_customers(transactions_input)

        stop_branches()

        generate_combined_events_file()

    except FileNotFoundError:
        log(LOGGER, "Could NOT find input file")
    except json.decoder.JSONDecodeError:
        log(LOGGER, "Could NOT decode JSON file")
