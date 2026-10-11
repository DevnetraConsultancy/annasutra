# 12. Infrastructure and deployment

## Layout

- Single Indian region. Two small app instances behind a load balancer, one worker, managed PostgreSQL with point-in-time recovery, S3-compatible object storage.
- Cloudflare in front of everything. Origin accepts only Cloudflare or private-tunnel traffic. Admin behind Cloudflare Access.
- Three environments (development, staging, production) in separate accounts or projects. No real data outside production.
- Infrastructure as code (Terraform or the provider's equivalent). No manual changes on servers.
- Domain: needed for the public QR link, for passkey domain association files, and for the API. Register early and keep it under the organisation's control.

## CI/CD

Protected main branch, mandatory review, signed commits, secret scanning, dependency scanning, container scanning, code scanning, software bill of materials, automated tests (backend and mobile), deploy only from the pipeline. Mobile: build with the pipeline, sign with keys held by the human or a managed signing service, never in the repo.

## Backups and recovery

- Continuous log shipping with point-in-time recovery plus daily snapshots, copied to a **separate account with immutable storage**. Object storage versioned.
- Starting targets [R]: recovery point under 15 minutes, recovery time under 4 hours. Adjust after testing.
- **Quarterly restore drill**, including hash-chain verification against the external anchors.

**Disaster recovery procedure:** declare an incident, restore the latest backup to a standby instance, verify hash chains against anchors, switch traffic, let apps resume sync (safe because events are idempotent), write a post-incident review.

## Monitoring and alerting

Uptime checks, error rates, queue lag, database health, disk, certificate expiry, auth-failure spikes, sync-reject spikes, hash-verification result. Alerts go to a named on-call person. Test the alert path monthly.

## Cost drivers to quote (do not guess)

Hosting, managed database, object storage, Cloudflare plan, SMS (with sender registration), QR sticker printing, device subsidies, field training and support, external penetration test, Apple and Google developer accounts, domain.

## What triggers a bigger architecture

See `02_architecture.md`. Do not add Kubernetes, Kafka, a service mesh or a blockchain without a written, measured reason.
