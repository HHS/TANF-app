# Real User Monitoring (RUM) Implementation

This document describes the Real User Monitoring (RUM) implementation for the TANF Data Portal frontend application using Grafana Faro SDK.

## Overview

The RUM implementation tracks user sessions, page view times, navigation changes, and application errors. The collected data is sent to Grafana for visualization and analysis.

## Components

### 1. RUM Service (`src/services/RumService.js`)

Centralized service that initializes and configures the Grafana Faro SDK. It provides:

- Automatic collection of web vitals (LCP, FID, CLS)
- Session tracking
- Error tracking
- Helper methods for manual instrumentation

### 2. Route Tracker (`src/components/RouteTracker/index.js`)

Tracks page views and navigation events. Integrated into the main application component to monitor all route changes.

### 3. Redux Middleware (`src/middleware/rumMiddleware.js`)

Monitors Redux actions and state changes, providing insights into application behavior and performance.

### 4. Error Boundary (`src/components/ErrorBoundary/index.js`)

Catches and reports unhandled errors in the React component tree.

## Configuration

The RUM implementation can be configured using environment variables:

- `REACT_APP_ENABLE_RUM`: Set to `true` to enable RUM in development environments (enabled by default in production)
- `REACT_APP_FARO_ENDPOINT`: The Grafana Faro collector endpoint URL
- `REACT_APP_VERSION`: Application version for tracking

## Grafana Integration

To visualize the collected data in Grafana:

1. Set up a Grafana instance or use Grafana Cloud
2. Configure the Faro data source
3. Create dashboards for:
   - User experience metrics (page load times, navigation patterns)
   - Error tracking and analysis
   - Redux action performance
   - Session analytics

## Sample Dashboards

### User Experience Dashboard

- Page load time by route
- Navigation flow visualization
- Core Web Vitals metrics
- Session duration distribution

### Error Dashboard

- Error rate by page/component
- Error types and frequency
- Error impact on user sessions

### Redux Performance Dashboard

- Action execution time
- Action frequency
- State change patterns

## Privacy Considerations

The RUM implementation follows these privacy guidelines:

- No personally identifiable information (PII) is collected
- User actions are tracked anonymously
- Sensitive data in Redux actions is filtered out
- Compliance with relevant privacy regulations

## Future Enhancements

- Custom event tracking for specific user interactions
- Performance budget monitoring
- A/B testing integration
- User journey analysis
