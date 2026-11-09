[queue_times://<name>]
park_ids = <* or comma-separated positive integers>
* Use * to discover and collect every available park each poll.
* Required. Park identifiers from https://queue-times.com/parks.json.
interval = <integer>
* Poll interval in seconds, minimum 300. Default 300.
index = <string>
* Destination index. Default queue_times.
disabled = <boolean>
* Set to 0 to enable collection.

exclude_park_ids = <comma-separated positive integers>
* Optional. Skip these parks, including when park_ids is *.
