"""test_upload.py
py.test tests to test a number of previously problematic files
"""

from StringIO import StringIO

proper_headers = ['End Date', 'Description', 'All Day Event', 'Start Time',
                  'Private', 'End Time', 'Location', 'Start Date', 'Subject']


def test_from_string(client):
    """Make sure I have a way to pass in a string for easier testing."""
    string_event = ['01/16/2015', 'A great event!', 'FALSE', '08:00', 'FALSE',
                    '12:00', 'New York New York', '01/16/2015', 'Some event']

    csv_as_string = '\n'.join([','.join(each) for each in [proper_headers,
                                                           string_event]])
    data = dict(csv_file=(StringIO(csv_as_string), 'fake.csv'))
    response = client.post('/', data=data, follow_redirects=True)
    download = client.get('/download')
    assert response.status_code == 200
    assert 'DESCRIPTION:A great event!' in download.data
