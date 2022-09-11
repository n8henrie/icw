"""Converts csv files to ics files."""

import codecs
import csv
import typing as t
import uuid
from collections import Counter
from datetime import datetime, timedelta

import chardet
from icalendar import Calendar, Event, LocalTimezone
from werkzeug.datastructures import FileStorage

from icw import app

app.logger.debug("Starting converter in debug mode.")


class BaseICWError(Exception):
    """Base class for icw errors."""

    def __str__(self) -> str:
        """Pretty error string."""
        return f"{self.__class__.__name__}: {self.args[0]}"


class HeadersError(Exception):
    """Error with headers."""


class DatetimeFormatError(BaseICWError):
    """Error in input datetime format."""


class ContentError(BaseICWError):
    """Error in the body of the input data."""


def unicode_csv_reader(
    upfile: FileStorage, **kwargs: t.Any
) -> t.Iterable[list[str]]:
    """Workaround to decode data prior to passing to CSV module."""
    updata = upfile.read()

    # strip out BOM if present
    if updata.startswith(codecs.BOM_UTF8):
        idx = len(codecs.BOM_UTF8)
        updata = updata[idx:]

    # splitlines lets us respect universal newlines
    def line_decoder(updata: bytes) -> t.Iterable[str]:
        for line in updata.splitlines():
            try:
                line_str = line.decode()
            except UnicodeDecodeError:
                encoding = chardet.detect(updata)["encoding"]
                app.logger.warning(
                    f"Had UnicodeDecodeError, now trying with {encoding}"
                )
                # Retry the line, uncaught exception if still not right
                line_str = line.decode(encoding)
            yield line_str

    yield from csv.reader(line_decoder(updata), **kwargs)


def check_headers(headers: list[str]) -> list[str]:
    """Ensure sure that all headers are exactly correct.

    This ensures the headers will be recognized as the necessary keys.
    """
    headers = [header.strip() for header in headers]
    valid_keys = [
        "End Date",
        "Description",
        "All Day Event",
        "Start Time",
        "Private",
        "End Time",
        "Location",
        "Start Date",
        "Subject",
    ]

    if not sorted(headers) == sorted(valid_keys):
        app.logger.info(
            "Problem in the check_headers function. "
            f"Headers: {', '.join(headers)}"
        )
        errmsg = "Something isn't right with the headers."
        try:
            # bool(0) is False
            extras = Counter(headers) - Counter(valid_keys)
            missing = set(valid_keys) - set(headers)
            if extras:
                extras_str = ", ".join(extras.elements())
                errmsg += f" Extra or misspelled keys: {extras_str}."
            if missing:
                missing_str = ", ".join(missing)
                errmsg += f" Missing keys: {missing_str}."
        except Exception as e:
            app.logger.exception(e)

        raise HeadersError(errmsg)
    return headers


def clean_spaces(
    csv_dict: t.Iterable[dict[str, str]]
) -> t.Iterable[dict[str, str | None]]:
    """Clean trailing spaces from the dictionary values.

    Trailing spaces can break my datetime patterns.
    """
    yield from (
        {k: (v.strip() if v else None) for k, v in row.items()}
        for row in csv_dict
    )


def check_dates_and_times(
    start_date: str | None,
    start_time: str | None,
    end_date: str | None,
    end_time: str | None,
    all_day: bool | None,
    rownum: int | None,
) -> None:
    """Check the dates and times to make sure everything is kosher."""
    app.logger.debug("Date checker started.")

    # Gots to have a start date, no matter what.
    if start_date in ["", None]:
        app.logger.error(f"Missing a start date at row {rownum}")
        errmsg = "Missing a start date"
        try:
            errmsg += f" around row number {rownum}."
        except Exception:
            pass
        raise DatetimeFormatError(errmsg)

    for date in [start_date, end_date]:
        if date not in ["", None]:
            try:
                datetime.strptime(date, "%m/%d/%Y")
            except ValueError as e:
                errmsg = (
                    f"Something isn't right with a date in row {rownum}. "
                    "Make sure you're using MM/DD/YYYY format."
                )
                try:
                    bad_date = e.args[0].split("'")[1]
                    errmsg += " Problematic date: " + bad_date
                except Exception:
                    pass

                raise DatetimeFormatError(errmsg) from e

    for time in [start_time, end_time]:
        if time not in ["", None]:
            try:
                time = time.replace(" ", "")
                if time[-2:].lower() in ["am", "pm"]:
                    datetime.strptime(time, "%I:%M%p")
                else:
                    datetime.strptime(time, "%H:%M")
            except ValueError as e:
                errmsg = (
                    "Something isn't right with a time in row {rownum}. "
                    "Make sure you're using either '1:00 PM' or '13:00' "
                    "format."
                )
                try:
                    bad_time = e.args[0].split("'")[1]
                    errmsg += " Problematic time: " + bad_time
                except Exception:
                    pass

                raise DatetimeFormatError(errmsg) from e

    if all_day is None or all_day.lower() != "true":
        if not (start_time and end_time):
            app.logger.error(
                "Missing a required time field in a non-all_day "
                "event on date: {}.".format(start_date)
            )
            errmsg = (
                'Unless an event is "all day," it needs both a start '
                "and end time. Double check row {rownum}."
            )
            raise DatetimeFormatError(errmsg)

    app.logger.debug("Date checker ended.")


def convert(upfile: t.IO) -> bytes:
    """Convert the file."""
    breakpoint()
    reader_builder = unicode_csv_reader(upfile, skipinitialspace=True)

    reader_list = list(reader_builder)

    # Check for correct headers before we spend the time to go through
    # the whole file
    headers = check_headers(reader_list[0])
    app.logger.debug("Verified headers: {}".format(", ".join(headers)))

    raw_reader = [dict(zip(headers, values)) for values in reader_list[1:]]
    reader = clean_spaces(raw_reader)

    # Start calendar file
    cal = Calendar()
    cal.add("prodid", "n8henrie.com")
    cal.add("X-WR-CALNAME", "Imported Calendar")
    cal.add("version", "2.0")

    # Write the clean list of dictionaries to events.
    # rownum starts at 2 to match the spreadsheet numbering.
    for rownum, row in enumerate(reader, start=2):
        app.logger.debug("Event {} started, contents:\n{}".format(rownum, row))

        # No blank subjects, skip row if subject is None or ''
        if row.get("Subject", "") in ["", None]:
            continue

        event = Event()
        event.add("summary", row["Subject"])

        # If marked as an "all day event" ignore times. If start and end date
        # are the same or if end date is blank, default to a single 24-hour
        # event.

        check_dates_and_times(
            start_date=row.get("Start Date"),
            start_time=row.get("Start Time"),
            end_date=row.get("End Date"),
            end_time=row.get("End Time"),
            all_day=row.get("All Day Event"),
            rownum=rownum,
        )

        # `{}.get('nothere', '') == ''`, but
        # `{'nothere': None}.get('nothere', '') == None`
        if (ade := row.get("All Day Event")) and ade.lower() == "true":

            # All-day events will not be marked as 'busy'
            event.add("transp", "TRANSPARENT")

            dtstart = datetime.strptime(row["Start Date"], "%m/%d/%Y")
            event.add("dtstart", dtstart.date())
            if row.get("End Date") in ["", None]:
                dtend = dtstart + timedelta(days=1)
                event.add("dtend", dtend.date())
            else:
                dtend = datetime.strptime(row["End Date"], "%m/%d/%Y")
                dtend += timedelta(days=1)
                event.add("dtend", dtend.date())

        # Continue processing events not marked as "all day" events.
        else:

            # Events with times should be 'busy' by default
            event.add("transp", "OPAQUE")

            # Get rid of spaces
            # Note: Must have both start and end times if not all_day, already
            # checked
            row["Start Time"] = row["Start Time"].replace(" ", "")
            row["End Time"] = row["End Time"].replace(" ", "")

            # Allow either 24 hour time or 12 hour + am/pm
            if row["Start Time"][-2:].lower() in ["am", "pm"]:
                dt_string = "%m/%d/%Y%I:%M%p"
            else:
                dt_string = "%m/%d/%Y%H:%M"
            dtstart = datetime.strptime(
                row["Start Date"] + row["Start Time"], dt_string
            )
            event.add("dtstart", dtstart)

            # Allow blank end dates (assume same day)
            if row.get("End Date") in ["", None]:
                row["End Date"] = row["Start Date"]

            if row["End Time"][-2:].lower() in ["am", "pm"]:
                dt_string = "%m/%d/%Y%I:%M%p"
            else:
                dt_string = "%m/%d/%Y%H:%M"
            dtend = datetime.strptime(
                row["End Date"] + row["End Time"], dt_string
            )
            event.add("dtend", dtend)

        for tag in ["Description", "Location"]:
            if row.get(tag):
                event.add(tag, row[tag])

        event.add(
            "dtstamp", datetime.replace(datetime.now(), tzinfo=LocalTimezone())
        )

        # n8henrie.com tag at the end not used for tracking, just
        # personalization
        event["uid"] = f"{uuid.uuid4()}___n8henrie.com"

        cal.add_component(event)
        rownum += 1

    if len(cal.subcomponents) > 0:
        final_file = cal.to_ical()
    else:
        raise ContentError("Final calendar was empty.")

    return final_file
