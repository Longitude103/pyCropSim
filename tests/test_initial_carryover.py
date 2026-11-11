"""Tests for INITIAL.DAT handling and year-to-year soil state carryover.

Run from the repo root with:  python -m unittest discover -s tests -t .
"""

import io
import os
import tempfile
import types
import unittest

import SIM
from Data.Crop import CropId
from Files.InitialFile import InitialFile
from HelperIO import ReadFloats
from Subroutines import CROPSIM


class CarryoverTest(unittest.TestCase):
    """End-of-year state must become the next year's starting state."""

    def setUp(self):
        self._saved = {k: getattr(SIM, k) for k in (
            "InitialData", "Sim", "THETA", "RESIDUE", "LIVECROP", "SNOTMP", "SNOH2O", "SOILT")}
        SIM.InitialData = InitialFile()
        SIM.Sim = types.SimpleNamespace(CROP=CropId(1))

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(SIM, k, v)

    def test_end_of_year_state_is_loaded_next_year(self):
        CROPSIM.loadInitialData()
        SIM.THETA = [0.30 + i / 100 for i in range(10)]
        SIM.SOILT = [-2.5 + i for i in range(10)]
        SIM.RESIDUE, SIM.LIVECROP, SIM.SNOTMP, SIM.SNOH2O = 1234.5, True, 20.1, 0.75
        CROPSIM.rewriteInitFile()

        # Clobber the working state, as the next simulated year would.
        SIM.THETA, SIM.SOILT = [0.0] * 10, [0.0] * 10
        CROPSIM.loadInitialData()

        self.assertEqual(SIM.THETA, [0.30 + i / 100 for i in range(10)])
        self.assertEqual(SIM.SOILT, [-2.5 + i for i in range(10)])
        self.assertEqual(SIM.OLDCRP, CropId(1))
        self.assertEqual(SIM.OLDRES, 1234.5)
        self.assertTrue(SIM.LIVECROP)
        self.assertEqual((SIM.SNOTMP, SIM.SNOH2O), (20.1, 0.75))

    def test_carryover_is_a_copy_not_an_alias(self):
        CROPSIM.loadInitialData()
        SIM.THETA[0] = 0.999  # in-place change during a simulated year
        self.assertNotEqual(SIM.InitialData.THETA[0], 0.999)
        CROPSIM.rewriteInitFile()
        SIM.THETA[0] = 0.111
        self.assertEqual(SIM.InitialData.THETA[0], 0.999)


class InitialFileFormatTest(unittest.TestCase):
    """INITIAL.DAT must round-trip in the original CROPSIM layout."""

    def _roundtrip(self, writer):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "INITIAL.DAT")
            writer(path)
            with open(path) as f:
                text = f.read()
            return text, InitialFile(path)

    def _state(self):
        data = InitialFile()
        data.THETA = [0.123, 0.234, 0.345, 0.111, 0.222, 0.333, 0.301, 0.302, 0.303, 0.304]
        data.CROP = CropId(1)
        data.RESIDUE = 2500.0
        data.LIVECROP = True
        data.SNOTMP = -3.4
        data.SNOH2O = 0.25
        data.SOILT = [-1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        return data

    def assertSameState(self, read, expected):
        self.assertEqual(read.THETA, expected.THETA)
        self.assertEqual(int(read.CROP), int(expected.CROP))
        self.assertEqual(read.RESIDUE, expected.RESIDUE)
        self.assertEqual(read.LIVECROP, expected.LIVECROP)
        self.assertEqual(read.SNOTMP, expected.SNOTMP)
        self.assertEqual(read.SNOH2O, expected.SNOH2O)
        self.assertEqual(read.SOILT, expected.SOILT)

    def test_initialfile_save_roundtrip(self):
        data = self._state()
        text, read = self._roundtrip(data.saveToFile)
        # FORMAT 476: 10(2X,F6.3)
        self.assertEqual(text.splitlines()[0], "".join(f"  {t:6.3f}" for t in data.THETA))
        self.assertSameState(read, data)

    def test_sim_write_initial_file_roundtrip(self):
        data = self._state()
        saved = {k: getattr(SIM, k) for k in ("Sim", "THETA", "RESIDUE", "LIVECROP",
                                              "SNOTMP", "SNOH2O", "SOILT")}
        try:
            SIM.Sim = types.SimpleNamespace(CROP=data.CROP)
            SIM.THETA, SIM.RESIDUE, SIM.LIVECROP = data.THETA, data.RESIDUE, data.LIVECROP
            SIM.SNOTMP, SIM.SNOH2O, SIM.SOILT = data.SNOTMP, data.SNOH2O, data.SOILT
            text, read = self._roundtrip(SIM.writeInitialFile)
        finally:
            for k, v in saved.items():
                setattr(SIM, k, v)
        self.assertNotIn(":4.3f", text)
        self.assertNotIn(":5.1f", text)
        self.assertSameState(read, data)


class ReadFloatsTest(unittest.TestCase):

    def test_negative_values_keep_their_sign(self):
        self.assertEqual(ReadFloats(io.StringIO("  -1.5   2.0  -0.25\n"), 3), [-1.5, 2.0, -0.25])

    def test_lone_dash_is_ignored(self):
        self.assertEqual(ReadFloats(io.StringIO("--- 1.0 - 2.0\n"), 2), [1.0, 2.0])


if __name__ == "__main__":
    unittest.main()
