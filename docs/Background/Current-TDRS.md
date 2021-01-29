OFA's TANF grantees submit data to TDRS that they are [legislatively-mandated](https://www.law.cornell.edu/uscode/text/42/611) to report. OFA then aggregates the data and uses it for descriptive analyses and program accountability, most notably through the work participation rate calculations. Work participation rates measure the degree to which families receiving TANF assistance are engaged in work activities specified under federal law. States, territories, and tribes must meet both an overall work participation rate and a two-parent work participation rate or be subject to a financial penalty.

The existing system was developed in the late 1990s with only minor updates in the past 20 years.
The TANF grantees usually generate their data in one of the following  ways (review [information about the incoming data format](https://www.acf.hhs.gov/ofa/resource/tanfedit/index#transmission-file-header)):
* Using a legacy tool (ftanf.exe) that exports files in a special text format
* Using their own software to export the data
* Emailing their data to an OFA staff member to be entered for them

The data is then uploaded using secure file transfer protocol (SFTP) into a system which then periodically attempts to process the data and import it into the database OFA staff uses for analysis. OFA staff access the data via direct read-only SQL queries using tools like python, Jupyter Notebooks, and SAS.

The database currently is around 50GB in size, though most of it is historical data which will not need to be migrated. Most of the tables contain between 700,000 to 1,300,000 rows and most of the data is stored in seven tables. These tables are renamed periodically so there is a historical record. Access to this data is extremely limited, both because the data is sensitive (contains personally identifiable information or PII) and because managing access to these aging systems is difficult.

We've outlined what we've observed from user research about how data is prepared and submitted in this **[process map](https://app.mural.co/t/officeoffamilyassistance2744/m/gsa6/1593114727729/906879aaeb5467c27f0ae3dfbcf5fcfd9cf8ca89)**, which includes details on:
 * The kinds of data STT can submit
 * Tools STT use to prepare data files (fTANF, extranet, etc)
 * Resources OFA provides to STT on how to prepare and validate their files
 * The kinds of communications sent between OFA and STT
 * The types of reports OFA publishes using this data

# Types of data

## Types of reports

There are two categories of reports that STTs submit to OFA.

**TANF reports** show how STTs use federal funds to provide benefits to individuals.

There are also **SSP-MOE reports**, which stand for Separate State Programs Maintenance of Effort. As a condition of receiving federal TANF funds, states are required to spend a certain amount of their own funds (MOE) on TANF-allowable categories. These reports document how STTs use their own funds for allowable categories.

## Universe vs Sample data
STTs can send either universe or sample data to OFA. The split is about 50/50 among STTs.

Universe data means they send all of their caseload data to OFA when reporting actives and negatives.

Sample data means they send samples of their caseloads for certain data reports.

## Data layouts
TANF and SSP-MOE reports each have [four data layouts](https://www.acf.hhs.gov/ofa/resource/tanfedit/index#transmission-file-header). Which layouts a STT sends depends on if they are submitting sample or universe data.

The layouts between TANF and SSP-MOE are similar, but not identical.

### TANF

#### Section 1 active report
Case-level records on who's getting benefits through TANF
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section1_10_2008.pdf)
* [Tribal TANF transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/tribal_layout_for_section1.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_01_2008_tansec1.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_tansec1.pdf)


#### Section 2 negative report
Case-level records on who stopped getting benefits through TANF
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section2.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_02_2007_tansec2.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_tansec2.pdf)

#### Section 3 aggregate report
In total how many people get and stopped getting benefits through TANF
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section3.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_02_2007_tansec3.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_tansec3.pdf)

#### Section 4 stratum report
If sending sample data, a report on the stratum totals for TANF reporting.
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/tanf_data_report_section4.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_02_2008_tansec4.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_tansec4.pdf)

### SSP-MOE

#### Section 1 active report
Case-level records on who's getting benefits through SSP-MOE
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/ssp_moe_transmission_format_section_1.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_01_2008_sspsec1.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_sspsec1.pdf)

#### Section 2 negative report
Case-level records on who stopped getting benefits through SSP-MOE
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/ssp_moe_transmission_format_section_2.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_02_2007_sspsec2.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_sspsec2.pdf)

#### Section 3 aggregate report
In total how many people get and stopped getting benefits through SSP-MOE
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/ssp_moe_transmission_format_section_3.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_02_2007_sspsec3.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_sspsec3.pdf)

#### Section 4 stratum report
If sending sample data, a report on the stratum totals for SSP-MOE reporting.
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/ofa/ssp_moe_transmission_format_section_4.pdf)
* [Instructions](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_instr_10_01_2008_sspsec4.pdf)
* [Form](https://www.acf.hhs.gov/sites/default/files/ofa/tdrs_form_reports_10_1_2008_sspsec4.pdf)

## Additional resources:
* [Instructions and form templates for all sections](https://www.acf.hhs.gov/ofa/resource/policy/pi-ofa/2008/200809/tanf-acf-pi-2008-07)
* [Legacy screenshots are in the process map](https://app.mural.co/t/officeoffamilyassistance2744/m/gsa6/1593114727729/906879aaeb5467c27f0ae3dfbcf5fcfd9cf8ca89)
* [More about TDRS users](../User-Research/Stakeholders-and-Personas.md)
* [Tribal TANF Data Coding Instructions](https://www.acf.hhs.gov/ofa/resource/tribal-tanf-data-coding-instructions)


