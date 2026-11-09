# Contributing

Start with a focused issue or pull request describing the planning problem, expected behavior, and evidence. Keep public changes free of credentials, collected ride-event dumps and vendor license files.

Run the unit tests, rebuild dashboards, package the app and run the release checker using the commands in the README. Changes to calculations need scenario tests for gaps, sparse data, closed rides and local-day boundaries. Do not fill missing observations with invented history.

Use the standard-library collector and native Splunk dashboards where practical. Keep attribution visible. Document any new external dependency, permission or network destination. Include manual browser validation for visual changes; a successful SPL search does not prove that a dashboard renders correctly.
