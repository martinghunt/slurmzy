from pkg_resources import get_distribution

try:
    __version__ = get_distribution("slurmzy").version
except:
    __version__ = "local"


__all__ = [
    "sbatch",
]

from slurmzy import *