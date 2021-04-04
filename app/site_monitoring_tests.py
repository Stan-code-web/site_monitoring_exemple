import unittest
from site_monitoring import WebSiteStatusResult

class WebSiteStatusResultTest(unittest.TestCase):
    def test_statusToString_should_return_up_when_status_true(self):
        webSiteStatus = WebSiteStatusResult(True, -1, '')
        self.assertEqual(webSiteStatus.statusToString(), 'up')

    def test_statusToString_should_return_down_when_status_false(self):
        webSiteStatus = WebSiteStatusResult(False, -1, '')
        self.assertEqual(webSiteStatus.statusToString(), 'down')

if __name__ == '__main__':
    unittest.main()