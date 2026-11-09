# Park Atlas 1.2.1 — QA release candidate

Fixes trip-planning flow, analytical edge cases, health reporting and release metadata.

- Ride choices follow the selected park immediately; specific shortlists override All rides.
- A 60-day research window supports seven matched weekdays.
- Afternoon recommendations display arrival-clipped windows and exclude overnight observations.
- Early availability includes days when the ride did not open during the early window.
- Validate dates, times and imported data; add JSON import, readable brief labels and brief-only printing.
- Group health records by stable park ID.
- AppInspect metadata fixes and explicit modern Python declarations, preserving Splunk 9.4.13 behavior.
- Add regression tests, a QA report, and AppInspect failure gating in CI.

Local verification: 13 Python tests, controller tests, live SPL regressions, btool and release-hygiene checks. AppInspect 4.4.0 precert: zero failures/errors with five documented warnings. See docs/QA_REPORT.md.

Still a prerelease: actual browser flows, accessibility and responsive/print layout have not been verified because browser control is unavailable. This is not Splunkbase or Splunk Cloud certification. GitHub pictures are labeled illustrations.

Install `queue_times-1.2.1.tar.gz` over the existing app and preserve local configuration. Indexed history is unchanged. Powered by Queue-Times.com.
