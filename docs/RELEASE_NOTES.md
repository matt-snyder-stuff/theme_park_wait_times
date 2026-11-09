# Park Atlas 1.1.0 — release candidate 1

Park Atlas turns Queue-Times observations into a theme park planning and research workspace in Splunk. Start with an opening priority, compare later opportunities, and keep a backup ready.

This candidate introduces a guided home page, a worldwide Park Planner, a focused Disney World workspace, a shared dark teal/amber theme, clearer data-readiness messages, and in-app research and setup guides. The repository includes a blog draft, Docker setup helper, MIT license, CI validation and code-only packaging.

## Install or upgrade

Install `queue_times-1.1.0.tar.gz` using Splunk's app installation interface. The app ID remains `queue_times`; existing index data and local configuration remain in place. New package installations leave collection disabled until configured. See the README for Docker and distributed-deployment notes.

## Validated

- Nine unit tests, repeatable dashboard generation, XML/navigation validation, package exclusions and local-credential scanning.
- Splunk Enterprise 9.4.13 btool check.
- New views registered; landing-page, data-readiness, opening-priority and live-board queries execute against actual collected data.
- The new CSS is served by Splunk Web and matches the packaged asset.

## Remaining before stable release

Live browser rendering, responsive/keyboard review, blog screenshots and Splunk AppInspect have not been completed. Browser automation was unavailable during this refresh. This is a prerelease, not a certified Splunkbase or Splunk Cloud app. Review the release checklist before promoting it.

The planner infers operating hours and compares sampled posted waits. It does not provide official schedules, guaranteed savings, reservation inventory, walking routes or historical API backfill.

Powered by Queue-Times.com. Community project; no endorsement by park operators, Queue-Times or Splunk is implied.
