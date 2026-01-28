
#!/usr/bin/env bash
set -euo pipefail
URL=${1:-}
EXPECT=${2:-200}
TIMEOUT=${3:-120}

if [ -z "$URL" ]; then
  echo "Usage: smoke-test.sh <url> [expected_status] [timeout_seconds]" >&2
  exit 2
}

echo "Smoke testing $URL expecting HTTP $EXPECT (timeout ${TIMEOUT}s)"
end=$((SECONDS+TIMEOUT))
while [ $SECONDS -lt $end ]; do
  code=$(curl -ks -o /dev/null -w '%{http_code}' "$URL") || true
  echo "Got $code"
  if [ "$code" = "$EXPECT" ]; then
    echo "OK"
    exit 0
  fi
  sleep 5
done
echo "Timeout waiting for $URL to return $EXPECT" >&2
exit 1
