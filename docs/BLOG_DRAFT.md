# I used Splunk to plan a better theme park day

*Draft for author review. Product name: Park Atlas. Screenshots should be added after live browser review; no screenshot or production certification is implied by this draft.*

The question was simple: which ride should I do first?

I was planning a trip with mornings in one park and afternoons in another. I wanted to avoid spending the best part of the morning in a queue that would be just as long—or shorter—later. I also wanted to save paid queue access for the experiences where it would make the most difference.

A live wait-time screen helps once you are standing in the park. I wanted something slightly different: a way to learn from the days before the trip, then use that evidence without pretending it could predict every moment of the visit.

That became Park Atlas, a Splunk app for theme park planning and research.

## From a current reading to useful history

Queue-Times provides a public API with park information and current attraction waits. Its documented live data updates every five minutes. The collector discovers parks, fetches ride snapshots, and emits one JSON event per unique ride in each poll. It handles attractions nested under lands as well as rides at the top level of the response.

The important distinction is time. The event records when we observed the reading, while preserving the source's last-updated timestamp. An unchanged wait is still an observation; it is not evidence that the ride changed state. Missing observations remain missing.

The public API does not document a historical backfill endpoint. Our research therefore starts when our collector starts. That constraint shapes the whole product: tell people how much history exists before asking them to trust it.

## A dashboard should lead to a decision

The first version looked like an operations dashboard: current queues, open rides, trends and collection health. Useful, but it left the visitor to do most of the interpretation.

The refreshed app starts with a different sequence:

- Choose a park and the weekday you expect to visit.
- Check that the data includes enough complete operating days.
- Compare the first 30 minutes with later-day waits.
- Choose an opening priority and a backup.
- Recheck live conditions before committing to a line.

“Potential minutes avoided” is a deliberately simple comparison: later-day median posted wait minus the opening-period median. It is not a guaranteed saving, a forecast, or a score that knows what your family enjoys. A ride with a large early advantage is a candidate to investigate, not an instruction to sprint across the park.

The tables also show the next half-hour, a longer-wait P95 value, early availability and the number of observed days. That makes the reasoning reviewable.

## The blank panel that taught us something

One of the most useful bugs appeared as an empty planning panel.

Some attractions—especially shows and exhibits—remained marked open overnight. If any open attraction defined the start and end of a park day, the inferred operating window could stretch across the entire calendar day. The completeness check then rejected that day.

The fix was to infer boundaries from attractions observed both open and closed during the day. Always-open entries could no longer define the opening time. We also added a readiness table and explicit insufficient-data messages. A blank recommendation now means “here is the evidence you still need,” rather than silently suggesting the app is broken.

These are still inferred hours. Early entry may precede general admission, overnight operations cross calendar boundaries, and an API status is not an official operating schedule. The app keeps those limitations visible.

## Reliability belongs in a trip plan

A low wait is not useful if the ride is unavailable when you arrive.

Park Atlas groups consecutive unavailable observations into episodes. A completed episode needs an open observation before and after it. Collection gaps and incomplete episodes do not contribute to typical completed-duration statistics.

Even then, “unavailable” is not the same as “mechanical failure.” Weather, maintenance and planned closures can produce the same status. The useful planning question is not “can I diagnose the attraction?” It is “should I have another nearby priority ready?”

## The unglamorous part: operating the collector

Collecting every park every five minutes used approximately 686–698 MiB per day in our initial deployment. That exceeded the trial license's daily allowance and eventually blocked application searches.

Indexing continued, so the collected history was still there when a developer license restored search access. We reduced the example collection schedule to five minutes for Disney World and fifteen for other parks. The lesson was straightforward: estimate and measure ingestion before expanding a prototype's scope.

Another practical limit is the laptop. Docker cannot keep collecting while its host sleeps. Persistent volumes protect stored history, but they cannot recover snapshots that were never requested. An always-on host is the right place for continuous research.

## A product with a point of view

The visual refresh gives Park Atlas a simple story: less waiting, more of the day you came for.

The Start Here page explains the research loop. A general Park Planner supports any collected park, while a Disney World workspace keeps those four parks close at hand. Live queues, wait research, reliability and data health remain available without making the visitor start with an administrator's view.

The implementation stays close to native Splunk: Simple XML, local CSS, a Python standard-library collector, and no external fonts or tracking scripts. The public package excludes local credentials, runtime settings, vendor license files and indexed data.

It does not book rides, optimize walking routes, or know your must-dos. Those are intentional boundaries. The next useful step is a personal shortlist and a two-park workspace with explicit travel-time assumptions—not a more impressive-looking prediction built on weak evidence.

## Try the release candidate

The source and installation instructions are at [theme_park_wait_times](https://github.com/matt-snyder-stuff/theme_park_wait_times). Start with a small collection scope, check your Splunk license allowance, and let complete days accumulate before relying on recommendations.

Park Atlas is a community project, not an official park product. It is not AppInspect- or Splunkbase-certified. The most valuable output is a better-informed conversation about the day you want, with enough flexibility to enjoy it when reality changes the plan.

**Powered by [Queue-Times.com](https://queue-times.com/).** [API documentation](https://queue-times.com/en-US/pages/api). For licensing context, see [Splunk's trial enforcement guidance](https://www.cisco.com/c/en/us/support/docs/observability/splunk-platform/splunk-enterprise/5/SPLK051873-troubleshooting-search-lockdown-due-to-splunk-tria.html).

### Editorial assets to capture before publication

1. Start Here: the product promise and three planning entry points.
2. Opening priorities: selected park, readiness and evidence columns visible.
3. A before/after example of always-open attractions affecting inferred hours.
4. Reliability ledger: completed and incomplete episodes clearly distinguished.

Use screenshots from an authenticated local review with account details and credentials excluded. Date any example wait statistics and label their sample size.
