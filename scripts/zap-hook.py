"""Python hook that can be used to disable ignored rules in ZAP scans."""


def zap_started(zap, target):
    """This hook runs after the ZAP API has been successfully started.

    This is needed to disable passive scanning rules which we have set to IGNORE
    in the ZAP configuration files. Due to an unresolved issue with the scripts
    the HTML report generated will still include ignored passive rules so this
    allows us to ensure they never run and won't be present in the HTML report.

    https://github.com/zaproxy/zaproxy/issues/6291#issuecomment-725947370
    https://github.com/zaproxy/zaproxy/issues/5212
    """
    # Active scan rules are ignored properly through the configuration file.
    # To see a list of all alerts and whether they are active or passive:
    # https://www.zaproxy.org/docs/alerts/
    ignored_passive_scan_ids = []

    # The `target` argument will contain the URL passed to the ZAP scripts, we
    # can use this to determine the appropriate rules to ignore.
    if 'web' in target or 'backend' in target:
        ignored_passive_scan_ids = [
            10036,  # Server Leaks Version Information
            10055,  # CSP unsafe inline
            10096,  # Informational: Timestamp Disclosure - Unix,
            100000,  # A Client Error response code was returned by the server
        ]

    if 'frontend' in target:
        ignored_passive_scan_ids = [
            10020,  # X-Frame-Option Header Not Set
            10021,  # X-Content-Type-Options Header Missing
            10027,  # Informational: Suspicious Comments
            10036,  # Server Leaks Version Information
            10055,  # CSP unsafe inline
            10096,  # Informational: Timestamp Disclosure - Unix
            10109,  # Modern Web Application
            90022,  # Application Error Disclosure
        ]

    for passive_scan_id in ignored_passive_scan_ids:
        # Use the ZAP Passive Scan API to disable ignored rules.
        # https://www.zaproxy.org/docs/api/#pscanactiondisablescanners
        # The ZAP scanner scripts do this only for active rules.
        # https://www.zaproxy.org/blog/2017-06-19-scanning-apis-with-zap/
        zap.pscan.set_scanner_alert_threshold(
            id=passive_scan_id,
            alertthreshold='OFF'
        )

    print(f'zap-hook disabled {len(ignored_passive_scan_ids)} passive rules')
