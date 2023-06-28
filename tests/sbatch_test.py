import pytest

from slurmzy import sbatch


def test_convert_ram():
    assert sbatch.convert_ram(1) == "1G"
    assert sbatch.convert_ram(1.0) == "1G"
    assert sbatch.convert_ram(1.5) == "1536M"
    assert sbatch.convert_ram(0.5) == "512M"


def test_submit_job_dry_run():
    # Hard to test is this in any meaningful way (without actually submitting
    # a job to slurm, which don't want to do)
    got = sbatch.submit_job(
        "echo test",
        "job_name",
        3,
        2, # time in hours, will be converted to minutes
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

