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

from constants import BASE_PORT, THREAD_POOL_MAX_WORKERS, OUTPUT_FILE_PATH
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
    log(LOGGER, "finished stop_branches")


def start_customer(customer):
    log(LOGGER, f"Executing events for customer with id: {customer.id}")
    customer.execute_events()
    customer_result = customer.get_customer_results()
    previous_results = json.load(open(OUTPUT_FILE_PATH))

    previous_results.append(customer_result)

    with open(OUTPUT_FILE_PATH, 'w') as json_file:
        json_data = json.dumps(previous_results)
        json_file.write(json_data)


def start_customers(transactions):
    for transaction in transactions:
        if transaction["type"] == "customer":
            customer = Customer(transaction["id"], transaction["events"])
            customer.create_stub(BASE_PORT + customer.id)
            CUSTOMERS.append(customer)

    for customer in CUSTOMERS:
        customer_process = multiprocessing.Process(name=f"Customer-{customer.id}", target=start_customer,
                                                   args=(customer,))
        customer_process.start()

        # Waiting for the customer process to finish because
        # customers should execute sequentially according to project document
        customer_process.join()


def write_initial_data_to_output_file(output_file_path):
    with open(output_file_path, 'w') as json_file:
        json_data = json.dumps([])
        json_file.write(json_data)


if __name__ == "__main__":
    log(LOGGER, "Starting main")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--input_file")
    args = argument_parser.parse_args()

    write_initial_data_to_output_file(OUTPUT_FILE_PATH)

    try:
        transactions_input = json.load(open(args.input_file))

        start_branches(transactions_input)

        start_customers(transactions_input)

        stop_branches()

    except FileNotFoundError:
        log(LOGGER, "Could NOT find input file")
    except json.decoder.JSONDecodeError:
        log(LOGGER, "Could NOT decode JSON file")
