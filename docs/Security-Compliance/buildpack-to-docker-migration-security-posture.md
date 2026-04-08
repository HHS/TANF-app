# Transitioning TDP Deployments from Cloud.gov Buildpacks to Docker Containers

## Security Posture & Compliance Analysis

**Prepared for:** ACF TDP Stakeholders
**Date:** April 2026
**Related Issue:** [raft-tech/TANF-app#5542](https://github.com/raft-tech/TANF-app/issues/5542)

---

## Summary

This document demonstrates that migrating TDP deployments from Cloud.gov buildpacks to Docker containers—built on CIS-validated hardened base images—**maintains or improves our security posture** while resolving significant operational pain points. Cloud.gov's FedRAMP Moderate inherited controls remain fully intact regardless of deployment method, and Docker Hardened Images (DHI) provide security guarantees that meet or exceed what buildpacks offer at the application image layer.

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

## 3. Docker Hardened Images: Security Guarantees

Docker provides [CIS-validated Hardened Images](https://hub.docker.com/hardened-images/catalog) that are **free to use, share, and build on** under the Apache 2.0 license.

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

4. **Other federal systems on Cloud.gov use Docker.** This is not unprecedented in the ACF or broader federal ecosystem.

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
| **Configuration hardening** | DHI images are pre-hardened to CIS benchmarks; no manual hardening required |
| **Incident response** | Immutable images simplify forensics; roll back by redeploying a previous digest |
| **SSP documentation updates** | Update relevant control narratives to reflect Docker deployment model and DHI security features |

---

## 8. ATO Impact Assessment

### What Changes

#### New Content Required
- **Container image scanning** must be added to the vulnerability management scanning tools table (currently lists OWASP ZAP, Dependabot, and Webinspect — needs a container scanner like Trivy/Grype with defined frequency)
- **Dockerfiles and container image digests** must be added as configuration management artifacts in the CM tools and CM library sections
- **CI/CD pipeline description** must be rewritten to include Docker image build, container scanning, image registry, and `cf push --docker-image` deployment flow
- **Shared responsibility boundary** must be updated to document TDP team ownership of container runtime environment (base image OS packages, system libraries) vs. cloud.gov ownership of host OS and platform
- **Container image baselines** (Dockerfiles, pinned base image versions) must be added as a distinct baseline type in the configuration baselining section
- **Risk summary** may need new entries for container image supply chain risks and their mitigations (DHI, image signing, SLSA provenance)

#### New Control Narratives Required
- **CM-7 (Least Functionality)** — no standalone section exists in the SSP; needs language about minimizing attack surface via slim/distroless base images
- **SI-7 (Software & Information Integrity)** — no standalone section exists in the SSP; needs language about Docker image signing, digest verification, and SLSA Level 3 provenance
- **SC-28 (Protection of Information at Rest)** — only briefly mentioned; may need a note about container images at rest in a registry

### What Does Not Change
- **Cloud.gov's FedRAMP package** (F1607067912) and all inherited controls remain unchanged.
- **The platform's container runtime**, network security, and isolation guarantees are identical.
- **The authorization boundary** does not change — applications still run within Cloud.gov's FedRAMP-authorized environment.

### Recommended Path
This transition can likely be handled as a **significant change request** rather than a full ATO reassessment, since:
- The authorization boundary is unchanged
- Inherited controls are unaffected
- The deployment method is a supported Cloud.gov capability
- The security posture is demonstrably maintained or improved

---

## 9. Conclusion

Transitioning from buildpacks to Docker containers built on CIS-validated Hardened Images **maintains our security posture** through Cloud.gov's unchanged inherited controls and **strengthens it** through:

- CIS-benchmarked, continuously scanned base images with near-zero CVEs
- SLSA Level 3 supply chain integrity with cryptographic verification
- Complete SBOMs and audit artifacts that buildpacks cannot provide
- Reduced attack surface through distroless image variants
- Immutable, reproducible deployments that eliminate environment drift

The additional responsibility for base image maintenance is fully mitigated by DHI's automated patching, continuous scanning, and (if needed) enterprise SLA-backed remediation.

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
