"""Tests for files that should fail."""

import glob
import os

import pytest

from icw.converter import (
    ContentError,
    convert,
    DatetimeFormatError,
    HeadersError,
)


def prefix(myfile) -> str:
    """Prefixes the file path for individual test files."""
    return os.path.join("tests", "fail_files", myfile)


def test_fail_blank_subject(client):
    """Fail if subject is blank or consists only of spaces."""
    for blank_subject in [
        "fail_blank_subject_spaces.csv",
        "fail_blank_subject.csv",
    ]:
        with open(prefix(blank_subject), "rb") as infile:

            # Should raise ContentError since blank subject will be skipped
            # and it's the only event.

            with pytest.raises(ContentError):
                return convert(infile)


def test_fail_dateformat(client):
    """Fail with an improper date format."""
    for date_format in [
        "fail_2_digit_years.csv",
        "fail_missing_startdate.csv",
    ]:
        with open(prefix(date_format), "rb") as infile:
            with pytest.raises(DatetimeFormatError):
                return convert(infile)


def test_fail_timeformat(client):
    """Fail with an improper time format."""
    for time_format in ["fail_timeformat.csv", "fail_missing_endtime.csv"]:
        with open(prefix(time_format), "rb") as infile:
            with pytest.raises(DatetimeFormatError):
                return convert(infile)


def test_fail_headers(client):
    """Test a few conditions with improper headers."""
    fail_headers_files = glob.glob("tests/fail_files/fail_*_header.csv")
    for fail_headers_file in fail_headers_files:
        with open(fail_headers_file, "rb") as infile:
            with pytest.raises(HeadersError):
                return convert(infile)
