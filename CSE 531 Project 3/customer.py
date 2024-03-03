import grpc
import time

import banking_system_pb2
import banking_system_pb2_grpc
from constants import BASE_PORT
from logging_util import setup_logger, log


class Customer:

    def __init__(self, id, events):
        # unique ID of the Customer
        self.id = id
        # events from the inputs
        self.events = events
        # a list of received messages used for debugging purpose
        self.recd_msgs = list()
        # pointer for the stub
        self.stub = None

    # def create_stub(self, corresponding_branch_port):
    #     channel = grpc.insecure_channel("localhost:" + str(corresponding_branch_port))
    #     stub = banking_system_pb2_grpc.TransferStub(channel)
    #     self.stub = stub

    def execute_events(self):
        logger = setup_logger("execute_events")
        for event in self.events:
            amount = 0
            propagate = True
            if event["interface"] == "query":
                propagate = False
            else:
                amount = event["money"]

            operation_type = event["interface"]

            branch_id = event["branch"]
            port = BASE_PORT + branch_id
            channel = grpc.insecure_channel("localhost:" + str(port))
            stub = banking_system_pb2_grpc.TransferStub(channel)

            response = stub.message_delivery(
                banking_system_pb2.Transfer_Request(
                    id=self.id,
                    operation_type=operation_type,
                    amount=amount,
                    propagate=propagate,
                )
            )

            recv = list()
            msg = {"interface": response.interface, "branch": branch_id}  # , "result": response.result}
            if event["interface"] == "query":
                msg["balance"] = response.balance
            else:
                msg["result"] = response.result
            recv.append(msg)
            # print(msg)

            final_msg = {"id": self.id, "recv": recv}
            print(final_msg)
            self.recd_msgs.append(final_msg)
            # log(logger, f"\nCustomer \nid: {self.id} \nresponse: {response}")

    def get_customer_results(self):
        # return {"id": self.id, "recv": self.recd_msgs}
        return self.recd_msgs
