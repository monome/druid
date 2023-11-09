#!/usr/bin/python3

import os
import sys
import logging
import unittest
from parameterized import parameterized
from subprocess import Popen, PIPE

# Point to a collection of crow scripts. Defaults to the bowery
# collection which comes with the bowering norns script.
MURDER = "/home/we/dust/code/bowering/crow"

class TestCli(unittest.TestCase):
    def test_cli_is_found(self):
        process = Popen(["druid", "--help"], stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        self.assertEqual(0, process.returncode)
        self.assertIn("Terminal interface for crow", out.decode())


class TestRun(unittest.TestCase):
    """Tests for running druid scripts from command line https://github.com/monome/druid/pull/84. Tests use script in the MURDER directory."""
    def setUp(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def test_run_without_filename_should_fail(self):
        process = Popen(["druid", "run"], text=True, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        self.assertEqual(2, process.returncode)
        self.assertIn("Error: Missing argument 'FILENAME'.", err)

    def test_run_with_missing_file_should_fail(self):
        script  = "shiny_thing.lua"
        process = Popen(["druid", "run", script], text=True, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        self.assertEqual(2, process.returncode)
        self.assertIn(f"Error: Invalid value for 'FILENAME': Path '{script}' does not exist.", err)

    def test_run_with_script_should_pass(self, script="boids.lua"):
        filename = f"{MURDER}/{script}"
        with open(filename) as fd:
            script_name = fd.readline().lstrip('--- ')
        self.logger.debug(f"Testing {script_name}")
        process = Popen(["druid", "run", filename], text=True, stdout=PIPE, stderr=PIPE)
        out, err = process.communicate()
        self.assertEqual(0, process.returncode)
        self.assertIn(f"Running: {script_name}", out)

    @parameterized.expand([f for f in os.listdir(MURDER) if f.endswith(".lua")])
    def test_run_entire_bowery_should_pass(self, script):
        self.test_run_with_script_should_pass(script)

if __name__ == '__main__':
    unittest.main()
