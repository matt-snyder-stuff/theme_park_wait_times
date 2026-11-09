# QA report — Park Atlas 1.2.1 candidate

Reviewed November 9, 2026. Scope: app source, generated views, live Splunk searches, local package, browser-controller unit tests, GitHub content and release configuration.

## Issues found and corrected

| Issue | Correction | Evidence |
| --- | --- | --- |
| Ride menus used last-submitted park | Lookup queries use current `form` park tokens | Structural regression test |
| All rides could override chosen rides | Controller normalizes selections; SPL only treats standalone `*` as all | Controller regression and query inspection |
| Seven matched weekdays unavailable in 30-day window | My Trip now uses 60 days | Structural test |
| Arrival at 14:30 could recommend “14:00” | Explicit arrival-clipped time windows; exclude observations outside park operation | Live query asserts every returned window starts after arrival |
| Closed mornings excluded from availability denominator | Availability includes all complete days, even without an early open-wait comparison | Synthetic SPL scenario returns 50%, not 100% |
| Invalid dates/times could be saved | Calendar/time/transfer validation before save, import, load, print and export; query-side guards | Controller tests |
| JSON export had no restore path | Added local file import with schema checks and a 100 KB limit | Controller import tests |
| Saved brief showed internal labels and invalid nested HTML | Friendly labels, park names, safe text rendering and a div container | Controller and structural tests |
| Printing edited settings could include old search results | Print brief only; research results are not mixed into the printout | Code review; browser print dialog still needs manual verification |
| Health failures and successes split into different rows | Group by stable park ID, with park name as a display field | Query review |
| AppInspect metadata/runtime declarations missing | Added app id/version, disabled Splunkbase update lookup, and declared modern Python runtimes | Local AppInspect and Splunk 9.4.13 btool |

## Automated and live verification

- 13 Python unit/structural tests passed.
- JavaScript controller tests passed: user-scoped storage, save/load, malformed data, invalid dates, reversed times, mixed All/specific rides, JSON import and text-only rendering.
- Live two-park searches returned evidence for the selected historical weekday; afternoon windows respect arrival.
- Existing outage tests verify repeated episodes, gap exclusion, always-open shows, coverage gaps and fifteen-minute jitter.
- Repeatable dashboard build, XML/navigation/asset checks and code-only packaging.
- Known local credential values absent from publishable source and package.
- Splunk btool configuration check passed.
- README illustration paths exist, all navigation targets resolve, and repository metadata/release links were inspected.

## AppInspect 4.4.0

Local `precert` mode: **0 failures, 0 errors, 126 successes, 5 warnings, 1 skipped, 122 not applicable**. Trusted-library metadata was refreshed for the review run.

Warnings concern Cloud Victoria input deployment, SplunkJS informational detection, legacy Python-migration guidance, the presence of a modular input, and Cloud's `sc_admin` role. The target remains local Enterprise 9.4.13; Cloud is not certified. The modern `python.required` declaration is ignored by 9.4.13 according to its installed inputs.conf specification, so the existing `python.version = python3` behavior remains.

AppInspect is now part of CI, with explicit failure/error-count gating because a validator process exit code alone is insufficient. A local CLI pass is not Splunkbase certification or a substitute for manual review.

## Remaining limitations

Native browser control failed to start again. Therefore no claim is made that desktop/mobile rendering, actual input interaction, download/import dialogs, print layout, keyboard navigation or screen-reader behavior has passed end-to-end browser testing. Controller tests use mocks and do not replace that work.

The GitHub pictures are clearly labeled original illustrations, not screenshots. Saved trip data remains browser-local; official hours, route optimization and automatic enforcement of party requirements/reservations are outside the current app's capabilities.
