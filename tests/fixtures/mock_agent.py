from awdac.schemas import Proposal

class MockAgent:
    def propose(self, context):
        return Proposal("Retain initialization", "Mock advice")
