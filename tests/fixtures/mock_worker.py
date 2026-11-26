from awdac.reference import ReferenceWorker

class MockWorker(ReferenceWorker):
    def __init__(self):
        self.advice = []

    def create(self, parent, context, recommendation):
        self.advice.append(recommendation)
        return super().create(parent, context, recommendation)
