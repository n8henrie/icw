"""Tests for files that should not be a problem."""

import glob


def test_success_files(client):
    """Test each in `success_files` and ensure conversion without errors."""
    success_files = glob.glob("tests/success_files/*")

    for success_file in success_files:
        with open(success_file, "rb") as f:
            response = client.post(
                "/", data=dict(csv_file=f), follow_redirects=True
            )

        download = client.get("/download")

        assert response.status_code == 200
        assert download.status_code == 200
        assert b"END:VEVENT\r\nEND:VCALENDAR" in download.data
