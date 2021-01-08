#!/usr/bin/env python
"""
Api tests

these tests use the requests package however similar requests can be made with curl

e.g.
data = '{"key":"value"}'
curl -X POST -H "Content-Type: application/json" -d "%s" http://localhost:8080/predict'%(data)
"""

import sys
import os
import unittest
import requests
import re
from ast import literal_eval
import numpy as np

port = 8080

try:
    requests.post('http://0.0.0.0:{}/test'.format(port))
    server_available = True
except:
    server_available = False
    
## test class for the main window function
class ApiTest(unittest.TestCase):
    """
    Test the essential API functionality
    """

    @unittest.skipUnless(server_available,"local server is not running")
    def test_train(self):
        """
        test the train functionality
        """
      
        request_json = {'mode':'test'}
        r = requests.post('http://0.0.0.0:{}/train'.format(port),json=request_json)
        train_complete = re.sub("\W+","",r.text)
        self.assertEqual(train_complete,'true')
    
    @unittest.skipUnless(server_available,"local server is not running")
    def test_predict_empty(self):
        """
        ensure appropriate failure types
        """
    
        ## provide no data at all 
        r = requests.post('http://0.0.0.0:{}/predict'.format(port))
        self.assertEqual(re.sub('\n|"','',r.text),"[]")

        ## provide improperly formatted data
        r = requests.post('http://0.0.0.0:{}/predict'.format(port),json={"key":"value"})     
        self.assertEqual(re.sub('\n|"','',r.text),"[]")
    
    @unittest.skipUnless(server_available,"local server is not running")
    def test_predict(self):
        """
        test the predict functionality
        """

        query_data = {'country': "all",
                      'year': "2018",
                      'month': "12",
                      'day': '12'
        }

        #query_type = 'dict'
        #request_json = {'query':query_data,'type':query_type,'mode':'test'}

        r = requests.post('http://0.0.0.0:{}/predict'.format(port),json=query_data)
        self.assertTrue(r)
### Run the tests
if __name__ == '__main__':
    unittest.main()
