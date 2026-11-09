# Release checklist — 1.1.0 candidate

## Automated / local checks

- [x] Unit tests, including exclusion and daylight-saving scenarios.
- [x] Dashboard generators complete and emitted XML parses.
- [x] Build is repeatable without accumulating duplicate panels or options.
- [x] Package includes only app code/configuration/assets and excludes local settings.
- [x] Release checker finds no local secrets in publishable files.
- [x] Splunk btool validation passes on 9.4.13.
- [x] New landing-page and planner searches execute on real indexed data.
- [x] CSS asset is served by Splunk Web.

## Required before promoting to a stable public release

- [ ] Live browser review: desktop and narrow viewport, navigation, Apply, cascading ride selection, no-data states and table links.
- [ ] Keyboard focus, contrast and screen-reader review of the new presentation.
- [ ] Blog screenshots captured from the reviewed live app without sensitive details.
- [ ] Blog author review and final screenshot captions.
- [ ] Splunk AppInspect assessment or explicitly documented outstanding findings.
- [ ] CI run reviewed on GitHub.
- [ ] Repository private vulnerability reporting enabled.

Browser automation was unavailable during the initial refresh session (native browser-control service failed to start). Search execution and XML parsing are not substitutes for this visual review. Publish as a release candidate until the required review is complete.

## Release contents

- Source code and MIT license.
- `queue_times-1.1.0.tar.gz` code-only app package.
- Release notes identifying the stable `queue_times` app ID and new Park Atlas display name.
- No `.env`, `queue_times/local`, vendor `.lic` files, indexed data or cached bytecode.

## 1.2.0 candidate update

- [x] Ten Python unit tests pass, including configured-cadence emission.
- [x] JavaScript controller tests pass for user scoping, save/load, malformed data and text-only rendering.
- [x] Live SPL scenarios reject missing mid-day coverage and accept normal 15-minute polling jitter.
- [x] My Trip morning and afternoon queries return real evidence.
- [x] Original illustrations rendered and visually inspected; labeled as non-screenshots.
- [ ] Browser interaction / accessibility checks and AppInspect still required.
