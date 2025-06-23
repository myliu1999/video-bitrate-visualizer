# Video Bitrate Visualizer

This repository contains a small Python script for inspecting the variable bitrate of
an encoded video file. It relies on `ffprobe` from FFmpeg to collect per-packet
information and uses `matplotlib` to plot bitrate over time. The tool can also
export bitrate data to CSV or JSON and save the plot image for later analysis.

## Usage

```bash
python main.py VIDEO [--bucket SECS] [--export-csv FILE] [--export-json FILE] \
                     [--save-plot IMAGE] [--stats] [--plotly-html FILE]
```

* `VIDEO` – path to the input video file.
* `--bucket` – optional time window in seconds over which bytes are
  aggregated (defaults to `1`).
* `--export-csv/--export-json` – write the aggregated time/bitrate pairs to
  the specified file.
* `--save-plot` – save the plot to an image file in addition to displaying it.
* `--stats` – overlay minimum, maximum and average bitrates on the plot.
* `--plotly-html` – write an interactive HTML plot using Plotly.

Running the script pops up a plot window showing the average bitrate (in kbps)
for each time bucket.

## Requirements

- Python 3
- `ffprobe` available in `PATH` (ships with FFmpeg)
- `matplotlib`
- `plotly`

Install dependencies with `pip install matplotlib plotly` if needed.
