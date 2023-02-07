import unittest
import route as Wrapper

print(Wrapper)

class TestRouteApi(unittest.TestCase):
    def test_api_ping(self):
        """Makes sure the API is up & token valid"""
        response = Wrapper.ping()
        self.assertEqual(response.status_code,200)
        body = response.json()
        self.assertFalse('error' in body)

    def barrier_reactive(self):
        """Barrier polygon should change route"""
        pass

if __name__ == '__main__':
    unittest.main()