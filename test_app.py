import os
import unittest
from app import response

class AppTest(unittest.TestCase):
    def test_commit_identity(self):
        os.environ['APP_COMMIT'] = 'a' * 40
        self.assertEqual(response()['commit'], 'a' * 40)
        self.assertEqual(response()['application'], 'Jenkins CI/CD Lab')

if __name__ == '__main__':
    unittest.main()
