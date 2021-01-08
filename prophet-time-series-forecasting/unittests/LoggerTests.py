#!/usr/bin/env python

import os
import csv
import unittest
import pandas as pd
from logger import update_train_log, update_predict_log

class LoggerTest(unittest.TestCase):
    """
    Test the essential logger functionality
    """
        
    def test_log_creation(self):
        """
        Ensure log file is created
        """

        log_file = os.path.join("logs","train-test.log")
        if os.path.exists(log_file):
            os.remove(log_file)
        
        ## update the log
        data_shape = (100,10)
        runtime = "00:00:01"
        model_version = 0.1
        model_version_note = "test model"
        
        update_train_log(data_shape, runtime,
                         model_version, model_version_note ,test=True)

        self.assertTrue(os.path.exists(log_file))
        
    def test_log_training(self):
        """
        Ensure that content can be retrieved from log file
        """

        log_file = os.path.join("logs","train-test.log")
        
        ## update the log
        data_shape = (100,10)
        runtime = "00:00:01"
        model_version = 0.1
        model_version_note = "test model"
        
        update_train_log(data_shape, runtime,
                         model_version, model_version_note ,test=True)

        df = pd.read_csv(log_file)
        self.assertTrue(os.path.exists(log_file))
                

    def test_log_prediction(self):
        """
        Ensure that content can be retrieved from log file
        """

        log_file = os.path.join("logs","predict-test.log")

        ## update the log
        y_pred = 100
        runtime = "00:00:02"
        model_version = 0.1
        model_note="Prophet"
        test=True
        update_predict_log(y_pred,runtime,model_version, model_note, test)
        
        self.assertTrue(os.path.exists(log_file))

### Run the tests
if __name__ == '__main__':
    unittest.main()
      
