# Getting Started with Grafana&#x20;

Grafana enables DIGIT to query, visualize, alert on, and explore [metrics, logs, and traces.](#user-content-fn-2) Dashboards are created and managed in Grafana. The purpose of this documentation is to support DIGIT users with onboarding materials so that you can quickly and confidently explore available dashboards, extract insights, and contribute to data-driven processes.

---

## Login

Access Grafana by clicking the link in the top navigation of TANF Data Portal and log in using your assigned username and password.


<img width="599" height="169" alt="Screenshot 2025-08-05 at 12 21 16 PM" src="https://github.com/user-attachments/assets/a5afb86f-839f-47c2-a848-91ee72cad6f5" />

The top navigation menu on TANF Data Portal includes a link to Grafana.

With your access, you can:

* View all available dashboards
* Use filters to customize data views
* Export individual widgets from dashboards
* Run queries to explore data as needed


<img width="1625" height="879" alt="Screenshot 2025-05-30 at 10 19 15 AM" src="https://github.com/user-attachments/assets/5227945c-f90b-46b6-b679-09a6e0bd93bb" />

Login screen for Grafana

If you encounter any issues logging in or accessing certain features, please contact **tanfdata@acf.hhs.gov**.

---

## Dashboards

Each dashboard includes an Overview to describe the purpose and intention.&#x20;

<table><thead><tr><th width="175.05078125">Dashboard</th><th width="256.68359375">Description and Purpose</th><th width="237.15234375">Filters Needed </th><th>Status/Notes</th></tr></thead><tbody><tr><td><a href="https://tdp-frontend-a11y.app.cloud.gov/grafana/d/eemnhxok5dr7kd/b3ed5b3f-cce8-5855-a97c-7e8f7330e003">[DIGIT] Query Views by program type, record type, and time period</a></td><td>Dashboard with pre-set query params (prod)</td><td>program type, record type, and time period</td><td>In progress</td></tr><tr><td><p></p><p><a href="https://tdp-frontend-a11y.app.cloud.gov/grafana/d/fe6fa4dye7s3kf/digit-stts-missing-approved-users">[DIGIT] STTs missing Approved Users</a></p></td><td>List of STTs with no approved users in TDP (prod)</td><td>STT region, STT code, STT</td><td>In progress</td></tr><tr><td><a href="https://tdp-frontend-a11y.app.cloud.gov/grafana/d/ce6f8l7vw36kgd/digit-tdp-submission-history">[DIGIT] TDP Submission History</a></td><td>Production data submission history</td><td>Program_type, Section, Fiscal_Year, Fiscal Quarter, STT Region, STT_Type, STT</td><td>Templating Error Type alert</td></tr></tbody></table>

---

## Set dashboard time range

_Note: Time settings are saved on a per-dashboard basis._

To view the **time range** setting on a dashboard, hover over the time menu located in the top menu.


<img width="1190" height="88" alt="Screenshot 2025-06-23 at 11 04 41 AM" src="https://github.com/user-attachments/assets/f8c51027-130a-4e5b-b4e7-9f2a93096b36" />

The <strong>Time</strong> menu is located at the top of the page, to the right of the <strong>Share</strong> button


<img width="165" height="152" alt="Screenshot 2025-06-25 at 11 09 27 AM" src="https://github.com/user-attachments/assets/0b390fe0-4722-4930-9d14-de7fec638d7f" />

Hovering over the menu displays the current time range setting

DIGIT dashboards reflect the most recent records, so choose a time range within the last 24 hours. To adjust the **time range** on a dashboard, click the time menu to select a relative time range or set custom absolute time ranges.

<img width="548" height="435" alt="Screenshot 2025-06-25 at 11 09 43 AM" src="https://github.com/user-attachments/assets/f9660be1-1c88-4415-b22f-950ea325bedc" />

The time menu provides inputs to set absolute and relative time ranges or select common or recently used time ranges

The **timezone** and **fiscal year** settings can be changed from the **time** menu by clicking the **Change time settings** button.

_Additional information about supported time units and relative ranges can be found in the_ [_Set dashboard time range_](https://grafana.com/docs/grafana/latest/dashboards/use-dashboards/#set-dashboard-time-range) _section of Grafana's documentation site._

---

## Filter dashboard data

#### Query variables

Variables can be used to dynamically change the data displayed on a dashboard. They are displayed as dropdown lists at the top of the dashboard.

<img width="1418" height="141" alt="Screenshot 2025-06-25 at 12 25 03 PM" src="https://github.com/user-attachments/assets/4245f206-f516-415d-aa87-964f7f6b2052" />

Variables are located at the top of the dashboard and appear as dropdown menus

_Advanced documentation about creating and working with variables can be found in the_ [_Variables_](https://grafana.com/docs/grafana/latest/dashboards/variables/) _section of the Grafana documentation site._

---

## Export data to CSV

1. Click the **Menu** in the upper right corner of a panel, and select **Inspect**, then select **Data** (keyboard shortcut i)

<img width="328" height="183" alt="Screenshot 2025-07-22 at 4 14 01 PM" src="https://github.com/user-attachments/assets/de16f3d4-06e2-4e92-b1f6-c0d88fbb01a8" />

Clicking <strong>Inspect</strong> will open a side panel to look at the data, stats, and JSON

2. Click **Data options** to adjust settings, then click **Download CSV**


<img width="620" height="300" alt="Screenshot 2025-07-22 at 4 15 14 PM" src="https://github.com/user-attachments/assets/819ada6d-8506-46e6-87e1-2837e642f82d" />

Clicking <strong>Data options</strong> opens a dropdown to toggle <strong>Formatted data</strong> and <strong>Download for Excel</strong>

---

## Querying  Datasets

_Note: Firefox or Edge browsers are recommended for the best performance when running large queries in Grafana._

You can use the Query inspector to inspect raw data, export data to a CSV file, export log results, and view query requests.

1.  Navigate to the **Explore** page

    _Note: you must have either the `editor` or `administrator` basic role or the `data sources explore`  role to access Explore in Grafana._
2.  Use the query **Builder** UI to create your query, or use the **Code** option to write an SQL query&#x20;

    To switch between methods, use the **Builder** and **Code** buttons in the upper right of the query block

For queries that could potentially return more than 1 million records at a time, it is recommended to filter records by reporting month.&#x20;

<img width="1575" height="543" alt="Screenshot (32)" src="https://github.com/user-attachments/assets/5e70c74d-edd3-4d70-a7ad-3538a72b63f1" />

A warning will occur when the 1 million row limit is reached.

If you receive a Warning that there are more than 20 columns in the query, you can choose to show all columns.

3. Click **Run Query**
4. Query results will be displayed in a table below the query row&#x20;
5. To export the query results, click the **Query inspector** button at the bottom of the query row, then select the **Data** tab
6. [Open the **Data options** section to change the settings as needed, then click the **Download CSV** button](#user-content-fn-3)

<img width="1033" height="588" alt="Screenshot 2025-06-30 at 3 17 48 PM" src="https://github.com/user-attachments/assets/c5a370d6-c908-4622-8026-9269076ff062" />

The <strong>Query inspector</strong> button is below the query row, and opens a panel below with tabs for Stats, Query, JSON, and Data. Select the <strong>Data</strong> tab to download a CSV

---

### Examples of common SQL queries

**Preview data from any table**

To use the **Builder** UI to create a query to preview data from a table:

1. Select the table view to query from the **Table** dropdown \
   Below is a list of table views that are most relevant to your data tasks

<table><thead><tr><th width="223">Table_View</th><th width="230">Description</th></tr></thead><tbody><tr><td>tanf_t1</td><td>T1 records for states and territories</td></tr><tr><td>tanf_t2</td><td>T2 records for states and territories</td></tr><tr><td>tanf_t3</td><td>T3 records for states and territories</td></tr><tr><td>tanf_t4</td><td>T4 records for states and territories</td></tr><tr><td>tanf_t5</td><td>T5 records for states and territories</td></tr><tr><td>tanf_t6</td><td>T6 records for states and territories</td></tr><tr><td>tanf_t7</td><td>T7 records for states and territories</td></tr><tr><td>ssp_m1</td><td>M1 records for states and territories</td></tr><tr><td>ssp_m2</td><td>M2 records for states and territories</td></tr><tr><td>ssp_m3</td><td>M3 records for states and territories</td></tr><tr><td>ssp_m4</td><td>M4 records for states and territories</td></tr><tr><td>ssp_m5</td><td>M5 records for states and territories</td></tr><tr><td>ssp_m6</td><td>M6 records for states and territories</td></tr><tr><td>ssp_m7</td><td>M7 records for states and territories</td></tr><tr><td>tribal_tanf_t1</td><td>T1 records for tribes</td></tr><tr><td>tribal_tanf_t2</td><td>T2 records for tribes</td></tr><tr><td>tribal_tanf_t3</td><td>T3 records for tribes</td></tr><tr><td>tribal_tanf_t4</td><td>T4 records for tribes</td></tr><tr><td>tribal_tanf_t5</td><td>T5 records for tribes</td></tr><tr><td>tribal_tanf_t6</td><td>T6 records for tribes</td></tr><tr><td>tribal_tanf_t7</td><td>T7 records for tribes</td></tr><tr><td>stt_section_to_type_mapping</td><td>metadata for each table view</td></tr><tr><td>mr_record_counts_by_tableview</td><td>most recent record count by table view and stt</td></tr></tbody></table>

1. Select the **Column** (selecting \* means you would like to retrieve all columns)
2. _(Optional)_ Ensure the **Order** toggle is selected to limit results


<img width="1101" height="564" alt="Screenshot 2025-06-30 at 2 00 16 PM" src="https://github.com/user-attachments/assets/5c18f601-38a8-43a2-aa0e-a74c7b6b1eae" />

An example of using the <strong>Builder</strong> UI to preview data from a table

The same query can be written in SQL and run in the **Code** view

```
SELECT *    -- select all columns/fields
FROM ssp_m1 -- ssp, active m1 (family-level) records
LIMIT 100;  -- limit results to 100 records
```

---

### **Aggregate counts: total records vs. unique cases**

To build a query that compares the total number of records versus unique cases:

1. Select the "tanf\_t1" table to query from the **Table** dropdown
2. Select \* in the **Column** dropdown (selecting \* means you would like to retrieve all columns), select the Aggregation method **Count**, and input an Alias of "total\_records" to label the query results column
3. Click the **+** to add another column to the query
4.  Select the "CASE\_NUMBER" column to query, select the Aggregation method **Count**, and input an Alias of "unique\_cases" to label the second column of query results column

    _Note: The Builder UI does not provide a way to remove duplicate rows from the result set using the_ DISTINCT _keyword; if this action is desired, using the Code method to input your query will provide more flexibility_
5. Click the **Run query** button


<img width="1108" height="587" alt="Screenshot 2025-06-30 at 2 30 23 PM" src="https://github.com/user-attachments/assets/f3230490-09a9-4cad-833f-23d9463d08d6" />

An example of using the <strong>Builder</strong> UI to aggregate data to compare total records versus unique cases

The same query can be written in SQL and run in the **Code** view:

```
SELECT 
    COUNT(*) AS total_records,
    COUNT(DISTINCT "CASE_NUMBER") AS unique_cases
FROM tanf_t1;-- TANF, active t1 (family-level) records
```

---

### **Grouped counts: total records by month and STT**

1. Select the tanf\_t16 table to query from the **Table** dropdown
2. Select "STT" as the first **Column**
3. Click the **+** to add another column to the query, and select "RPT\_MONTH\_YEAR"
4. Click the **+** to add another column to the query, and select \*, set the Aggregation to COUNT
5. Ensure the **Group**, and **Order** toggles are switch on
6. Select "STT" in the Group by column dropdown
7. Click the **+** to add another group by column attribute, and select "RPT\_MONTH\_YEAR"
8.  In the Order by dropdown, select "STT"; (optional) click to sort by ascending or descending &#x20;

    _Note: The Builder UI limits ordering to one attribute, if multiple ordering attributes are desired, the Code option will provide more flexibility_
9. Click the **Run query** button


<img width="889" height="622" alt="Screenshot 2025-06-30 at 4 15 05 PM" src="https://github.com/user-attachments/assets/9f89b3b1-e429-4207-b588-56d5b39eaee5" />

An example of using the <strong>Builder</strong> UI to group data by column and order by data type

The same query can be written in SQL and run in the **Code** view:

```
SELECT 
    "STT", -- State or territory 
    "RPT_MONTH_YEAR",     -- Reporting month (e.g., 202401, 202402)             
    COUNT(*) AS total_records
FROM tanf_t6 -- TANF,  t6 (aggregate-level) records
GROUP BY  "STT","RPT_MONTH_YEAR"
ORDER BY "STT","RPT_MONTH_YEAR";
```

_Advanced documentation about ways to explore data in Grafana is available in the_ [_Explore_](https://grafana.com/docs/grafana/latest/explore/get-started-with-explore/#get-started-with-explore) _section of the Grafana documentation site._
