import copy

SEFF_LOOKUP = {
    "Job ID": ("job_id", int),
    "Cores": ("cores", int),
    "State": ("state", str),
}

SLURM_STATS = {
    "command": None,
    "requested_ram": float,
    "job_name": None,
    "start_time": None,
    "end_time": None,
    "exit_code": int,
    "wall_clock_s": int,
}

OTHER_STATS = {
        "max_ram": None,
        "cpu_percent": None,
        "ram_percent": None,
        "user_time": None,
        "system_time_s": None,
        "system_time_m": None,
        "system_time_h": None,
        "wall_clock_s_from_time": None,
        "wall_clock_m_from_time": None,
        "wall_clock_h_from_time": None,
        "job_id": None,
        "cores": None,
        "wall_clock_m": None,
        "wall_clock_h": None,
}

EMPTY_STATS = copy.deepcopy(OTHER_STATS)
EMPTY_STATS.update({k: None for k in SLURM_STATS})
EMPTY_STATS.update({v[0]: None for v in SEFF_LOOKUP.values()})


def parse_elapsed_time_line(line):
    time_fields = line.rstrip().split()[-1].split(":")
    if not 2 <= len(time_fields) <= 3:
        raise Exception(f"Error getting time from this line: {line}")
    time_in_seconds = float(time_fields[-1]) + 60 * float(time_fields[-2])
    if len(time_fields) == 3:
        time_in_seconds += 60 * 60 * float(time_fields[0])
    return time_in_seconds, round(time_in_seconds / 60, 2), round(time_in_seconds / (60 * 60), 2)


def unix_time_lines_to_time_and_memory(lines):
    stats = {}
    in_time_lines = False

    for line in lines:
        if not in_time_lines:
            if line.startswith("\tCommand being timed:"):
                in_time_lines = True
        elif line.startswith("\tElapsed (wall clock) time (h:mm:ss or m:ss): "):
            time_s, time_m, time_h = parse_elapsed_time_line(line)
            stats["wall_clock_s_from_time"] = time_s
            stats["wall_clock_m_from_time"] = time_m
            stats["wall_clock_h_from_time"] = time_h
        elif line.startswith("\tUser time (seconds): "):
            stats["user_time"] = float(line.rstrip().split()[-1])
        elif line.startswith("\tSystem time (seconds): "):
            stats["system_time_s"] = float(line.rstrip().split()[-1])
            stats["system_time_m"] = round(stats["system_time_s"] / 60, 2)
            stats["system_time_h"] = round(stats["system_time_s"] / (60 * 60), 2)
        elif line.startswith("\tMaximum resident set size (kbytes): "):
            stats["max_ram"] = round(float(line.rstrip().split()[-1]) / (1024*1024), 4)
        elif line.startswith("\tPercent of CPU this job got:"):
            assert line.endswith("%")
            stats["cpu_percent"] = float(line.split()[-1].strip("%"))

    return stats


def parse_stats_lines(lines):
    stats = {}
    for line in lines:
        if line.startswith("SLURM_STATS\t"):
            _, key, value = line.split("\t")
            if SLURM_STATS[key] is None or (key == "exit_code" and value == "UNKNOWN"):
                stats[key] = value
            else:
                stats[key] = SLURM_STATS[key](value)
        elif line.startswith("SLURM_STATS_SEFF\t") and ":" in line:
            key, value = line.split("\t", maxsplit=1)[1].split(":", maxsplit=1)
            value = value.strip()
            if key in SEFF_LOOKUP:
                new_key, value_type = SEFF_LOOKUP[key]
                stats[new_key] = value_type(value)

    return stats


def load_one_o_file(filename):
    # The file we're parsing has stdout from the job that was run, as well
    # as the stats that we are looking for.
    # We want all the lines at the end. There's the output of /usr/bin/time -v,
    # which starts with a line like this:
    # Command being timed: "<TAB>/usr/local/bin/bash -c echo test"
    # and after those stats is the line:
    # SLURM_STATS_BEGIN
    # followed by more stats that we want.
    # Look for last occurences of those lines, just in case by coincidence
    # the job output the same thing to stdout.
    stats = copy.deepcopy(EMPTY_STATS)

    with open(filename) as f:
        lines = [x.rstrip() for x in f]

    last_being_timed_line = None
    last_stats_begin_line = None

    for i, line in enumerate(lines):
        if line.startswith("\tCommand being timed: "):
            last_being_timed_line = i
        elif line == "SLURM_STATS_BEGIN":
            last_stats_begin_line = i

    if last_being_timed_line is not None:
        stats.update(unix_time_lines_to_time_and_memory(lines[last_being_timed_line:]))

    if last_stats_begin_line is not None:
        stats.update(parse_stats_lines(lines[last_stats_begin_line+1:]))

    if stats["max_ram"] is not None and stats["requested_ram"] is not None and stats["requested_ram"] > 0:
        stats["ram_percent"] = round(100 * stats["max_ram"] / stats["requested_ram"], 2)

    if stats["wall_clock_s"] is not None:
        stats["wall_clock_m"] = round(stats["wall_clock_s"] / 60, 2)
        stats["wall_clock_h"] = round(stats["wall_clock_s"] / (60 * 60), 2)

    if stats["state"] is not None and stats["state"].startswith("TIMEOUT"):
        stats["exit_code"] = "TIMEOUT"

    return stats


def parse_o_files(options):
    columns = ["exit_code", f"system_time_{options.time_units}", f"wall_clock_{options.time_units}", "max_ram", "requested_ram"]
    if options.all_columns:
        columns.extend(sorted([x for x in EMPTY_STATS if x not in columns]))
    print(*columns, "filename", sep="\t")

    for filename in options.filenames:
        stats = load_one_o_file(filename)
        if any([(x is not None) for x in stats.values()]):
            if options.fails and stats["exit_code"] == 0:
                continue
            print(*(stats[x] for x in columns), filename, sep="\t")
