# Searchable Infrastructure Demo Guide

This guide helps you demonstrate the correlation between **Infrastructure Changes** (Terraform) and **Application Performance** (OpenTelemetry) using the Elastic Stack.

## 1. Setup & Pre-requisites

1.  **Start Services**: Ensure all containers are running (`docker-compose up -d`).
2.  **Jenkins Jobs**: Run `Backend-Pipeline` and `Demo-Pipeline` at least once to generate baseline data.
3.  **Kibana**: Open your Elastic Cloud Kibana instance.

## 2. The Chaos Scenario (Instructions)

1.  **Baseline**: Show the app running normally (latency ~0s).
2.  **Inject Fault**:
    *   Go to Jenkins > `Backend-Pipeline` > **Build with Parameters**.
    *   Set `SIMULATED_LATENCY` to `2.0` (2 seconds).
    *   Run the build.
3.  **Observe**:
    *   Wait for the pipeline to finish the `Terraform Apply` stage.
    *   Go to the App frontend and trigger some actions (`/action` endpoint).
    *   They should now be slow.

## 3. Kibana Discovery (Showing the Correlation)

Use the **Discover** app in Kibana to tell the story.

### A. Create a "Unified" Data View
Create a Data View that includes both your application logs/traces and your infrastructure/pipeline logs.
*   **Name**: `Searchable Infra`
*   **Index Pattern**: `logs-*, traces-*, infra-raw-events-*`

### B. The "Root Cause" Filter (KQL)

Paste this query into the search bar to see **Terraform Changes** AND **App Latency** in one view:

```kql
(service.name: "backend-service" AND transaction.duration.us > 1000000) 
OR 
(log.type: "terraform_plan_summary" OR log.type: "terraform_apply")
```

**What this shows:**
*   **High Latency Transactions**: Requests taking > 1s.
*   **Terraform Events**: The exact moment infrastructure was changed.

### C. Visualizing the Story

1.  **Columns**: Add these columns to your Discover grid for clarity:
    *   `@timestamp`
    *   `log.type` (shows `terraform_apply` vs `null`)
    *   `service.name` (shows `backend-service`)
    *   `transaction.duration.us`
    *   `terraform.plan.list` (shows what resource changed! e.g., `[~] docker_container.backend`)

2.  **Timeline**:
    *   Look at the Histogram at the top.
    *   You will see a **bar** for the `terraform_apply` log.
    *   **Immediately after**, you will see a massive spike in `backend-service` duration logs.

### D. Deep Dive into the Change

Expand the `terraform_plan_summary` log document:
*   Look at the `terraform.plan.list` field.
*   It explicitly says: `[~] docker_container.backend`.
*   **Conclusion**: "We can see exactly when the latency started, and looking at the infrastructure log immediately preceding it, we see that the backend container was updated."

## 4. Building the "Searchable Infra" Dashboard

Create a new Dashboard in Kibana and add the following visualizations (using Lens).

### Visualization 1: "Change Heatmap" (Timeline of Changes)
*   **Type**: Bar Chart
*   **Horizontal Axis**: `@timestamp`
*   **Vertical Axis**: Count of Records
*   **Breakdown by**: `log.type`
*   **Filter**: `log.type: terraform_apply OR log.type: terraform_destroy OR log.type: pipeline_failure`
*   **Goal**: Shows "When did deployments happen?"

### Visualization 2: "App Latency" (Correlated line)
*   **Type**: Line Chart
*   **Horizontal Axis**: `@timestamp`
*   **Vertical Axis**: Average `transaction.duration.us`
*   **Breakdown by**: `service.name`
*   **Goal**: Shows performance spikes.
*   **Tip**: Place this directly below Vis #1 to line up the time axes.

### Visualization 3: "Recent Infrastructure Changes" (Detail Table)
*   **Type**: Data Table
*   **Rows**:
    *   `@timestamp`
    *   `service.name`
    *   `terraform.plan.list` (The changed resources)
    *   `vcs.revision` (Git Commit)
    *   `ci.build.url` (Link to Jenkins)
*   **Filter**: `log.type: terraform_plan_summary`
*   **Goal**: Provides the detailed "What changed?" context.

### Visualization 4: "Change Impact Summary"
*   **Type**: Metric
*   **Primary Metric**: Count of `terraform.plan.summary.update`
*   **Secondary Metric**: Count of `terraform.plan.summary.create`
*   **Goal**: Quick stats on how much churn is happening in your infra.

### Dashboard Layout
1.  Top Row: **Change Heatmap** (spanning full width).
2.  Second Row: **App Latency** (spanning full width).
3.  Third Row: **Recent Infrastructure Changes** (Table).
