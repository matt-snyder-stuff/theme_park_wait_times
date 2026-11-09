# Queue Times Observatory for Splunk

Installable Splunk app with a Python 3 modular input and three dark-theme Simple XML dashboards. No pip dependencies or API key required. Powered by [Queue-Times.com](https://queue-times.com/).

## Install

1. Install `dist/queue_times-1.0.0.tar.gz` through Splunk Web → Apps → Manage Apps → Install app from file, or extract it into `$SPLUNK_HOME/etc/apps`. Restart Splunk.
2. The bundled `indexes.conf` provisions a `queue_times` index on a single-instance Enterprise deployment with 90-day retention. For distributed deployments, provision this index on the indexers, deploy search configuration and dashboards to search heads, and run the input on **one** Python-capable heavy forwarder or collection instance. Do not enable duplicate collectors on search-head members. Review storage and retention for your volume.
3. Find park IDs at https://queue-times.com/parks.json. Create `queue_times/local/inputs.conf`:

   ```ini
   [queue_times://selected_parks]
   park_ids = 2
   interval = 300
   index = queue_times
   disabled = 0
   ```

   ID 2 is the API documentation's Thorpe Park example. Replace or extend it with your selected IDs. Alternatively use Settings → Data inputs → Queue-Times. Ensure the input is enabled and uses a poll interval of at least 300 seconds.
4. Restart Splunk after file-based input changes. Allow outbound HTTPS to `queue-times.com:443`; TLS certificate verification is enabled. Grant dashboard users search access to the index.
5. Open **Queue Times Observatory**. Verify `index=queue_times sourcetype=queue_times:health`, then `index=queue_times sourcetype=queue_times:ride`.

For a different destination index, set `index` on the input and override the `queue_times_index` macro in `local/macros.conf`. Provision that index separately. Splunk Cloud requires the normal app review process and appropriate index provisioning; this package has not been AppInspect-certified. Collection may be hosted on a heavy forwarder feeding Cloud. Target: Splunk Enterprise 9.x/10.x with Python 3; runtime compatibility still needs validation on your version.

## Dashboards

- **Live Operations:** open-ride and wait KPIs, ranked queues, park availability, ride board and geographic wait map. Latest observation per park/ride from the last 30 minutes; source age is shown independently.
- **Wait-Time Trends:** selectable history window, park trends, median/P95/peak ride waits, observed availability and hourly patterns. Times follow the Splunk user's timezone. Closed snapshots are excluded from wait averages. Availability includes overnight closures and is not an uptime SLA.
- **Collection Health:** success/error counts, last contact, latency and error details. Contact older than 15 minutes is flagged. This is a dashboard, not a configured notification alert.

No synthetic events are shipped. Empty dashboards before the first poll are expected. The real-time API supplies no historical backfill: history accumulates as polling runs. Missing rides are not inferred to be closed. The live board can retain a ride's last observation for up to 30 minutes; consult freshness fields.

## Data and collection behavior

`queue_times:ride` emits one event per unique ride per poll, covering both land-nested and top-level rides. Fields include `park_id`, `park_name`, `group_name`, `country`, `continent`, coordinates, `park_timezone`, `land_id`, `land_name`, `ride_id`, `ride_name`, `is_open`, `wait_time` (minutes), `last_updated` (upstream UTC), and `observed_at` (epoch seconds).

Splunk `_time` is observation time. Repeated source timestamps are intentionally retained as periodic observations, so historical charts measure sampled waits rather than change frequency. No checkpoint is needed because each run collects a current snapshot. Duplicate collection instances will produce duplicate samples.

`queue_times:health` records per-park status, ride count and request duration, or catalog failures. A failed park does not prevent collecting subsequent parks. Requests have a 30-second timeout and up to three attempts for transient network errors, HTTP 429 and selected 5xx responses, with bounded exponential backoff. Catalog is refreshed each run. Inputs execute once and exit; Splunk schedules subsequent runs. Large park selections can take longer than five minutes during outages, so monitor latency and freshness.

Estimate daily ride-event volume as `selected ride count × 288`, plus health events. Use `park_ids = *` to discover all parks each poll, or explicit park IDs to keep collection scoped.

## Development and validation

```sh
python3 -m unittest discover -s tests -v
python3 queue_times/bin/queue_times.py --scheme
python3 scripts/package.py
```

Tests cover normalization, duplicate ride IDs, XML escaping, input validation, isolated park errors, catalog failures, and XML parsing. Before production deployment, run Splunk AppInspect, verify configuration with `splunk btool check`, enable a single park, and confirm all panels render and searches execute on the target Splunk version. A local Splunk runtime is not bundled.

API reference: https://queue-times.com/en-US/pages/api

## Local Docker instance

`compose.yaml` runs Splunk 9.4.13 at http://localhost:8000 with persistent configuration and index volumes. The admin password is in the git-ignored `.env` file (username `admin`). Ports bind only to loopback. On Apple Silicon this image runs with amd64 emulation.

The local setup enables all API-listed parks (`park_ids = *`) through `queue_times/local/inputs.conf`. Edit that file to select other parks. The `docker/inputs.conf` file is a starter example. Local settings are excluded from release packages.

```sh
docker compose up -d
docker compose logs --tail 50 splunk
docker compose stop
```

Restart after input configuration changes with `docker compose restart splunk`. `docker compose down` removes the container but preserves volumes. The compose setup uses Splunk's license-acceptance startup flag and the bundled trial license; it does not provision a paid license.

## Observed hours and ride reliability

The **Hours & Ride Reliability** dashboard compares the first and final 60 minutes of inferred daily park operations, shows ride-level median/P95 completed unavailable durations, and ranks each ride's most frequently unavailable local hour with sample and day counts.

Observed hours use the earliest and latest open ride snapshot for each park-local calendar date. Opening/closing summaries include only completed local days with at least one poll at least four minutes before and after those boundaries, and at least two hours between them. This excludes today's moving closing boundary and many partial collection days; it is still an estimate, not a published schedule. Parks operating across midnight are split into calendar days. Data absent from the API cannot be recovered.

New ride events carry `park_local_date`, `park_local_hour`, `park_local_time` (ISO timestamp with offset), and `park_day_end` (next local midnight as epoch). Timezone conversion uses the API's IANA timezone and handles daylight saving changes. Events collected before these fields were introduced are excluded from this dashboard.

A completed unavailable episode requires an open observation before and after a consecutive closed sequence, within the same inferred operating day. Gaps over 15 minutes break sequences; incomplete episodes remain visible in the ledger but are excluded from typical-duration metrics. Duration runs from the first unavailable observation to the next open observation; `observed_minutes` is the span directly observed unavailable, and transition uncertainty is the sum of the two transition sampling intervals. These are polling-based estimates, not incident logs. Unavailable may mean weather, maintenance, a scheduled closure, or another cause.

Hourly likelihood is the percentage of collected ride snapshots marked unavailable within inferred park hours, not a forecast or a failure-start probability. The dashboard shows exposure counts and days; sparse history should not be interpreted as a stable trend. First/final-hour wait metrics include open rides only. Full-park closures truncate inferred hours, which can bias both hour and outage estimates.

Local validation completed on Splunk 9.4.13 in Docker: configuration validation passed, live API events indexed with local-time fields, and all 30 dashboard/input searches executed successfully. Search-only synthetic scenarios verified repeated outage durations, collection-gap exclusion, observed boundaries, and partial-day exclusion; no fixture events were indexed. Seven Python unit tests passed, including a daylight-saving transition. Visual browser rendering and AppInspect certification remain separate checks.

To repeat the integration checks:

```sh
docker cp scripts/check_splunk.py queue-times-splunk:/tmp/check_splunk.py
docker cp scripts/check_reliability.py queue-times-splunk:/tmp/check_reliability.py
docker exec -u splunk queue-times-splunk /opt/splunk/bin/splunk cmd python3 /tmp/check_splunk.py
docker exec -u splunk queue-times-splunk /opt/splunk/bin/splunk cmd python3 /tmp/check_reliability.py
```

## Disney World trip planner

Open **Disney World Planner** in the app navigation, or visit http://localhost:8000/en-US/app/queue_times/disney_world. It is restricted to the API catalog's four Walt Disney World parks: Magic Kingdom (6), EPCOT (5), Hollywood Studios (7), and Animal Kingdom (8).

Select a park, ride, visit weekday, and learning window. The best-hour table ranks each ride's eligible hours by median open wait, then P95 and number of days; it shows the difference from that ride's busiest eligible hourly median. Recommendations require at least 12 samples per hour and three distinct days by default (adjustable to one or seven). This difference is a historical comparison, not guaranteed time saved. The hourly matrix, wait curve, observed opening/closing comparison, unavailable frequency table and live ride board support planning. The live board ignores history and weekday filters.

Hours use Orlando local time. December 2026 trip planning currently learns from data collected since November 2026, not prior Decembers. Holiday demand and operating schedules can differ. This is a timing aid, not a walking-route or reservation optimizer; Lightning Lane inventory, early-entry eligibility, official schedules and personal ride priorities are not available from this API. Sparse recommendation panels remain empty until enough history accumulates. The hourly curve is exploratory and is not subject to the recommendation sample threshold.

The planner's primary **Opening priorities** table supports saving passes for later: it compares each ride's median wait in the first 30 minutes of observed operations with its later-day median, then ranks positive differences largest first. It also shows the next 30 minutes, early P95, early open percentage and distinct-day counts. A second table breaks the first hour into 15-minute intervals to assess how rapidly waits grow. Opening rankings require eligible completed days, the selected minimum days in both periods, at least six early open snapshots and 12 later open snapshots. Potential wait avoided is a historical difference, not a guaranteed saving or a measure of pass value. Observed opening may include early entry before general admission; confirm your access and actual park hours before using that window.

### Planning panel readiness

The planner shows observed and eligible completed days per park. Until the selected minimum is met, tables explain why no qualifying results exist; select the one-day exploratory setting to inspect early evidence without changing the default three-day threshold. Daily operating boundaries now use only attractions observed both open and closed that local day, excluding always-open shows from the boundary calculation. Hourly recommendations are restricted to those inferred operating windows. This remains an estimate: sparse coverage, overnight operations and unusually timed attractions can affect it.


## License incident and collection cadence (November 9, 2026)

The 500 MB/day Enterprise Trial reached five overage warnings after worldwide five-minute collection used approximately 686–698 MiB/day. Searches of application indexes are blocked by license enforcement; indexing continues. No indexed history or license records were deleted.

The local Docker configuration now polls Disney World (IDs 5,6,7,8) every 300 seconds and all other parks every 900 seconds, using `exclude_park_ids` to avoid duplicates. This should substantially reduce daily volume; confirm actual use after a full new day in Settings → Licensing. Today's already-consumed volume cannot be undone by lowering the rate. The collector-contact dashboard flags observations older than 30 minutes. Worldwide outage estimates are now coarser; the existing 15-minute gap rule can classify non-Disney episodes as incomplete. Disney's five-minute resolution is unchanged.

To restore search, obtain a valid appropriately sized Enterprise/developer license or a Splunk-issued reset license, then install it through Settings → Licensing → Add License. A restart may be required. Lowering ingestion does not clear existing warnings. Do not recreate volumes or remove license history to bypass enforcement. Switching to Free is not a volume solution: its allowance is also 500 MB/day and its warning threshold is lower.

Official resolution: https://www.cisco.com/c/en/us/support/docs/observability/splunk-platform/splunk-enterprise/5/SPLK051873-troubleshooting-search-lockdown-due-to-splunk-tria.html

Suggested support request: “My local Splunk Enterprise 9.4.13 trial reached five daily indexing overages at approximately 686–698 MiB/day against the 500 MB/day allowance. I have reduced non-Disney collection from five to fifteen minutes, preserving five-minute collection for four Disney World parks. Please advise on a trial reset license or a suitable development license to restore searches of existing indexed data.”
