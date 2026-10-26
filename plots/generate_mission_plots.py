#!/usr/bin/env python3

import json
import math
import os
from datetime import datetime, timedelta
import matplotlib as mpl    
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# ---------------------------
# Configuration
# ---------------------------
INPUT_FILE = "missions_data.json"
OUTPUT_DIR = "mission_plots"
PARTS = 4

COLOR_MAP = {
    "past": "#0076d6",      # USWDS blue-50v
    "current": "#538200",   # USWDS green-cool-50v
    "future": "#e5a000"     # USWDS gold-30v
}

STAR_SYMBOL = "★"

mpl.rcParams.update({
    "font.size": 14,
    "font.weight": "bold",
    "axes.titlesize": 16,
    "axes.titleweight": "bold",
    "axes.labelsize": 14,
    "axes.labelweight": "bold",
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 13,
    "figure.titlesize": 16,
    "figure.figsize": (6, 6),
    "figure.dpi": 96,
    "savefig.dpi": 96,
})

# ---------------------------
# Date Parsing (robust)
# ---------------------------
def parse_date(date_str, is_end=False):
    """
    Handles:
      YYYY-MM-DD
      YYYY-MM
      YYYY
    """
    if not date_str:
        return None

    try:
        # Full date
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        pass

    try:
        # Year-Month
        dt = datetime.strptime(date_str, "%Y-%m")
        if is_end:
            # approximate end of month
            if dt.month == 12:
                return datetime(dt.year, 12, 31)
            else:
                next_month = datetime(dt.year, dt.month + 1, 1)
                return next_month.replace(day=1) - timedelta(days=1)
        return dt
    except ValueError:
        pass

    try:
        # Year only
        year = int(date_str)
        if is_end:
            return datetime(year, 12, 31)
        return datetime(year, 1, 1)
    except ValueError:
        return None


# ---------------------------
# Utilities
# ---------------------------
def mission_color(mission):
    status = mission.get("status", "").lower()
    return COLOR_MAP.get(status, "#0076d6")


def has_heasarc(mission):
    # older entries use a Boolean field, newer ones the tags list
    if mission.get("heasarc"):
        return True
    tags = mission.get("data_tags", [])
    return any(t.upper() == "HEASARC" for t in tags)


def chunk_list(data, parts):
    chunk_size = math.ceil(len(data) / parts)
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def is_multiple_flight(mission):
    """Return True if the mission represents a collection of flights rather
    than a continuous satellite/observatory.  The dataset encodes this in
    ``date_range_note``; look for keywords that indicate balloon or rocket
    flight activity.
    """
    note = mission.get("date_range_note", "").lower()
    return "balloon" in note or "flight" in note


def add_legend(ax, missions_sorted=None):
    legend_elements = [
        Patch(facecolor=COLOR_MAP["past"], edgecolor="black", label="Past"),
        Patch(facecolor=COLOR_MAP["current"], edgecolor="black", label="Current"),
        Patch(facecolor=COLOR_MAP["future"], edgecolor="black", label="Future"),
        Patch(facecolor="white", edgecolor="black", hatch='//', label="Balloon/rocket flights"),
        Line2D([0], [0], marker='*', color='w',
               markerfacecolor='black', markersize=10,
               label="HEASARC Data")
    ]

    margin = 0.1
    ax.figure.subplots_adjust(top=0.9, right=0.8)  # optional
    legend = ax.legend(
        handles=legend_elements,
        loc='best',
        borderaxespad=margin,
        framealpha=0.85
    )
    ax.add_artist(legend)


def save_plot(fig, filename_base, target_px_width=1400, dpi=150):
    png_path = os.path.join(OUTPUT_DIR, filename_base + ".png")
    svg_path = os.path.join(OUTPUT_DIR, filename_base + ".svg")

    # Compute pixel height to preserve aspect ratio from the current figure size
    width_in, height_in = fig.get_size_inches()
    aspect = float(height_in) / float(width_in) if width_in else 1.0
    px_width = int(target_px_width)
    px_height = int(round(px_width * aspect))

    save_png(png_path, px_width=px_width, px_height=px_height, dpi=dpi)
    save_svg(svg_path)
    plt.close(fig)

def save_png(output_path, px_width=None, px_height=None, dpi=None, transparent=False):
    fig = plt.gcf()

    # Resolve DPI: prefer explicit `dpi` arg; otherwise consult rcParams.
    if dpi is not None:
        try:
            dpi_val = float(dpi)
        except Exception:
            dpi_val = 150.0
    else:
        sf_dpi = mpl.rcParams.get("savefig.dpi", None)
        # Matplotlib allows 'figure' to mean use the figure's dpi
        if sf_dpi == "figure" or sf_dpi is None:
            fig_dpi = mpl.rcParams.get("figure.dpi", 150)
            try:
                dpi_val = float(fig_dpi)
            except Exception:
                dpi_val = 150.0
        else:
            try:
                dpi_val = float(sf_dpi)
            except Exception:
                dpi_val = 150.0

    size = fig.get_size_inches()
    try:
        width_in = float(size[0])
        height_in = float(size[1])
    except Exception:
        import numpy as _np
        arr = _np.asarray(size).flatten()
        width_in = float(arr[0])
        height_in = float(arr[1]) if arr.size > 1 else float(arr[0])

    if px_width is None:
        px_width = int(round(width_in * dpi_val))
    if px_height is None:
        px_height = int(round(height_in * dpi_val))

    fig.set_size_inches(px_width / dpi_val, px_height / dpi_val)
    plt.tight_layout()
    fig.savefig(output_path, dpi=int(round(dpi_val)), bbox_inches="tight", transparent=transparent)

def save_svg(output_path_svg):
    fig = plt.gcf()
    plt.tight_layout()
    fig.savefig(output_path_svg, format="svg", bbox_inches="tight")


# ---------------------------
# Timeline Plot
# ---------------------------
def plot_timeline(missions, part_number):
    missions_sorted = list(reversed(missions))

    # shrink vertical footprint a bit; 0.5 gives a reasonably compact plot
    row_height = 0.5
    fig, ax = plt.subplots(figsize=(18, row_height * len(missions_sorted)))

    min_date = None
    max_date = None

    for i, mission in enumerate(missions_sorted):
        launch = parse_date(mission.get("launch_date"))
        if not launch:
            continue
        # debug output for problematic entries

        # --- Determine End Dates ---
        actual_end = parse_date(mission.get("end_date"), is_end=True)
        planned_end = parse_date(mission.get("planned_end_date"), is_end=True)
        extended_end = parse_date(mission.get("extended_end_date"), is_end=True)

        # choose the best endpoint, with extended as last resort
        primary_end = actual_end or planned_end or extended_end
        if mission.get("status", "").lower() == "current":
            # make sure the solid bar reaches at least to today so there is
            # no visual gap when we later draw a fade from today outward
            today = datetime.today()
            if not primary_end or primary_end < today:
                primary_end = today
        if not primary_end:
            # past mission with no date at all -> skip
            print(f"skipping {mission.get('name')} – no usable end date")
            continue
        if primary_end < launch:
            print(f"skipping {mission.get('name')} – end before launch")
            continue

        # Track dynamic axis range
        min_date = launch if not min_date else min(min_date, launch)
        max_date = primary_end if not max_date else max(max_date, primary_end)

        if extended_end:
            max_date = max(max_date, extended_end)

        color = mission_color(mission)

        # bar height for both timeline and energy plots
        bar_height = 0.6

        # --- Solid portion ---
        # compute width in days including fractional part; using .days
        # truncates the time component and produced a gap when primary_end
        # was set to "today" with a time-of-day.
        width = mdates.date2num(primary_end) - mdates.date2num(launch)
        ax.barh(
            i,
            width,
            left=mdates.date2num(launch),
            color=color,
            edgecolor="none",  # will draw border separately
            height=bar_height,
            zorder=2
        )
        if is_multiple_flight(mission):
            # Special logic needed for hatch marks (must set edgecolor)
            hatch_bar = ax.barh(
                i,
                width,
                left=mdates.date2num(launch),
                color='none',
                edgecolor='black',
                hatch='//',
                height=bar_height,
                zorder=3  # above base bar, below fade
            )

        # --- Fade portion for projections or extensions ---
        fade_start = None
        fade_end = None
        if mission.get("status", "").lower() == "current":
            # for ongoing missions we only draw a fade if an extension exists
            # beyond the planned/primary end.  The fade should begin at the
            # end of the planned interval, not at the current date.
            if extended_end and primary_end and extended_end > primary_end:
                fade_start = primary_end
                fade_end = extended_end
        else:
            # for past missions with an extension beyond planned
            if planned_end and extended_end and extended_end > primary_end:
                fade_start = planned_end
                fade_end = extended_end

        if fade_start and fade_end and fade_end > fade_start:
            import numpy as _np
            # create explicit RGBA gradient so alpha fades out
            left = mdates.date2num(fade_start)
            # small epsilon to cover the stroke without shifting the fade
            left -= 1e-3
            right = mdates.date2num(fade_end)
            n = 300
            rgb = mpl.colors.to_rgb(color)
            # RGBA array shape (1,n,4)
            grad = _np.zeros((1, n, 4))
            grad[..., :3] = rgb
            # start fully opaque and decay to zero
            grad[..., 3] = _np.linspace(1, 0, n)[_np.newaxis, :]
            ax.imshow(
                grad,
                aspect="auto",
                extent=(left, right, i - bar_height / 2, i + bar_height / 2),
                origin="lower",
                interpolation="nearest",
                zorder=3
            )
        # draw outline around whole mission interval (launch→extended end if any)
        border_end = mdates.date2num(extended_end or primary_end)
        from matplotlib.patches import Rectangle
        rect = Rectangle((mdates.date2num(launch), i - bar_height/2),
                         border_end - mdates.date2num(launch),
                         bar_height,
                         fill=False,
                         edgecolor="black",
                         linewidth=1,
                         zorder=4)
        ax.add_patch(rect)

    # enforce the computed min/max range; without this the axes will
    # autoscale to the first bar encountered which in the newest‑missions
    # chunk can be a 2030s mission, resulting in a misleading title.
    if min_date and max_date:
        ax.set_xlim(min_date, max_date)

    ax.grid(axis='x', color='#dfe1e2', linewidth=0.8)
    ax.set_axisbelow(True)

    ax.set_yticks(range(len(missions_sorted)))
    ax.set_ylim(-0.5, len(missions_sorted) - 0.5)

    labels = []
    for m in missions_sorted:
        label = f"{STAR_SYMBOL} {m['name']}" if has_heasarc(m) else m["name"]
        labels.append(label)

    ax.set_yticklabels(labels)


    span_years = (max_date - min_date).days / 365.25
    if span_years <= 20:
        ax.xaxis.set_major_locator(mdates.YearLocator(2))
    elif span_years <= 50:
        ax.xaxis.set_major_locator(mdates.YearLocator(5))
    else:
        ax.xaxis.set_major_locator(mdates.YearLocator(10))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.set_xlabel("Year")
    #start_year = min_date.year
    #end_year = max_date.year
    #ax.set_title(f"Mission Timeline ({start_year}–{end_year})")

    # give a small padding on both ends of the x axis so bars aren't flush
    span = max_date - min_date
    pad = timedelta(days=span.days * 0.01)
    ax.set_xlim(min_date - pad, max_date + pad)

    plt.tight_layout()
    add_legend(ax, missions_sorted)

    save_plot(fig, f"timeline_part_{part_number}")


# ---------------------------
# Energy Plot (Log Scale)
# ---------------------------
def plot_energy(missions, part_number):
    missions_sorted = list(missions)
    
    # Filter valid energy values (already in keV units)
    valid_lows = [m["low_energy"] for m in missions_sorted if m.get("low_energy", 0) > 0]
    valid_highs = [m["high_energy"] for m in missions_sorted if m.get("high_energy")]

    if not valid_lows or not valid_highs:
        # No valid data to plot
        return

    min_energy = min(valid_lows)
    max_energy = max(valid_highs)

    def round_down_to_power_of_10(x):
        return 10**math.floor(math.log10(x))

    def round_up_to_power_of_10(x):
        return 10**math.ceil(math.log10(x))
 
    def format_energy(value_keV):
        """
        Format an energy value given in keV with appropriate units:
        eV, keV, MeV, GeV, TeV, PeV, EeV
        """
        # Convert keV to eV for simpler calculation:
        value_eV = value_keV * 1e3

        # Define unit thresholds and names in ascending order
        units = [
            (1e18, "EeV"),
            (1e15, "PeV"),
            (1e12, "TeV"),
            (1e9,  "GeV"),
            (1e6,  "MeV"),
            (1e3,  "keV"),
            (1,    "eV")
        ]

        # Find appropriate unit by descending from largest to smallest
        for threshold, unit_name in units:
            if value_eV >= threshold:
                scaled_value = value_eV / threshold
                # Format with reasonable decimals
                if scaled_value >= 100:
                    fmt = f"{scaled_value:.0f} {unit_name}"
                elif scaled_value >= 10:
                    fmt = f"{scaled_value:.1f} {unit_name}"
                else:
                    fmt = f"{scaled_value:.2f} {unit_name}"
                return fmt
    
        # If below 1 eV, show in eV with decimals
        return f"{value_eV:.2f} eV"
  
    # reduce vertical height to match timeline plots
    row_height = 0.5
    fig, ax = plt.subplots(figsize=(18, row_height * len(missions_sorted)))
        
    for i, mission in enumerate(missions_sorted):
        low = mission.get("low_energy")
        high = mission.get("high_energy")

        if not low or not high or low <= 0:
            continue

        ax.barh(
            i,
            high - low,
            left=low,
            color=mission_color(mission),
            edgecolor="black",
            height=0.6,
            hatch='//' if is_multiple_flight(mission) else None
        )

    ax.set_xscale("log")
    # Compute new axis limits rounded to even powers of ten
    x_min = round_down_to_power_of_10(min_energy)
    x_max = round_up_to_power_of_10(max_energy)
    #ax.set_xlim(min_energy, max_energy)
    ax.set_xlim(x_min, x_max)

    ax.set_yticks(range(len(missions_sorted)))
    ax.set_ylim(-0.5, len(missions_sorted) - 0.5)

    labels = []
    for m in missions_sorted:
        label = f"{STAR_SYMBOL} {m['name']}" if has_heasarc(m) else m["name"]
        labels.append(label)

    ax.set_yticklabels(labels)

    ax.set_xlabel("Energy Range (keV)")
    #ax.set_title(f"Mission Energy Range ({format_energy(min_energy)} - {format_energy(max_energy)})")

    # pad energy axis by 2% on each side in log space
    #factor = 0.02
    #ax.set_xlim(min_energy * (1 - factor), max_energy * (1 + factor))

    plt.tight_layout()
    add_legend(ax, missions_sorted)

    save_plot(fig, f"energy_part_{part_number}")


# ---------------------------
# Main
# ---------------------------
def main():
    # start each run with a clean output directory to avoid confusion
    if os.path.exists(OUTPUT_DIR):
        import shutil
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    with open(INPUT_FILE, "r") as f:
        data = json.load(f)

    missions = data.get("missions", [])

    missions_time_sorted = sorted(
        missions,
        key=lambda m: parse_date(m.get("launch_date")) or datetime.min,
        reverse=True  # newest first
    )
    time_chunks = chunk_list(missions_time_sorted, PARTS)

    for i, chunk in enumerate(time_chunks, start=1):
        plot_timeline(chunk, i)

    missions_energy_sorted = sorted(
        missions,
        key=lambda m: m.get("low_energy", float("inf"))
    )

    energy_chunks = chunk_list(missions_energy_sorted, PARTS)

    for i, chunk in enumerate(energy_chunks, start=1):
        plot_energy(chunk, i)

    # Filter HEASARC missions
    heasarc_missions = [m for m in missions if has_heasarc(m)]

    # Sort by launch date, newest first
    heasarc_time_sorted = sorted(
        heasarc_missions,
        key=lambda m: parse_date(m.get("launch_date")) or datetime.min,
        reverse=True
        )

    heasarc_energy_sorted = sorted(
       heasarc_missions,
       key=lambda m: m.get("low_energy", float("inf"))
       )
    

    # Plot timeline for HEASARC missions
    plot_timeline(heasarc_time_sorted, "heasarc_timeline")
    plot_energy(heasarc_energy_sorted, "heasarc_energy")
        
    print(f"Generated plots in '{OUTPUT_DIR}' directory.")


if __name__ == "__main__":
    main()
