# Video Bitrate Visualizer

This repository contains a small Python script for inspecting the variable bitrate of
an encoded video file. It relies on `ffprobe` from FFmpeg to collect per-packet
information and uses `matplotlib` to plot bitrate over time.

## Usage

```bash
python main.py <path/to/video.mp4> [bucket_seconds]
```

* `<path/to/video.mp4>` – path to the input video.
* `bucket_seconds` – optional time window in seconds over which bytes are
  aggregated (defaults to `1`).

Running the script pops up a plot window showing the average bitrate (in kbps)
for each time bucket.

## Requirements

- Python 3
- `ffprobe` available in `PATH` (ships with FFmpeg)
- `matplotlib`

Install dependencies with `pip install matplotlib` if needed.
