# Xiaomi/Mijia NAS recordings

This fork adds timestamp parsing for `mmMssS_UNIX.mp4` exports and skips
Synology `@eaDir` metadata directories. Original media remains read-only.

Supported examples:

- `camera-id/2026081007/12M56S_1786317176.mp4`: the Unix timestamp is the
  absolute recording start, independent of backup modification times.
- `camera-name/00_20260920162802_20260920163344.mp4`: the existing parser
  reads the first date as the start time. Set the camera timezone to
  `Asia/Shanghai` for recordings whose filenames use Beijing time.

Add each camera separately, select **recursive/full indexing**, and scan it.
The upstream date-partitioned mode expects day folders and does not support
these hourly or flat layouts. Recursive cameras require another manual scan
to discover new recordings; upstream automatic daily indexing does not cover
them. This patch intentionally does not change scheduling or directory layout.

Use read-only Docker binds for the recordings and a separate writable volume
for the index and thumbnails. First test with a small representative sample.
Do not rename camera-generated files while cameras are writing to the NAS.

HEVC video and camera-specific audio can require the Balanced or Fast playback
profile. Server transcoding costs CPU. A timestamp parser cannot repair a
truncated MP4 that has no usable media metadata.

Validation: `python -m unittest discover -s tests -p test_scanner.py -v`
and `python -m unittest discover -s tests -p test_indexer.py -v`.
