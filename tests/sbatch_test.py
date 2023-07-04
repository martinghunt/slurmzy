import pytest

from slurmzy import sbatch


def test_convert_ram():
    assert sbatch.convert_ram(1) == "1G"
    assert sbatch.convert_ram(1.0) == "1G"
    assert sbatch.convert_ram(1.5) == "1536M"
    assert sbatch.convert_ram(0.5) == "512M"


def test_get_array_str():
    assert sbatch.get_array_str(None, None) is None
    assert sbatch.get_array_str(1, 42, limit=3) == "#SBATCH --array=1-42%3"


def test_submit_job_dry_run():
    # Hard to test is this in any meaningful way (without actually submitting
    # a job to slurm, which don't want to do)
    got = sbatch.submit_job(
        "echo test",
        "job_name",
        3,
        2,  # time in hours, will be converted to minutes
        dry_run=True,
        cpus=42,
        partition="queue_name",
    )
    assert "echo test" in got
    assert "SBATCH --output=job_name.o" in got
    assert "SBATCH --error=job_name.e" in got
    assert "SBATCH --mem=3G" in got
    assert "SBATCH --time=120" in got
    assert "SBATCH --cpus-per-task=42" in got
    assert "SBATCH --partition=queue_name" in got

    got = sbatch.submit_job(
        "echo test",
        "job_name",
        3,
        2,
        dry_run=True,
        array_start=1,
        array_end=42,
        array_limit=3
    )
    assert "echo test" in got
    assert "SBATCH --output=job_name.%a.o" in got
    assert "SBATCH --error=job_name.%a.e" in got
    assert "SBATCH --mem=3G" in got
    assert "SBATCH --time=120" in got
    assert "SBATCH --array=1-42%3" in got
