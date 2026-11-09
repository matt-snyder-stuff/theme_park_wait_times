# Park Atlas 1.2.0 — release candidate 1

This update addresses data-quality gaps and adds a practical two-park trip brief.

## New and fixed

- Outage segmentation follows the expected collection cadence, with a tolerance of two intervals plus one minute. Fifteen-minute polling no longer breaks an episode because of ordinary request jitter.
- Completed days require at least 90% estimated poll coverage and no excessive mid-day gap. Coverage and largest gaps appear in planner readiness.
- New events include the configured polling interval; older data uses an inferred median interval.
- My Trip adds a visit date, two parks, confirmed entry time, transfer allowance, shortlists, party reminders and a backup plan.
- My Trip comparisons use matched weekdays and equal-weight daily medians, with daily variability visible.
- User-scoped browser-local saving, JSON download and print/PDF controls. No personal trip data is sent to GitHub.
- README and blog now include three original, explicitly labeled editorial illustrations, provided in SVG and PNG formats.

## Verification

Ten Python tests and the JavaScript controller tests pass. Live Splunk regression searches verify completed outages, always-open attraction handling, missing mid-day coverage, and fifteen-minute polling jitter. The two trip searches return actual evidence rows. Release package and credential-exclusion checks pass.

## Limitations

Browser interaction, responsive/accessibility review and AppInspect remain outstanding because browser control is unavailable in this environment. The images are illustrations, not app screenshots. This is a prerelease.

The trip brief is not a walking-route optimizer. Party notes and reservations are reminders, not automatically enforced constraints. Entry times are user-confirmed; official hours are not imported. Transfers assume both parks share a timezone. Browser saves do not sync between devices. Do not add individual opening advantages together as promised itinerary savings.

Install the attached `queue_times-1.2.0.tar.gz` over the existing `queue_times` app, preserving local configuration and indexed history. Powered by Queue-Times.com.
