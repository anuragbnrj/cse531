import json
import time

import grpc
import banking_system_pb2
import banking_system_pb2_grpc
from constants import *
from logging_util import setup_logger, log


class Branch(banking_system_pb2_grpc.TransferServicer):

    def __init__(self, id, balance, branch_ids):
        # unique ID of the Branch
        self.id = id
        # replica of the Branch's balance
        self.balance = balance
        # the list of process IDs of the branches
        self.branch_ids = branch_ids
        # the list of Client stubs to communicate with the branches
        self.stub_list = list()
        # the map of Client stubs and their ids to be used for the generating the comments in messages
        self.stub_map = dict()
        # a list of received messages used for debugging purpose
        self.messages = list()
        # logical clock of the branch process
        self.logical_clock = 1

    def populate_stub_list(self):
        for branch_id in self.branch_ids:
            if branch_id != self.id:
                port = BASE_PORT + branch_id
                channel = grpc.insecure_channel("localhost:" + str(port))
                stub = banking_system_pb2_grpc.TransferStub(channel)
                self.stub_list.append(stub)
                self.stub_map[stub] = branch_id

    def message_delivery(self, request, context):
        self.logical_clock = max(self.logical_clock, request.logical_clock) + 1

        propagate = request.propagate
        interface = request.interface
        customer_request_id = request.customer_request_id
        amount = request.amount

        message = {
            "customer-request-id": request.customer_request_id,
            "logical_clock": self.logical_clock,
        }
        if propagate:
            message["interface"] = interface
            message["comment"] = "event_recv from customer " + str(request.id)
        else:
            message["interface"] = "propagate_" + interface
            message["comment"] = "event_recv from branch " + str(request.id)
        # self.messages.append(message)
        self.write_branch_message_to_file(message)

        status = "success"
        balance = 0
        if interface == "query":
            status = self.query()
            balance = self.balance

        if interface == "deposit":
            status = self.deposit(amount)

        if interface == "withdraw":
            status = self.withdraw(request.amount)

        response = banking_system_pb2.Transfer_Response(
            interface=interface,
            result=status,
            balance=balance
        )

        if request.propagate:
            self.propagate_interface(interface, request.amount, customer_request_id)
            # if interface == "deposit":
            #     self.propagate_deposit(request.amount, request["customer_request_id"])
            #
            # if interface == "withdraw":
            #     self.propagate_withdraw(request.amount, request["customer_request_id"])

        return response

    def query(self):
        time.sleep(SLEEP_BEFORE_QUERYING)
        return "success"

    def deposit(self, amount):
        if amount <= 0:
            return "invalid"

        self.balance = self.balance + amount
        return "success"

    def withdraw(self, amount):
        if amount <= 0:
            return "invalid"

        if amount > self.balance:
            return "invalid"

        self.balance = self.balance - amount
        return "success"

    def propagate_interface(self, interface, amount, customer_request_id):

        for stub in self.stub_list:
            self.logical_clock = self.logical_clock + 1

            message = {
                "customer-request-id": customer_request_id,
                "logical_clock": self.logical_clock,
                "interface": "propagate_" + interface,
                "comment": "event_sent to branch " + str(self.stub_map[stub])
            }
            # self.messages.append(message)
            self.write_branch_message_to_file(message)

            stub.message_delivery(
                banking_system_pb2.Transfer_Request(
                    id=self.id,
                    interface=interface,
                    amount=amount,
                    propagate=False,
                    customer_request_id=customer_request_id,
                    logical_clock=self.logical_clock
                )
            )

    def write_branch_message_to_file(self, message):
        # Write branch data to file
        first_event_for_curr_branch = True
        all_branch_outputs = json.load(open(BRANCH_EVENTS_OUTPUT_FILE_PATH))
        for branch_output in all_branch_outputs:
            if self.id == branch_output["id"]:
                branch_output["events"].append(message)
                first_event_for_curr_branch = False
                break

        if first_event_for_curr_branch:
            branch_output = {
                "id": self.id,
                "type": "branch",
                "events": [message]
            }
            all_branch_outputs.append(branch_output)

        with open(BRANCH_EVENTS_OUTPUT_FILE_PATH, 'w') as json_file:
            json_data = json.dumps(all_branch_outputs)
            json_file.write(json_data)

    # def propagate_withdraw(self, amount, customer_request_id):
    #     interface = "withdraw"
    #
    #     for stub in self.stub_list:
    #         self.logical_clock = self.logical_clock + 1
    #
    #         message = {
    #             "customer-request-id": customer_request_id,
    #             "logical_clock": self.logical_clock,
    #             "interface": "propagate_" + interface,
    #             "comment": "event_sent to branch"
    #         }
    #         self.messages.append(message)
    #         stub.message_delivery(
    #             banking_system_pb2.Transfer_Request(
    #                 id=self.id,
    #                 interface=interface,
    #                 amount=amount,
    #                 propagate=False,
    #                 customer_request_id=customer_request_id,
    #                 logical_clock=self.logical_clock
    #             )
    #         )

    def get_branch_messages(self):
        return {"id": self.id, "type": "branch", "events": self.messages}
