# Redis cache resilience

Issue [#6169](https://github.com/raft-tech/TANF-app/issues/6169) is based on one
confirmed production incident: `/v1/feature-flags/` on October 14, 2026 at
2:20 PM ET. The request was aborted approximately 100.776 seconds after its
request-start header while waiting for a Redis SSL read. This is consistent
with Gunicorn's 100-second worker timeout. Recurrence and the infrastructure
trigger are unknown. STT and throttling are related code exposure, not
additional observed incidents.

## Timeout and failure policies

All Django Redis caches use a one-second connection timeout, a one-second
socket timeout, and no automatic retries. Both local and Cloud.gov settings
use the same options. These are network-operation limits, not a total request
deadline: a request can perform several cache operations. Celery's broker and
result backend are separate from Django caches and are unaffected.

| Cache | Redis connection or timeout failure |
| --- | --- |
| `stts` | Treat failed reads as misses and query the database. Failed page-cache writes do not prevent the response. |
| `feature-flags` | Query the database after failed reads. Failed writes do not prevent list or detail responses. |
| Feature-flag invalidation | Log a warning and allow the database create, update, or delete to finish. Cached values may remain stale until their existing five-minute expiry. |
| `throttle` | Reject affected bearer-token requests with HTTP 503 if either reading or writing the rate counter fails. Browser sessions still skip this throttle. |

Only Redis connection and timeout errors are suppressed by the optional
cache backend. Other errors remain visible. Warning logs identify the cache
prefix and operation without logging cache keys, values, or credentials.

`DEFAULT_CACHE_TIMEOUT = 300` is the lifetime of cached values; it does not
control socket waits. A failed invalidation is not retried in the background.
If a flag change must be reflected immediately, verify invalidation succeeds
after Redis recovers or wait for the existing cache entry to expire.

## Release identification

`scripts/deploy-backend.sh` supplies `SENTRY_RELEASE` to both backend and Celery
apps. It uses an explicit `SENTRY_RELEASE` when supplied, otherwise
`CIRCLE_SHA1`, otherwise the local Git commit. Django passes this identifier to
Sentry. Verify the deployed event's `release` field after deployment.

## Validation and release evidence

Run the targeted backend regression suite:

```sh
task backend-pytest PYTEST_ARGS='tdpservice/test/test_cache.py tdpservice/core/test/test_cache_resilience.py tdpservice/core/test/test_api.py tdpservice/core/test/test_models.py tdpservice/stts/test/test_api.py tdpservice/users/test/test_throttle_cache.py tdpservice/users/test/test_bearer_token_auth.py -q'
task backend-lint
```

The regression suite checks both connection and timeout errors during reads,
writes, and invalidation, plus existing warm/cold cache behavior. A local TCP
server accepts a Redis `GET` and deliberately withholds its response to check
that the configured read timeout bounds the wait.

Before closing the ticket, record staging validation in the release digest:

1. Use an isolated staging app/cache or a fault-injection proxy that can drop
   Redis replies without affecting other apps or Celery.
2. Request `/v1/feature-flags/`, a feature-flag detail URL, and `/v1/stts/alpha`.
   Verify database-backed HTTP 200 responses while Redis is unavailable.
3. Save and delete a test flag. Verify the database changes succeed and the
   invalidation warning is recorded. Account for the stale-value policy above.
4. Make a bearer-token request that uses the throttle. Verify HTTP 503 on
   Redis failure, then normal rate limiting after recovery.
5. Restore Redis and confirm warm-cache behavior. Record response timings,
   absence of Gunicorn worker timeouts, and the deployed Sentry release.

Staging validation and historical service-log investigation require access to
those environments; local tests do not establish either result.

### Local verification, November 16, 2026

- Full backend Flake8 and deployment-script `bash -n` checks passed.
- Twenty independent cache/configuration/throttle checks passed using a temporary
  minimal Django bootstrap with the installed Django 6.0.5 and redis-py 7.4.0.
  These versions differ from the lockfile (Django 5.2.14 and redis-py 7.1.0).
- The stalled-server test could not bind its localhost socket because of the
  execution environment's permissions, including after an elevated attempt.
- The normal database-backed suite could not start: Docker's executable was
  unavailable, local PostgreSQL shared memory was denied, and the local Python
  environment lacked application packages. Package-index access was unavailable.
- The locked-dependency regression suite and staging checks above remain required
  before marking the ticket's validation criteria complete.
