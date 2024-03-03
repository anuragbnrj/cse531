import grpc
import time

import banking_system_pb2
import banking_system_pb2_grpc
from logging_util import setup_logger, log


class Customer:

    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the inputs
        self.events = events
        # a list of received messages used for debugging purpose
        self.messages = list()
        # pointer for the stub
        self.stub = None
        # logical clock of the customer process
        self.logical_clock = 1

    def create_stub(self, corresponding_branch_port):
        channel = grpc.insecure_channel("localhost:" + str(corresponding_branch_port))
        stub = banking_system_pb2_grpc.TransferStub(channel)
        self.stub = stub

    def execute_events(self):
        logger = setup_logger("execute_events")
        for event in self.events:
            amount = 0
            propagate = True
            if event["interface"] == "query":
                propagate = False
            else:
                amount = event["money"]

            msg = {
                "customer-request-id": event["customer-request-id"],
                "logical_clock": self.logical_clock,
                "interface": event["interface"],
                "comment": "event_sent from customer " + str(self.id)
            }
            self.messages.append(msg)

            obj = banking_system_pb2.Transfer_Request(
                id=self.id,
                interface=event["interface"],
                amount=amount,
                propagate=propagate,
                customer_request_id=event["customer-request-id"],
                logical_clock=self.logical_clock
            )
            self.stub.message_delivery(obj)

            # if event["interface"] == "query":
            #     msg["balance"] = response.balance

            # self.logical_clock = max(self.logical_clock, response.logical_clock) + 1
            self.logical_clock = self.logical_clock + 1

            # log(logger, f"\nCustomer \nid: {self.id} \nresponse: {response}")

    def get_customer_messages(self):
        return {"id": self.id, "type": "customer", "events": self.messages}
