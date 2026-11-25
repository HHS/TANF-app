#!/bin/bash
# Exercise the real orchestration with synthetic commands, never cloud services.
set -euo pipefail

script_path="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/apply-database-config.sh"
test_root=$(mktemp -d "${TMPDIR:-/tmp}/tdp-database-config-test.XXXXXX")
trap 'rm -rf -- "$test_root"' EXIT
mkdir "$test_root/bin"

cat > "$test_root/bin/stub" <<'STUB'
#!/bin/bash
set -eu
case "${0##*/}" in
    cf)
        case "$1" in
            app)
                if [[ $TEST_SCENARIO == skip ]]; then
                    echo FAILED
                else
                    echo backend-guid
                fi
                ;;
            curl) echo '{}' ;;
            ssh)
                echo $$ > "$FIXTURE/tunnel.pid"
                trap 'touch "$FIXTURE/tunnel-stopped"' EXIT
                /bin/sleep 120 &
                child=$!
                trap 'kill "$child" 2>/dev/null || true; exit 0' TERM
                touch "$FIXTURE/tunnel-ready"
                wait "$child"
                ;;
        esac
        ;;
    jq)
        if [[ $* == *'join(":"'* ]]; then
            echo database.invalid:5432
        else
            echo '{}'
        fi
        ;;
    python)
        if [[ $1 == -m ]]; then
            mkdir -p env/bin
            echo 'deactivate() { :; }' > env/bin/activate
            exit 0
        fi
        action=$2
        if [[ $1 == *generate_views.py ]]; then
            action=generate
        elif [[ $2 == runscript ]]; then
            action=$3
        fi
        echo "$action" >> "$FIXTURE/actions"
        if [[ $action == "$TEST_FAIL_ACTION" ]]; then
            exit 23
        fi
        ;;
    sudo)
        if [[ $TEST_FAIL_ACTION == install ]]; then
            exit 23
        fi
        ;;
    sleep)
        for _ in {1..100}; do
            [[ -e "$FIXTURE/tunnel-ready" ]] && exit 0
            /bin/sleep 0.01
        done
        exit 1
        ;;
    pip|pipenv) : ;;
esac
STUB
chmod +x "$test_root/bin/stub"
for command in cf jq python sudo pip pipenv sleep; do
    ln -s stub "$test_root/bin/$command"
done

run_case() {
    local scenario=$1 failure=$2 app=$3 space=$4 expected_status=$5
    local fixture="$test_root/$scenario"
    mkdir -p "$fixture/tdrs-backend"
    cat > "$fixture/tdrs-backend/.env.example" <<'ENV'
OFA_READ_ONLY_PASSWORD=synthetic_test_password_only
OFA_ADMIN_READ_ONLY_PASSWORD=synthetic_test_password_only
OFA_DIGIT_SENSITIVE_PASSWORD=synthetic_test_password_only
ENV
    touch "$fixture/actions"
    if [[ $scenario == existing-env ]]; then
        echo preserve-me > "$fixture/tdrs-backend/.env.ci"
    fi
    local result=0
    (
        cd "$fixture"
        export PATH="$test_root/bin:$PATH" FIXTURE="$fixture"
        export TEST_SCENARIO="$scenario" TEST_FAIL_ACTION="$failure"
        bash "$script_path" "$app" "$space"
    ) > "$fixture/output" 2>&1 || result=$?
    if [[ $result -ne $expected_status ]]; then
        cat "$fixture/output"
        echo "Unexpected exit status for $scenario: $result" >&2
        exit 1
    fi
    if [[ $scenario == existing-env ]]; then
        [[ $(cat "$fixture/tdrs-backend/.env.ci") == preserve-me ]]
    else
        [[ ! -e "$fixture/tdrs-backend/.env.ci" ]]
    fi
    if [[ -e "$fixture/tunnel.pid" ]]; then
        ! kill -0 "$(cat "$fixture/tunnel.pid")" 2>/dev/null
        [[ -e "$fixture/tunnel-stopped" ]]
    fi
    if [[ $failure != none && $failure != install ]]; then
        [[ $(tail -n 1 "$fixture/actions") == "$failure" ]]
        ! grep -q 'Database configuration applied successfully' "$fixture/output"
    elif [[ $scenario == success-* ]]; then
        head -n 3 "$fixture/actions" > "$fixture/first-actions"
        printf 'migrate\ngenerate\napply_grafana_views\n' > "$fixture/expected-actions"
        cmp "$fixture/first-actions" "$fixture/expected-actions"
        grep -qx create_grafana_postgres_role "$fixture/actions"
        grep -qx create_grafana_readonly_postgres_users "$fixture/actions"
        grep -q 'Database configuration applied successfully' "$fixture/output"
    else
        [[ ! -s "$fixture/actions" ]]
    fi
    echo "PASS: $scenario"
}

run_case success-prod none tdp-backend-prod tanf-prod 0
run_case success-dev none tdp-backend-test tanf-dev 0
run_case skip none tdp-backend-test tanf-dev 0
run_case existing-env none tdp-backend-test tanf-dev 1
run_case install-failure install tdp-backend-test tanf-dev 23
for action in migrate generate apply_grafana_views create_grafana_postgres_role create_grafana_readonly_postgres_users; do
    run_case "$action-failure" "$action" tdp-backend-test tanf-dev 23
done
