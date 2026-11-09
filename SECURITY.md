# Security

Never include `.env`, `queue_times/local`, Splunk license files, private keys or indexed data in a public issue or pull request. Use sanitized examples.

The Docker example binds ports to localhost and stores credentials in a git-ignored file. It is a development setup, not a hardened internet-facing deployment. The public collector makes outbound HTTPS requests to queue-times.com with certificate validation enabled.

If you discover a vulnerability, use the repository's private vulnerability-reporting channel when available. Do not post exploit details or credentials in a public issue. Repository maintainers should enable private vulnerability reporting before the first public release.
