

class MockTable:

    def __init__(self, query_result: list):
        self.query_result = query_result

    def put_item(self, **kwargs):
        pass
        
    def query(self, **kwargs) -> dict:
        return {'Items': self.query_result, 'Count': len(self.query_result)}
    
    def scan(self) -> dict:
        return {'Items': self.query_result, 'Count': len(self.query_result)}

class MockBoto3:

    def __init__(self, mockTable: MockTable):
        self.mockTable = mockTable

    def Table(self, *args):
        return self.mockTable
    