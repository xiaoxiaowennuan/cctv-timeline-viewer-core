import unittest
import tempfile
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

from ctv_server.scanner import parse_ffprobe, extract_timestamp, scan_directory


class XiaomiRecordingTests(unittest.TestCase):
    def test_unix_filename_is_independent_of_backup_path_and_timezone(self):
        for zone in ("UTC", "Asia/Shanghai", "Europe/Rome"):
            self.assertEqual(extract_timestamp("04M05S_1704135845.mp4", "/backup/2024010203/04M05S_1704135845.mp4", zone), 1704135845)

    def test_flat_export_uses_start_not_end_time(self):
        expected = datetime(2024, 1, 2, 3, 4, 5, tzinfo=ZoneInfo("Asia/Shanghai")).timestamp()
        self.assertEqual(extract_timestamp("00_20240102030405_20240102030905.mp4", "", "Asia/Shanghai"), expected)

    def test_unrelated_or_invalid_unix_names_are_not_interpreted(self):
        for name in ("backup_1704135845.mp4", "62M56S_1704135845.mp4", "04M05S_1704135845000.mp4"):
            self.assertIsNone(extract_timestamp(name, ""))

    def test_recursive_scan_excludes_synology_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            hour = Path(root) / "2024010203"
            hour.mkdir()
            media = hour / "04M05S_1704135845.mp4"
            media.touch()
            metadata = hour / "@eaDir"
            metadata.mkdir()
            (metadata / "preview.mp4").touch()
            self.assertEqual([item["path"] for item in scan_directory(root)], [str(media)])


class ParseFfprobeTests(unittest.TestCase):
    def test_uses_video_stream_duration_when_format_duration_is_missing(self):
        info = parse_ffprobe({
            "format": {},
            "streams": [{
                "codec_type": "video",
                "codec_name": "h264",
                "duration": "53.5",
                "r_frame_rate": "25/1",
            }],
        })

        self.assertEqual(info["duration"], 53.5)
        self.assertEqual(info["fps"], 25.0)

    def test_uses_stream_time_base_when_duration_is_na(self):
        info = parse_ffprobe({
            "format": {"duration": "N/A"},
            "streams": [{
                "codec_type": "video",
                "duration": "N/A",
                "duration_ts": "90000",
                "time_base": "1/90000",
                "r_frame_rate": "N/A",
            }],
        })

        self.assertEqual(info["duration"], 1.0)
        self.assertEqual(info["fps"], 0.0)

    def test_invalid_duration_values_do_not_raise(self):
        info = parse_ffprobe({
            "format": {"duration": "inf"},
            "streams": [{
                "codec_type": "video",
                "duration_ts": "bad",
                "time_base": "bad",
                "r_frame_rate": "1/0",
            }],
        })

        self.assertEqual(info["duration"], 0.0)
        self.assertEqual(info["fps"], 0.0)


if __name__ == "__main__":
    unittest.main()
