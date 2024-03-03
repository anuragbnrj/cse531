import time

import grpc
import banking_system_pb2
import banking_system_pb2_grpc
from constants import BASE_PORT, SLEEP_BEFORE_QUERYING
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
        # a list of received messages used for debugging purpose
        self.received_messages = list()
        # logical clock of the branch process
        self.clock = 1

    def populate_stub_list(self):
        for branch_id in self.branch_ids:
            if branch_id != self.id:
                port = BASE_PORT + branch_id
                channel = grpc.insecure_channel("localhost:" + str(port))
                stub = banking_system_pb2_grpc.TransferStub(channel)
                self.stub_list.append(stub)

    def message_delivery(self, request, context):
        self.received_messages.append(request)
        operation_type = request.operation_type

        status = "success"
        balance = 0
        if operation_type == "query":
            status = self.query()
            balance = self.balance

        if operation_type == "deposit":
            status = self.deposit(request.amount)

        if operation_type == "withdraw":
            status = self.withdraw(request.amount)

        response = banking_system_pb2.Transfer_Response(
            interface=operation_type,
            result=status,
            balance=balance
        )

        if request.propagate:
            if operation_type == "deposit":
                self.propagate_deposit(request.amount)

            if operation_type == "withdraw":
                self.propagate_withdraw(request.amount)

        return response

    def query(self):
        time.sleep(SLEEP_BEFORE_QUERYING)
        return "success"

    def deposit(self, amount):
        if amount <= 0:
            return "invalid"

        self.balance = self.balance + amount
        return "success"

    def propagate_deposit(self, amount):
        operation_type = "deposit"

        for stub in self.stub_list:
            stub.message_delivery(
                banking_system_pb2.Transfer_Request(
                    id=self.id,
                    operation_type=operation_type,
                    amount=amount,
                    propagate=False
                )
            )

    def withdraw(self, amount):
        if amount <= 0:
            return "invalid"

        if amount > self.balance:
            return "invalid"

        self.balance = self.balance - amount
        return "success"

    def propagate_withdraw(self, amount):
        operation_type = "withdraw"

        for stub in self.stub_list:
            stub.message_delivery(
                banking_system_pb2.Transfer_Request(
                    id=self.id,
                    operation_type=operation_type,
                    amount=amount,
                    propagate=False
                )
            )
