from slurmzy.ext import jobinfo


def run(options):
    jobinfo.main(options.job_id, False)

