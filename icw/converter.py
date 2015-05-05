"""converter.py
Does the meat of the file conversion for icw.
"""

from icalendar import Calendar, Event, LocalTimezone
from datetime import datetime, timedelta
import logging
import uuid
import csv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class HeadersError(Exception):
    def __str__(self):
        return "HeadersError: " + self.args[0]


class DatetimeFormatError(Exception):
    def __str__(self):
        return "DatetimeFormatError: " + self.args[0]


class ContentError(Exception):
    def __str__(self):
        return "ContentError: " + self.args[0]


def check_headers(headers):
    """Makes sure that all the headers are exactly
    correct so that they'll be recognized as the
    necessary keys."""

    valid_keys = ['End Date', 'Description',
                  'All Day Event', 'Start Time', 'Private',
                  'End Time', 'Location', 'Start Date', 'Subject']

    if not all([set(headers) == set(valid_keys),
                len(headers) == len(valid_keys)]):
        logger.info("Problem in the check_headers function. Headers: "
                    "{}".format(", ".join(headers)))
        errmsg = "Something isn't right with the headers."
        try:
            # bool(0) is False
            extras = set(headers) - set(valid_keys)
            missing = set(valid_keys) - set(headers)
            if extras:
                errmsg += " Extra (or misspelled) keys: " + \
                          ", ".join(map(str, extras)) + "."
            if missing:
                errmsg += " Missing keys: " + ", ".join(map(str, missing)) \
                          + "."
        except Exception as e:
            logger.exception(e)

        raise HeadersError(errmsg)
    else:
        return headers


def clean_spaces(csv_dict):
    """Cleans trailing spaces from the dictionary
    values, which can break my datetime patterns."""
    clean_row = {}
    for row in csv_dict:
        for k, v in row.items():
            if v:
                clean_row.update({k: v.strip()})
            else:
                clean_row.update({k: None})

        yield clean_row


def check_dates_and_times(start_date, start_time, end_date, end_time, all_day,
                          rownum):
    """Checks the dates and times to make sure everything is kosher."""

    logger.debug('Date checker started.')

    # Gots to have a start date, no matter what.
    if start_date in ['', None]:
        logger.error('Missing a start date at row {}'.format(rownum))
        errmsg = 'Missing a start date'
        try:
            errmsg += " around row number {}.".format(rownum)
        except:
            pass
        raise DatetimeFormatError(errmsg)

    for date in [start_date, end_date]:
        if date not in ['', None]:
            try:
                datetime.strptime(date, '%m/%d/%Y')
            except ValueError as e:
                errmsg = "Something isn't right with a date in row {}. Make "\
                         "sure you're using MM/DD/YYYY format.".format(rownum)
                try:
                    bad_date = e.args[0].split("'")[1]
                    errmsg += " Problematic date: " + bad_date
                except:
                    pass

                raise DatetimeFormatError(errmsg)

    for time in [start_time, end_time]:
        if time not in ['', None]:
            try:
                time = time.replace(' ', '')
                if time[-2:].lower() in ['am', 'pm']:
                    datetime.strptime(time, '%I:%M%p')
                else:
                    datetime.strptime(time, '%H:%M')
            except ValueError as e:
                errmsg = "Something isn't right with a time in row {}. Make "\
                         "sure you're using either '1:00 PM' or '13:00' "\
                         "format.".format(rownum)
                try:
                    bad_time = e.args[0].split("'")[1]
                    errmsg += " Problematic time: " + bad_time
                except:
                    pass

                raise DatetimeFormatError(errmsg)

    if all_day is None or all_day.lower() != 'true':
        if not (start_time and end_time):
            logger.error('Missing a required time field in a non-all_day '
                         'event on date: {}.'.format(start_date))
            errmsg = 'Unless an event is "all day," it needs both a start '\
                     'and end time. Double check row {}.'.format(rownum)
            raise DatetimeFormatError(errmsg)

    logger.debug('Date checker ended.')


def convert(upfile):

    reader_builder = csv.reader(upfile.read().splitlines(),
                                skipinitialspace=True)

    reader_list = list(reader_builder)

    headers = check_headers(reader_list[0])
    logger.debug("Verified headers: {}".format(', '.join(headers)))

    raw_reader = [dict(zip(headers, values)) for values in reader_list[1:]]
    reader = clean_spaces(raw_reader)

    # Start calendar file
    cal = Calendar()
    cal.add('prodid', 'n8henrie.com')
    cal.add('X-WR-CALNAME', "Imported Calendar")
    cal.add('version', '2.0')

    # Write the clean list of dictionaries to events.
    # rownum starts at 2 to match the spreadsheet numbering.
    for rownum, row in enumerate(reader, start=2):
        logger.debug('Event {} started, contents:\n{}'.format(rownum, row))

        # No blank subjects, skip row if subject is None or ''
        if row.get('Subject') in ['', None]:
            continue

        event = Event()
        event.add('summary', row['Subject'])

        # If marked as an "all day event" ignore times. If start and end date
        # are the same or if end date is blank, default to a single 24-hour
        # event.

        check_dates_and_times(
            start_date=row.get('Start Date'),
            start_time=row.get('Start Time'),
            end_date=row.get('End Date'),
            end_time=row.get('End Time'),
            all_day=row.get('All Day Event'),
            rownum=rownum
            )

        # `{}.get('nothere', '') == ''`, but
        # `{'nothere': None}.get('nothere', '') == None`
        if row.get('All Day Event') and row.get('All Day Event').lower() == 'true':

            # All-day events will not be marked as 'busy'
            event.add('transp', 'TRANSPARENT')

            dtstart = datetime.strptime(row['Start Date'], '%m/%d/%Y')
            event.add('dtstart', dtstart.date())
            if row.get('End Date') in ['', None]:
                dtend = dtstart + timedelta(days=1)
                event.add('dtend', dtend.date())
            else:
                dtend = datetime.strptime(row['End Date'], '%m/%d/%Y')
                dtend += timedelta(days=1)
                event.add('dtend', dtend.date())

        # Continue processing events not marked as "all day" events.
        else:

            # Events with times should be 'busy' by default
            event.add('transp', 'OPAQUE')

            # Get rid of spaces
            # Note: Must have both start and end times if not all_day, already
            # checked
            row['Start Time'] = row['Start Time'].replace(' ', '')
            row['End Time'] = row['End Time'].replace(' ', '')

            # Allow either 24 hour time or 12 hour + am/pm
            if row['Start Time'][-2:].lower() in ['am', 'pm']:
                dt_string = '%m/%d/%Y%I:%M%p'
            else:
                dt_string = '%m/%d/%Y%H:%M'
            dtstart = datetime.strptime(row['Start Date'] + row['Start Time'],
                                        dt_string)
            event.add('dtstart', dtstart)

            # Allow blank end dates (assume same day)
            if row.get('End Date') in ['', None]:
                row['End Date'] = row['Start Date']

            if row['End Time'][-2:].lower() in ['am', 'pm']:
                dt_string = '%m/%d/%Y%I:%M%p'
            else:
                dt_string = '%m/%d/%Y%H:%M'
            dtend = datetime.strptime(row['End Date'] + row['End Time'],
                                      dt_string)
            event.add('dtend', dtend)

        for tag in ['Description', 'Location']:
            if row.get(tag):
                event.add(tag, row[tag])

        event.add('dtstamp', datetime.replace(datetime.now(),
                                              tzinfo=LocalTimezone()))

        # n8henrie.com tag at the end not used for tracking, just
        # personalization
        event['uid'] = str(uuid.uuid4()) + '___n8henrie.com'

        cal.add_component(event)
        rownum += 1

    if len(cal.subcomponents) > 0:
        final_file = cal.to_ical()
    else:
        raise ContentError("Final calendar was empty.")

    return final_file
