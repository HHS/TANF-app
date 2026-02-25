def get_cloudgov_broker_db_numbers(cloudgov_name):
    """
    Get the appropriate redis broker db numbers for an environment.

    Returns an object of {"celery": str, "caches": {"cache_name": str}}
    """
    spaces = {
        "dev": ["raft", "qasp", "a11y"],
        "staging": ["develop", "staging"],
        "prod": ["prod"],
    }
    cache_options = ["stts", "feature-flags"]

    broker_nums = {}

    for space, envs in spaces.items():
        incr = 0

        for env in envs:
            celery = str(incr)
            caches = {}
            for c in cache_options:
                incr += 1
                caches[c] = str(incr)

            broker_nums[env] = {"celery": celery, "caches": caches}
            incr += 1

    return broker_nums[cloudgov_name]
