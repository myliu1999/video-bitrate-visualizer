#!/usr/bin/env python3
"""
visualize_bitrate.py

Usage:
    python visualize_bitrate.py /path/to/video.mp4 1   # 1-second buckets
"""

import sys
import json
import subprocess
from pathlib import Path
from collections import defaultdict
import argparse
import csv
import webbrowser

import plotly.graph_objects as go

import matplotlib.pyplot as plt


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Visualize and export video bitrate over time"
    )
    parser.add_argument("video", type=Path, help="Path to video file")
    parser.add_argument(
        "--bucket",
        type=float,
        default=1.0,
        help="Bucket duration in seconds for bitrate aggregation",
    )
    parser.add_argument(
        "--export-csv",
        type=Path,
        help="Optional path to write CSV bitrate data",
    )
    parser.add_argument(
        "--export-json",
        type=Path,
        help="Optional path to write JSON bitrate data",
    )
    parser.add_argument(
        "--save-plot",
        type=Path,
        help="Optional path to save the plotted graph as an image",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Overlay min/max/average bitrate on the plot and print them",
    )
    parser.add_argument(
        "--stats-file",
        type=Path,
        help="Optional path to write bitrate statistics",
    )
    parser.add_argument(
        "--plotly-html",
        type=Path,
        help="Optional path to write interactive HTML plot using Plotly",
    )
    parser.add_argument(
        "--target-bitrate",
        type=float,
        help="Optional target bitrate in kbps to show as a reference",
    )
    return parser.parse_args()


def probe_packets(video_path: Path) -> list[tuple[float, int]]:
    """
    Return a list of (pts_time, size_bytes) for every packet in the video stream.
    Requires ffprobe (ships with FFmpeg) in PATH.
    """
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v",  # video stream only
        "-show_entries",
        "packet=pts_time,size",
        "-of",
        "json",
        str(video_path),
    ]
    result = subprocess.run(cmd, check=True, text=True, capture_output=True)
    data = json.loads(result.stdout)
    packets = []
    for pkt in data.get("packets", []):
        pts = float(pkt["pts_time"])
        size = int(pkt["size"])
        packets.append((pts, size))
    return packets


def aggregate_bitrate(
    packets: list[tuple[float, int]], window_sec: float
) -> tuple[list[float], list[float]]:
    """
    Aggregate bytes into window_sec buckets and convert to kilobits per second.
    Returns times[] (bucket center) and kbps[] lists.
    """
    bucket_totals = defaultdict(int)  # bucket_index -> bytes
    for pts, size in packets:
        idx = int(pts // window_sec)
        bucket_totals[idx] += size

    times = []
    kbps = []
    for idx in sorted(bucket_totals):
        midpoint = (idx + 0.5) * window_sec
        bits = bucket_totals[idx] * 8  # bytes -> bits
        rate = bits / window_sec / 1000  # bits/s -> kbps
        times.append(midpoint)
        kbps.append(rate)
    return times, kbps


def compute_stats(kbps: list[float]) -> tuple[float, float, float]:
    if not kbps:
        return 0.0, 0.0, 0.0
    mn = min(kbps)
    mx = max(kbps)
    avg = sum(kbps) / len(kbps)
    return mn, mx, avg


def plot_bitrate(
    times: list[float],
    kbps: list[float],
    video_name: str,
    save_path: Path | None = None,
    show_stats: bool = False,
    target_kbps: float | None = None,
) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(times, kbps, linewidth=1)
    plt.title(f"Variable Bitrate – {video_name}")
    plt.xlabel("Time (s)")
    plt.ylabel("Bitrate (kbps)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    if target_kbps is not None:
        plt.axhline(
            target_kbps,
            linestyle="--",
            color="red",
            label=f"target {target_kbps:.0f} kbps",
        )
    if show_stats and kbps:
        avg = sum(kbps) / len(kbps)
        mn = min(kbps)
        mx = max(kbps)
        text = f"min={mn:.0f} kbps\nmax={mx:.0f} kbps\navg={avg:.0f} kbps"
        plt.annotate(
            text,
            xy=(0.99, 0.95),
            xycoords="axes fraction",
            ha="right",
            va="top",
            bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.8),
        )
    plt.tight_layout()
    if target_kbps is not None:
        plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()


def plotly_bitrate(
    times: list[float],
    kbps: list[float],
    video_name: str,
    html_path: Path,
    target_kbps: float | None = None,
) -> None:
    fig = go.Figure(data=go.Scatter(x=times, y=kbps, mode="lines", line=dict(width=1)))
    fig.update_layout(
        title=f"Variable Bitrate – {video_name}",
        xaxis_title="Time (s)",
        yaxis_title="Bitrate (kbps)",
    )
    if target_kbps is not None:
        fig.add_hline(y=target_kbps, line_dash="dash", line_color="red")
    fig.write_html(str(html_path), auto_open=True)


def export_data(
    times: list[float],
    kbps: list[float],
    csv_path: Path | None,
    json_path: Path | None,
) -> None:
    if csv_path:
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["time_sec", "bitrate_kbps"])
            for t, b in zip(times, kbps):
                writer.writerow([t, b])
    if json_path:
        with open(json_path, "w") as f:
            records = [{"time_sec": t, "bitrate_kbps": b} for t, b in zip(times, kbps)]
            json.dump(records, f, indent=2)


def main() -> None:
    args = parse_args()

    packets = probe_packets(args.video)
    times, kbps = aggregate_bitrate(packets, args.bucket)

    mn, mx, avg = compute_stats(kbps)
    stats_text = f"min={mn:.0f} kbps\nmax={mx:.0f} kbps\navg={avg:.0f} kbps"
    if args.stats:
        print(stats_text)
    if args.stats_file:
        with open(args.stats_file, "w") as f:
            f.write(stats_text + "\n")

    export_data(times, kbps, args.export_csv, args.export_json)

    if args.plotly_html:
        plotly_bitrate(
            times,
            kbps,
            args.video.name,
            args.plotly_html,
            target_kbps=args.target_bitrate,
        )

    plot_bitrate(
        times,
        kbps,
        args.video.name,
        save_path=args.save_plot,
        show_stats=args.stats,
        target_kbps=args.target_bitrate,
    )


if __name__ == "__main__":
    main()
