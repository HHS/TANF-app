# Transitioning TDP Deployments from Cloud.gov Buildpacks to Docker Containers

## Security Posture & Compliance Analysis

**Prepared for:** ACF TDP Stakeholders
**Date:** April 2026
**Related Issue:** [raft-tech/TANF-app#5542](https://github.com/raft-tech/TANF-app/issues/5542)

---

## Summary

This document evaluates whether moving TDP deployments from Cloud.gov-managed buildpacks to team-managed Docker images would **maintain or improve the current security posture** while addressing known operational limitations in the current deployment model.

- **Background on the original buildpack decision:** [ADR-011](../Technical-Documentation/Architecture-Decision-Record/011-buildpacks.md) documents that TDP leveraged Cloud.gov buildpacks in 2021 in part because they provided a faster path to ATO than the team's earlier DockerHub-based approach, which lacked sufficient security documentation for ACF review.
- **What is changing:** TDP would shift from Cloud.gov-managed buildpacks to Docker DHI hardened base images and TDP-managed Docker images for application deployment, while continuing to run the applications inside the same Cloud.gov platform and runtime environment.
- **Implementation status note:** The current repository Dockerfiles still reference standard public images in some base or final stages, including `python:3.10.8-slim-bullseye`, `node:22-alpine`, and `nginx:1.25-alpine`. The DHI-based security claims in this document should be treated as target-state controls until those image baselines are updated to approved DHI images or an equivalent approved hardened-image baseline is documented.
- **Why this is being considered now:** Buildpacks continue to create operational pain points, including long deploy times, repeated dependency downloads, less predictable build behavior, and limited visibility into the full runtime stack. At the same time, Docker image security capabilities and documentation have matured, especially around hardened base images, SBOMs, provenance, signing, and vulnerability management.
- **Security responsibility impact:** This change shifts responsibility for selecting approved base images, maintaining TDP's derived application images, and applying updated DHI releases into the deployment lifecycle from Cloud.gov to the TDP application team. It does **not** mean TDP becomes responsible for remediating CVEs in DHI base images themselves; that remediation remains with the DHI provider. TDP is responsible for rebuilding, validating, and redeploying downstream images after remediated base image versions are published. Based on the current architecture, this does **not** change the Cloud.gov hosting model or the ATO boundary, because the workloads would still run inside the same FedRAMP-authorized Cloud.gov environment and retain the same inherited platform controls.
- **Key tradeoffs:** The main tradeoff is greater operational and security ownership by the TDP team in exchange for better supply chain visibility, reproducibility, auditability, and deployment control. In practice, that means TDP must monitor for remediated DHI releases and update its derived images on an appropriate timeline, and ACF may need to evaluate whether Docker Hardened Images' enterprise tier or similar vendor support is needed if contractual remediation timelines such as a 7-day high/critical CVE response target are required.
- **Registry note:** TDP will store and distribute deployment images through GitHub Container Registry (GHCR). GHCR should be treated as part of the implementation architecture because it affects image access control, retention, provenance, and scanning workflows. Its use does not by itself change the ATO boundary analysis, but SSP and supporting documentation should reflect GHCR as the private registry of record and describe the associated access and monitoring controls.
- **Compliance disposition:** Even though the authorization boundary, data flows, and Cloud.gov hosting environment remain unchanged, the packaging and deployment method change is security relevant. The SSP should be updated and an SIA should be initiated before production adoption to formally document the impact, affected controls, residual risk, and approval path.

---

## 1. Current State: Buildpack Deployment Challenges

TDP currently deploys frontend and backend applications to Cloud.gov using standard buildpacks. While functional, this approach introduces:

| Challenge | Impact |
|-----------|--------|
| **Extended deployment times** | 15–30+ minute deployment windows |
| **Transient network failures** | Dependencies re-downloaded from scratch on every deploy, increasing failure risk |
| **Supply chain volatility** | Upstream package changes can introduce regressions without warning |
| **Environment inconsistency** | No guarantee of identical behavior across dev, staging, and production |
| **Limited control** | Inability to pin or audit the full dependency tree of the runtime environment |

---

## 2. Cloud.gov Security Controls: Inherited Regardless of Deployment Method

Cloud.gov holds **FedRAMP Moderate Authorization**, covering over 60% of the 323 NIST SP 800-53 Rev 5 controls at the infrastructure and platform level.

### 2.1 Control Inheritance Is Deployment-Method Agnostic

The following platform-level controls are **fully inherited by tenant applications regardless of whether buildpacks or Docker images are used**:

| Control Family | Cloud.gov Responsibility | Affected by Deployment Method? |
|----------------|--------------------------|-------------------------------|
| **Physical Security (PE)** | AWS GovCloud data centers | No |
| **Infrastructure Security** | AWS GovCloud services & configuration | No |
| **Platform Security** | Cloud Foundry, container runtime, networking | No |
| **Container Isolation** | garden-runc runtime with cgroups, process namespaces, user namespaces | No |
| **Network Security** | Platform networking, TLS termination, routing | No |
| **Continuous Monitoring** | FedRAMP continuous monitoring, annual assessments | No |
| **CM-2 (Baseline Config)** | Platform configuration baseline | No — platform portion unchanged |
| **AU-12 (Audit Generation)** | Platform event logging | No |

**Critical point:** Cloud.gov does not use Docker's runtime. All applications—whether deployed via buildpacks or Docker images—run under `garden-runc`, built on the Open Container Initiative's `runc` specification. Both deployment methods receive identical container isolation: cgroups for resource limiting, process namespaces for isolation, and user namespaces to prevent privilege escalation.

### 2.2 What Changes: The Shared Responsibility Shift

The primary compliance difference between buildpacks and Docker is **who maintains the base image layer**:

| Responsibility | Standard Buildpacks | Docker (with DHI) |
|----------------|--------------------|--------------------|
| OS-level patching | Cloud.gov (on restage) | TDP team via DHI automated patching |
| Language runtime updates | Cloud.gov | TDP team via Dockerfile version pinning |
| Dependency management | Re-downloaded each deploy (uncontrolled) | Locked in image layers (controlled, auditable) |
| Vulnerability scanning | Limited visibility | Full SBOM + automated CVE scanning |
| Configuration hardening | Opaque buildpack defaults | CIS-benchmarked, STIG-scanned base images |

This shift in responsibility is **not a net loss**—it is a trade of opaque, automatic updates for transparent, auditable, and controlled updates backed by industry-recognized security benchmarks.

---

## 3. Docker Hardened Images: Target Security Guarantees

Docker provides [CIS-validated Hardened Images](https://hub.docker.com/hardened-images/catalog) that are **free to use, share, and build on** under the Apache 2.0 license.

The guarantees below apply only if the approved production image baseline uses DHI images, or an alternative hardened-image source with equivalent documented controls. If the final implementation continues to use standard public images, the SIA and SSP should either document compensating controls or avoid claiming DHI-specific benefits such as CIS validation, SLSA provenance, signed SBOMs, VEX statements, or DHI remediation timelines.

### 3.1 Community Tier (Free) — Security Features

| Feature | Detail |
|---------|--------|
| **Near-zero CVEs** | Continuously scanned and patched to maintain minimal known exploitable vulnerabilities |
| **CIS Benchmark Compliance** | Images validated against CIS Docker Benchmark v1.8.0 |
| **Distroless Variants** | Reduce attack surface by up to 95% compared to standard images |
| **Non-root Execution** | Default least-privilege configuration (FIPS & STIG variants only) |
| **SLSA Build Level 3 Provenance** | Tamper-resistant, verifiable build chain |
| **Signed SBOMs** | Complete Software Bill of Materials for every component |
| **VEX Statements** | CVE exploitability context for accurate risk assessment |
| **Cryptographic Signatures** | Every package and image cryptographically signed and verified |
| **Source-built Packages** | Built from upstream source by Docker, not pulled from third-party repos |
| **Automatic Patching** | Rebuilt when upstream security updates are available |

### 3.2 Enterprise Tier (Available if Needed)

| Feature | Detail |
|---------|--------|
| **7-day CVE SLA** | Critical/high severity vulnerabilities remediated within 7 days |
| **FIPS-enabled Variants** | For cryptographic module compliance |
| **STIG-ready Images** | Meet Department of Defense security requirements |
| **Custom Modifications** | Tailored images for specific compliance needs |
| **Extended Lifecycle Support** | Post-EOL security patches |

### 3.3 How DHI Compares to Buildpack Security

| Security Dimension | Buildpacks | Docker Hardened Images |
|--------------------|-----------|----------------------|
| **Vulnerability visibility** | Limited; opaque stack | Full SBOM with every component listed |
| **CIS compliance** | Not CIS-benchmarked | CIS Benchmark v1.8.0 validated |
| **Supply chain integrity** | Dependencies fetched at deploy time from public repos | SLSA Level 3 provenance, cryptographic signatures |
| **Attack surface** | Full OS with all default packages | Distroless variants reduce surface by up to 95% |
| **Patch transparency** | Automatic but opaque; requires restage | Automatic with full audit trail |
| **Runtime privilege** | Varies by buildpack | Non-root by default |
| **Audit artifacts** | None provided | SBOMs, VEX statements, provenance attestations |

---

## 4. NIST SP 800-53 Control Mapping

The following table maps relevant NIST controls to how they are addressed under the proposed Docker deployment model:

| Control | Description | How Addressed |
|---------|-------------|---------------|
| **CM-2** | Baseline Configuration | CIS-benchmarked DHI base images provide a documented, hardened baseline |
| **CM-6** | Configuration Settings | Dockerfile and image layers provide version-pinned, reproducible configuration |
| **CM-7** | Least Functionality | Distroless DHI variants eliminate unnecessary packages and services |
| **RA-5** | Vulnerability Scanning | DHI continuous scanning + CI/CD pipeline scanning (e.g., Trivy, Grype) |
| **SA-10** | Developer Configuration Management | SLSA Level 3 provenance ensures tamper-resistant build pipeline |
| **SA-11** | Developer Testing & Evaluation | Automated security scanning integrated into image build process |
| **SI-2** | Flaw Remediation | DHI automatic patching; Enterprise tier offers 7-day SLA |
| **SI-7** | Software & Information Integrity | Cryptographic signatures on all images and packages |
| **SC-28** | Protection of Information at Rest | Unchanged — Cloud.gov platform control |
| **AU-12** | Audit Record Generation | SBOMs and provenance attestations provide audit artifacts not available with buildpacks |

---

## 5. Addressing the "Not Recommended" Caveat in Cloud.gov Docs

Cloud.gov's Docker deployment documentation notes that Docker is "not a recommended path" and that users "lose a large set of features." This language warrants context:

1. **The caveat is about operational convenience, not security.** Cloud.gov recommends buildpacks because they reduce the maintenance burden on tenants. With DHI's automated patching and CI/CD integration, this burden is manageable and well-understood.

2. **The "lost features" are buildpack-specific automation.** Specifically, automatic language runtime updates on restage. With Docker, we gain explicit control over when and how these updates occur—improving change management (CM-3) and reducing the risk of unplanned regressions.

3. **Cloud.gov fully supports Docker deployments.** The `cf push --docker-image` workflow is a first-class deployment method. The same `garden-runc` container runtime, the same network isolation, and the same platform security controls apply.

---

## 6. Operational Security Improvements

Beyond maintaining compliance, Docker deployments actively improve our security operations:

### 6.1 Immutable, Versioned Artifacts
Each deployment uses a specific, tagged image digest. If a vulnerability is discovered, we can identify exactly which deployments are affected and roll back to a known-good image instantly.

### 6.2 Reproducible Builds
The same image runs in development, staging, and production. Environment-specific bugs are eliminated, reducing the risk of security issues that only manifest in production.

### 6.3 Supply Chain Control
Dependencies are locked at build time, not fetched from public repositories during each deployment. This eliminates an entire class of supply chain attacks where a compromised upstream package could be pulled into production during a routine deploy.

### 6.4 Enhanced Auditability
SBOMs, provenance attestations, and VEX statements provide audit artifacts that buildpack deployments simply cannot produce. This strengthens our posture for RA-5 (Vulnerability Scanning) and AU-12 (Audit Generation).

---

## 7. Proposed Mitigation Strategy

To address the additional responsibilities that come with Docker deployment, we propose:

| Responsibility | Mitigation |
|----------------|------------|
| **Base image maintenance** | Use DHI images with automated patching; pin to specific digests in CI/CD |
| **OS-level security updates** | DHI continuous scanning and automatic rebuilds on upstream updates |
| **Vulnerability management** | Integrate container scanning (e.g., Grype) into CI/CD pipeline for TDP frontend/backend containers; block deployment on critical/high CVEs |
| **Configuration hardening** | Use DHI or an approved equivalent hardened-image baseline; document any compensating controls if standard public base images remain in use |
| **Continuous monitoring** | Feed container scanner results, GHCR package activity, image digest changes, and DHI/base image update status into the existing process for monthly and quarterly reporting |
| **POA&M and vulnerability reporting** | Track unresolved high/critical container findings, scanner exceptions, overdue base image updates, and accepted residual risks through the applicable ACF/TDP vulnerability management process, including POA&M tracking where required |
| **Incident response** | Detect, triage, contain, and recover from image-related events using scanner alerts, CircleCI job logs, GHCR package activity, image digest inventory, and redeployment of a known-good digest |
| **SSP documentation updates** | Update relevant control narratives to reflect Docker deployment model and DHI security features |

---

## 8. Compliance Review/Updates

ACF feedback correctly identifies the Docker migration as a security-relevant modification even though it does not alter the authorization boundary, data flow, or Cloud.gov hosting environment. The proposed compliance package should therefore include an SIA and targeted SSP updates.

### 8.1 SIA and SSP Updates

The SIA should evaluate the packaging change as a significant security-relevant modification and document:

- No change to the system authorization boundary, Cloud.gov hosting environment, or application data flows
- New or changed implementation details for Docker image build, registry storage, scanning, signing/provenance, and deployment
- TDP responsibility for derived application images and base image update adoption
- Cloud.gov responsibility for the platform runtime, host operating system, network isolation, and inherited FedRAMP controls
- Residual risks associated with GHCR, external base image dependency, image tag/digest management, and delayed vulnerability remediation

### 8.2 Continuous Monitoring, Vulnerability Reporting, and POA&M

Container vulnerability management should be integrated into the existing continuous monitoring (ConMon) process rather than treated as a standalone CI/CD activity.

| Activity | Proposed Documentation Update |
|----------|-------------------------------|
| **CI/CD scanning** | Document container scanning for frontend, backend, and base images during build and before publishing or deployment |
| **Recurring review** | Include container scanner findings, GHCR package activity, image inventory, and base image update status in monthly and quarterly ConMon reporting |
| **Vulnerability reporting** | Report high/critical image findings using the same severity, ownership, due date, and remediation evidence practices used for existing vulnerability sources |
| **POA&M integration** | Open or update POA&M items for overdue remediation, accepted residual risk, scanner exceptions, or findings that cannot be remediated within required timelines |
| **Evidence artifacts** | Retain scan results, SBOMs, image digests, CircleCI workflow/job records, release tags, and remediation validation as audit evidence |

### 8.3 Configuration Management: CM-2 and CM-6

Docker configuration artifacts are stored in the TANF-app GitHub repository and should be treated as version-controlled configuration baseline artifacts.

| Artifact | Repository Location | CM Relevance |
|----------|---------------------|--------------|
| Backend application image | `tdrs-backend/Dockerfile` | Defines backend deployment image composition |
| Backend base image | `tdrs-backend/Dockerfile.base` | Defines backend base runtime and OS package baseline |
| Frontend application image | `tdrs-frontend/Dockerfile` | Defines frontend deployment image composition |
| Frontend base image | `tdrs-frontend/Dockerfile.base` | Defines frontend build/runtime baseline |
| Keycloak image | `tdrs-backend/keycloak/Dockerfile` | Defines Keycloak container image baseline, where applicable |
| CircleCI build/deployment configuration | `.circleci/config.yml`, `.circleci/deployment/workflows.yml`, `.circleci/deployment/jobs.yml`, `.circleci/deployment/commands.yml` | Defines deployment orchestration and should define image build, tag, authentication, and publish process when Docker image publishing is moved into CircleCI |

The SSP should state that Dockerfile changes, base image version changes, CircleCI deployment or image-publishing configuration changes, and production image digest changes are configuration-controlled changes subject to code review, CI validation, release approval, and audit retention.

### 8.4 GHCR ATO Considerations

GHCR introduces an external registry dependency and should be documented explicitly in the SSP, implementation architecture, and SIA.

| Area | Required Documentation |
|------|------------------------|
| **External dependency** | GHCR is the private container registry used to store and distribute TDP deployment images |
| **Access control** | Package read/write permissions should be limited by GitHub organization, repository, package, and team permissions, with CircleCI project and context access managed using least privilege |
| **Authentication method** | CircleCI should publish images using approved GHCR credentials or tokens stored in CircleCI contexts or project environment variables and managed through the existing secret management process |
| **Logging and monitoring** | CircleCI workflow/job logs, package publishing events, repository/package permission changes, CircleCI context or project setting changes, and available GitHub/GHCR audit logs should be retained and reviewed as part of ConMon and incident triage |
| **Image integrity** | Deployments should reference immutable image digests where feasible; mutable tags such as `latest` should not be the sole production reference |
| **Retention and recovery** | Release image tags and digests should be retained long enough to support rollback, forensic review, and audit evidence needs |

### 8.5 Incident Response Detail

The incident response narrative should go beyond rollback and define the expected lifecycle for image-related events.

| Phase | Docker/GHCR-Specific Response |
|-------|-------------------------------|
| **Detection** | Scanner alerts, GHCR package activity, failed CircleCI build or deploy checks, image signature/provenance validation failures, CircleCI audit or job anomalies, and available GitHub/GHCR audit events |
| **Triage** | Determine affected image digest, tag, source commit, SBOM components, environments deployed, severity, exploitability, and whether data or credentials may be affected |
| **Containment** | Pause promotion, restrict or remove affected registry artifacts where appropriate, rotate exposed credentials if indicated, and redeploy the last known-good image digest |
| **Eradication** | Rebuild from a patched base image or dependency set, validate scan results, regenerate SBOM/provenance artifacts, and verify configuration against the approved baseline |
| **Recovery** | Promote the remediated image through the normal release path, validate application health, retain evidence, and update vulnerability or POA&M records |

---

## 9. ATO Impact Assessment

### What Changes

#### New Content Required
- **Container image scanning** must be added to the vulnerability management scanning tools table (currently lists OWASP ZAP, Dependabot, and Webinspect — needs a container scanner like Trivy/Grype with defined frequency)
- **Dockerfiles, CircleCI deployment or image-publishing configuration, release image tags, and container image digests** must be added as configuration management artifacts in the CM tools and CM library sections
- **CI/CD pipeline description** must be rewritten to include CircleCI Docker image build, container scanning, image registry authentication, image publication to GHCR, and `cf push --docker-image` deployment flow
- **Shared responsibility boundary** must be updated to document TDP team ownership of container runtime environment (base image OS packages, system libraries) vs. cloud.gov ownership of host OS and platform
- **Container image baselines** (Dockerfiles, pinned base image versions) must be added as a distinct baseline type in the configuration baselining section
- **Base image source decision** must reconcile current Dockerfile references to standard public images with the target DHI posture; the approved baseline should identify the selected base image source, owner, patch process, and evidence artifacts
- **Risk summary** may need new entries for container image supply chain risks and their mitigations (DHI, image signing, SLSA provenance)
- **Continuous monitoring procedures** must describe how container findings are reported monthly/quarterly and how unresolved findings feed into vulnerability reporting and POA&M management
- **GHCR registry controls** must describe external dependency management, access control, authentication, logging/monitoring, image retention, and incident response expectations
- **Incident response procedures** must include detection, triage, containment, eradication, and recovery for compromised, vulnerable, or untrusted container images

#### New Control Narratives Required
- **CM-7 (Least Functionality)** — no standalone section exists in the SSP; needs language about minimizing attack surface via slim/distroless base images
- **SI-7 (Software & Information Integrity)** — no standalone section exists in the SSP; needs language about Docker image signing, digest verification, and SLSA Level 3 provenance
- **SC-28 (Protection of Information at Rest)** — only briefly mentioned; may need a note about container images at rest in a registry

### What Does Not Change
- **Cloud.gov's FedRAMP package** (F1607067912) and all inherited controls remain unchanged.
- **The platform's container runtime**, network security, and isolation guarantees are identical.
- **The authorization boundary** does not change — applications still run within Cloud.gov's FedRAMP-authorized environment.

### Recommended Path
This transition should be handled through an **SIA-backed significant change review** with targeted SSP updates rather than assuming a full ATO reassessment is required, since:
- The authorization boundary is unchanged
- Inherited controls are unaffected
- The deployment method is a supported Cloud.gov capability
- The security posture is demonstrably maintained or improved
- The SIA can formally document the security relevance, changed implementation responsibilities, and residual risks for AO review

---

## 10. Conclusion

Transitioning from buildpacks to Docker containers built on CIS-validated Hardened Images, or an approved equivalent hardened-image baseline, **maintains our security posture** through Cloud.gov's unchanged inherited controls and **strengthens it** through:

- CIS-benchmarked, continuously scanned base images with near-zero CVEs
- SLSA Level 3 supply chain integrity with cryptographic verification
- Complete SBOMs and audit artifacts that buildpacks cannot provide
- Reduced attack surface through distroless image variants
- Immutable, reproducible deployments that eliminate environment drift

The additional responsibility for base image maintenance is mitigated by DHI's automated patching, continuous scanning, and (if needed) enterprise SLA-backed remediation. Under that target-state model, the TDP team is responsible for monitoring new patches, verifying the patches, and applying them to downstream images rather than managing the full base-image supply chain itself. If the final implementation uses standard public base images instead of DHI or an approved equivalent, the SIA and SSP should document the different residual risk and compensating controls.

---

## References

- [Cloud.gov Compliance Overview](https://docs.cloud.gov/platform/compliance/)
- [Cloud.gov ATO Process](https://docs.cloud.gov/platform/compliance/ato-process/)
- [Cloud.gov Docker Deployment](https://docs.cloud.gov/platform/deployment/docker/)
- [Cloud.gov Shared Responsibilities](https://docs.cloud.gov/platform/technology/shared-responsibilities/)
- [Docker Hardened Images Catalog](https://hub.docker.com/hardened-images/catalog)
- [Docker Hardened Images Features](https://docs.docker.com/dhi/features/)
- [Docker Hardened Images — Free for Everyone](https://www.docker.com/blog/docker-hardened-images-for-every-developer/)
- [FedRAMP Compliance with Hardened Images](https://www.docker.com/blog/fedramp-compliance-with-hardened-images/)
- [CIS Docker Benchmark v1.8.0](https://www.cisecurity.org/benchmark/docker)
- [NIST SP 800-190: Application Container Security Guide](https://csrc.nist.gov/publications/detail/sp/800-190/final)
- [Docker Hardened Images — 2026 Architect's Guide](https://mrcloudbook.com/docker-hardened-images-the-2026-architects-guide-to-supply-chain-compliance/)
