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

import matplotlib.pyplot as plt


def probe_packets(video_path: Path) -> list[tuple[float, int]]:
    """
    Return a list of (pts_time, size_bytes) for every packet in the video stream.
    Requires ffprobe (ships with FFmpeg) in PATH.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v",            # video stream only
        "-show_entries", "packet=pts_time,size",
        "-of", "json",
        str(video_path),
    ]
    result = subprocess.run(
        cmd, check=True, text=True, capture_output=True
    )
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
        bits = bucket_totals[idx] * 8        # bytes -> bits
        rate = bits / window_sec / 1000      # bits/s -> kbps
        times.append(midpoint)
        kbps.append(rate)
    return times, kbps


def plot_bitrate(times: list[float], kbps: list[float], video_name: str):
    plt.figure(figsize=(10, 5))
    plt.plot(times, kbps, linewidth=1)
    plt.title(f"Variable Bitrate – {video_name}")
    plt.xlabel("Time (s)")
    plt.ylabel("Bitrate (kbps)")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) < 2:
        print("Usage: python visualize_bitrate.py <video> [bucket_sec]")
        sys.exit(1)

    video_path = Path(sys.argv[1])
    bucket = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0

    packets = probe_packets(video_path)
    times, kbps = aggregate_bitrate(packets, bucket)
    plot_bitrate(times, kbps, video_path.name)


if __name__ == "__main__":
    main()
