import pytest

from slurmzy import job_stats


def test_parse_elapsed_time_line():
    assert job_stats.parse_elapsed_time_line("0:06.00") == (6.0, 0.1, 0)
    assert job_stats.parse_elapsed_time_line("2:06.00") == (126.0, 2.1, 0.04)
    assert job_stats.parse_elapsed_time_line("1:2:06.00") == (3726.0, 62.1, 1.03)


def test_unix_time_lines_to_time_and_memory():
    lines = [
        "\tfoo",
        "\tCommand being timed: echo blah",
        "\tUser time (seconds): 0.06",
        "\tSystem time (seconds): 0.35",
        "\tPercent of CPU this job got: 47%",
        "\tElapsed (wall clock) time (h:mm:ss or m:ss): 0:00.87",
        "\tMaximum resident set size (kbytes): 1024",
        "\tspam",
        "\teggs",
    ]
    assert job_stats.unix_time_lines_to_time_and_memory(lines) == {
        "user_time": 0.06,
        "cpu_time_s": 0.35,
        "cpu_time_m": 0.01,
        "cpu_time_h": 0.0,
        "cpu_percent": 47.0,
        "wall_clock_s_from_time": 0.87,
        "wall_clock_m_from_time": 0.01,
        "wall_clock_h_from_time": 0.0,
        "max_ram": 0.001,
    }


def test_parse_stats_lines():
    lines = [
        "SLURM_STATS_BEGIN",
        "SLURM_STATS\tjob_id\t1234567",
        "SLURM_STATS\tcommand\techo blah",
        "SLURM_STATS\trequested_ram\t0.1",
        "SLURM_STATS\tjob_name\tdave_lister",
        "SLURM_STATS\tstart_time\t2023-06-30T15:06:46",
        "SLURM_STATS\tend_time\t2023-06-30T15:06:47",
        "SLURM_STATS\twall_clock_s\t42",
        "SLURM_STATS\texit_code\t137",
        "SLURM_STATS_JOBINFO\tNodes : node1",
        "SLURM_STATS_JOBINFO\tState : RUNNING",
    ]

    print("GOT:", job_stats.parse_stats_lines(lines))

    assert job_stats.parse_stats_lines(lines) == {
        "command": "echo blah",
        "requested_ram": 0.1,
        "job_name": "dave_lister",
        "start_time": "2023-06-30T15:06:46",
        "end_time": "2023-06-30T15:06:47",
        "wall_clock_s": 42,
        "exit_code": 137,
        "job_id": "1234567",
        "nodes": "node1",
        "state": "RUNNING",
    }
