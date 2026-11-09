# Product direction: Park Atlas

## Promise

Help a visitor turn observed queue patterns into a flexible park-day plan. Answer “what first?”, “what later?”, and “what if it closes?” with evidence visible beside each suggestion.

## First-release journey

1. Start Here explains the research loop and shows live collection coverage.
2. Park Planner narrows the research to a park, weekday and learning period.
3. Readiness makes missing evidence explicit before recommending rides.
4. Opening advantage identifies candidate first stops, with early availability and sample counts.
5. Hourly and closing comparisons identify flexible rides and later opportunities.
6. Live Explorer and Ride Reliability support decisions when conditions change.
7. Research and Setup guides explain assumptions and operating responsibilities.

## Design principles

- A plan is a set of priorities and alternatives, not a false promise of minute-by-minute precision.
- Show why a recommendation exists. Never hide sparse history behind a score.
- Use park-local time and distinguish observation freshness from source freshness.
- Never substitute synthetic values for missing history.
- Keep collectors and credential handling out of normal trip-planning flows.
- Honor attribution without implying affiliation with park operators.

## Visual system

Night-sky surfaces, teal navigation cues, warm amber accents, large editorial headlines, compact explanatory cards, readable tables and native Splunk controls. No remote font dependency or custom JavaScript. CSS is scoped to dashboard presentation and custom `pp-` components. Native tables and controls remain intact.

## Next priorities

- A saved personal shortlist with must-do, optional and backup categories.
- A two-park itinerary workspace with explicit transfer-time assumptions.
- Official-hours import with provenance and an early-entry eligibility setting.
- Daily summaries to make long-range research faster on small local instances.
- Confidence and collection-gap summaries beside each recommended hour.
- Broader Splunk-version validation, browser accessibility testing and AppInspect.

These are future features, not capabilities claimed by the current release candidate. There is no booking, ticket purchase, route optimization or paid-access inventory integration.
