from pkg_resources import get_distribution

try:
    __version__ = get_distribution("slurmzy").version
except:
    __version__ = "local"


__all__ = [
    "ext",
    "job_stats",
    "sbatch",
]

from slurmzy import *
