# Clean and Re-parse DataFiles

## Background
As TDP has evolved so has it's validation mechanisms, messages, and expansiveness. As such, many of the datafiles locked in the database and S3
have not undergone TDP's latest and most stringent validation processes. Because data quality is so important to all TDP stakeholders
we wanted to introduce a way to re-parse and subsequently re-validate datafiles that have already been submitted to TDP to enhance the integrity
and the quality of the submissions. The following lays out the process TDP takes to automate and execute this process, and how this process can
be tested locally and in our deployed environments.

## Clean and Re-parse Flow
As a safety measure, this process must ALWAYS be executed manually by a system administrator. Once executed, all processes thereafter are completely
automated. The steps below outline how this process executes.

1. System admin logs in to the appropriate backend application. E.g. `tdp-backend-raft`.
2. System admin executes the `clean_and_reparse` Django command. E.g `python manage.py clean_and_reparse ...options`.
4. System admin validates the command is selecting the appropriate set of datafiles to reparse and executes the command.
4. `clean_and_reparse` collects the appropriate datafiles that match the system admin's command choices.
5. `clean_and_reparse` executes a backup of the Postgres database.
6. `clean_and_reparse` creates/deletes appropriate Elastic indices pending the system admin's command choices.
7. `clean_and_reparse` deletes documents from appropriate Elastic indices pending the system admin's command choices.
8. `clean_and_reparse` deletes all Postgres rows associated to all selected datafiles.
9. `clean_and_reparse` deletes `DataFileSummary` and `ParserError` objects associated with the selected datafiles.
10. `clean_and_reparse` re-saves the selected datafiles to the database.
11. `clean_and_reparse` pushes a new `parser_task` onto the Redis queue for each of the selected datafiles.

## Local Clean and Re-parse
Make sure you have submitted a few datafiles, ideally accross program types and fiscal timeframes.

1. Browse the [indices](http://localhost:9200/_cat/indices/?pretty&v&s=index) and the DAC and verify the indices reflect the document counts you expect and the DAC reflects the record counts you expect.
2. Exec into the backend container.
3. Execute `python manage.py clean_and_reparse -h` to get an idea of what options you might want to specify.
4. Execute the `clean_and_reparse` command with your selected options.
5. Verify in the above URL that Elastic is consistent with the options you selected.
6. Verify the DAC has the same amount of records as in step 1.

### Local Examples
This section assumes that you have submitted the following files: `ADS.E2J.FTP1.TS06`, `cat_4_edge_case.txt`, and `small_ssp_section1.txt`. After submitting, your indices should match the indices below:
```
health status index                   uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1               VKeA-BPcSQmJJl_AbZr8gQ   1   0          1            0      4.9kb          4.9kb
yellow open   dev_ssp_m1_submissions  mDIiQxJrRdq0z7W9H_QUYg   1   1          5            0       24kb           24kb
yellow open   dev_ssp_m2_submissions  OUrgAN1XRKOJgJHwr4xm7w   1   1          6            0     33.6kb         33.6kb
yellow open   dev_ssp_m3_submissions  60fCBXHGTMK31MyWw4t2gQ   1   1          8            0     32.4kb         32.4kb
yellow open   dev_tanf_t1_submissions 19f_lawWQKSeuwejo2Qgvw   1   1        817            0    288.2kb        288.2kb
yellow open   dev_tanf_t2_submissions dPj2BdNtSJyAxCqnMaV2aw   1   1        884            0    414.4kb        414.4kb
yellow open   dev_tanf_t3_submissions e7bEl0AURPmcZ5kiFwclcA   1   1       1380            0    355.2kb        355.2kb
```
All tests are considered to have been run INDEPENDENTLY. For each test, your Elastic and DAC state should match the initial conditions above. The commands in the section below should be run in between each test if you want to match the expected output.

#### Some Useful Commands to Reset Elastic State
The commands should ALWAYS be executed in the order they appear below.
1. curl -X DELETE 'http://localhost:9200/dev*'
2. python manage.py search_index --rebuild

#### Clean and Re-parse All with New Indices and Keeping Old Indices
1. Execute `python manage.py clean_and_reparse -a -n`
    - If this is the first time you're executing a command with new indices, because we have to create an alias in Elastic with the same name as the
    original index i.e. (`dev_tanf_t1_submissions`), the old indices no matter whether you specified `-d` or not will be deleted. From thereafter,
    the command will always respect the `-d` switch.
2. Expected Elastic results.
    - If this is the first time you have ran the command the [indices](http://localhost:9200/_cat/indices/?pretty&v&s=index) url should reflect 21 indices prefixed with `dev` and they should contain the same number of documents as the original indices did. The new indices will also have a datetime suffix indicating when the re-parse occurred.
    - If this is the second time running this command the [indices](http://localhost:9200/_cat/indices/?pretty&v&s=index) url should reflect 42 indices prefixed with `dev` and they should each contain the same number of documents as the original indices did. The latest indices will have a new datetime suffix delineating them from the other indices.
3. Expected DAC results.
    - The DAC record counts should be exactly the same no matter how many times the command is run.
    - The primary key for all reparsed datafiles should no longer be the same.
    - `ParserError` and `DataFileSummary` objects should be consistent with the file.

- First run:
```
health status index                                              uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1                                          VKeA-BPcSQmJJl_AbZr8gQ   1   0          2            0      8.9kb          8.9kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.19.04         MaU2tuZbS0Cnr_xnsnZFeg   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.19.04         y3-XdOxTQhiFJ418R8vLyQ   1   0          6            0     28.5kb         28.5kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.19.04         oGv9YqqVQTusDTVhdOp8QQ   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m4_submissions_2024-07-05_17.19.04         zfB8iEjbSVu_PV1OC96RPA   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.19.04         5vvT2bwSSs-p1qqXuDCdgw   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.19.04         jLiBUnsnQhWk-6fodCG8nw   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.19.04         sP96nbMYTfOo_idi6crukA   1   0          0            0       208b           208b
green  open   dev_tanf_t1_submissions_2024-07-05_17.19.04        grF44EQbSZO3Gd5MOIx1sw   1   0        817            0      259kb          259kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.19.04        rCXW-xARQsidOO2At6K8Ag   1   0        884            0    302.9kb        302.9kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.19.04        -FdmCStMQcSbj05MQFx-Aw   1   0       1380            0      284kb          284kb
green  open   dev_tanf_t4_submissions_2024-07-05_17.19.04        cERybc1CRNeJWvUPA_Mfug   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.19.04        dsG23wOJR5GzCbw9g6NaTQ   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.19.04        2qLii1GmSSCeKaRpaW1vWA   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.19.04        emROGjIfQti7F4XL_lyBhA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.19.04 W-Z98uOzSI2ayP6E8PFUGg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.19.04 2hgjlY4eRI2jocJkZLF_rQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.19.04 3xy9iWisRZWnsm4qqj6Fow   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.19.04 6weq13MQTymTH0yaB3SJXA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.19.04 DzpKU2zpTLO8UUYOubnzjA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.19.04 CiEiyGGBQXa-pUnGwvEM9g   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.19.04 3NFTCxRHTDWfbLkCSbVyRw   1   0          0            0       208b           208b
```

- Second run:
```
health status index                                              uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1                                          VKeA-BPcSQmJJl_AbZr8gQ   1   0          2            0      9.1kb          9.1kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.19.04         MaU2tuZbS0Cnr_xnsnZFeg   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.20.50         bhwRrxqlS7yMACaryZooUg   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.19.04         y3-XdOxTQhiFJ418R8vLyQ   1   0          6            0     28.5kb         28.5kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.20.50         EuQWp0T6T2OHNvFTwsIVNg   1   0          6            0     28.6kb         28.6kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.19.04         oGv9YqqVQTusDTVhdOp8QQ   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.20.50         QMlwSBjGSQWeBVTy_X1cEw   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m4_submissions_2024-07-05_17.19.04         zfB8iEjbSVu_PV1OC96RPA   1   0          0            0       208b           208b
green  open   dev_ssp_m4_submissions_2024-07-05_17.20.50         U_UNdlOHSmCCLRLNBUBQew   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.19.04         5vvT2bwSSs-p1qqXuDCdgw   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.20.50         2XGFMJqrRyy4gDOpgzla8A   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.19.04         jLiBUnsnQhWk-6fodCG8nw   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.20.50         oOF-YfZsSOOGqOw7WwaeEg   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.19.04         sP96nbMYTfOo_idi6crukA   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.20.50         CWJAk6poRO-0kDe4GFnlHg   1   0          0            0       208b           208b
green  open   dev_tanf_t1_submissions_2024-07-05_17.19.04        grF44EQbSZO3Gd5MOIx1sw   1   0        817            0      259kb          259kb
green  open   dev_tanf_t1_submissions_2024-07-05_17.20.50        x-IZvFY9TnWsu2zKIz4nLg   1   0        817            0    259.1kb        259.1kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.19.04        rCXW-xARQsidOO2At6K8Ag   1   0        884            0    302.9kb        302.9kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.20.50        5W6ks0ULRruCYTR3d4TFcw   1   0        884            0    302.8kb        302.8kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.19.04        -FdmCStMQcSbj05MQFx-Aw   1   0       1380            0      284kb          284kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.20.50        oN3mankySa-OJytsgqmk3w   1   0       1380            0    283.9kb        283.9kb
green  open   dev_tanf_t4_submissions_2024-07-05_17.19.04        cERybc1CRNeJWvUPA_Mfug   1   0          0            0       208b           208b
green  open   dev_tanf_t4_submissions_2024-07-05_17.20.50        M5JsTQpXTkS3Tm8aezhWEQ   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.19.04        dsG23wOJR5GzCbw9g6NaTQ   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.20.50        kW-qa72tTDGZqaFSiapWSw   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.19.04        2qLii1GmSSCeKaRpaW1vWA   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.20.50        Q-bM4s2ASSuC7r3WUN7vbA   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.19.04        emROGjIfQti7F4XL_lyBhA   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.20.50        3xDn6L4VTsOWCLXHXUfz9g   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.19.04 W-Z98uOzSI2ayP6E8PFUGg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.20.50 kEunfM4jTLeWdU6v8HhUXg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.19.04 2hgjlY4eRI2jocJkZLF_rQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.20.50 oW1JmR24QkW97F7EtFvFQg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.19.04 3xy9iWisRZWnsm4qqj6Fow   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.20.50 X1oAYhWuTmKnVOOIkVC5Lg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.19.04 6weq13MQTymTH0yaB3SJXA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.20.50 BCQ4LbkSTOOr282JksXnDA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.19.04 DzpKU2zpTLO8UUYOubnzjA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.20.50 cEV3dTw9SJCGx9sPp6AU6Q   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.19.04 CiEiyGGBQXa-pUnGwvEM9g   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.20.50 QCNiUdxMTZ-0MRZBKom62w   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.19.04 3NFTCxRHTDWfbLkCSbVyRw   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.20.50 ENvlUUWvRo6ulQOTS2l9Tw   1   0          0            0       208b           208b
```

#### Clean and Re-parse All with New Indices and Deleting Old Indices
1. Execute `python manage.py clean_and_reparse -a -n -d`
2. The expected results for this command will be exactly the same as above. The only difference is that no matter how many times you execute this command, you should only see 21 indices in Elastic with the `dev` prefix.

```
health status index                                              uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1                                          VKeA-BPcSQmJJl_AbZr8gQ   1   0          2            0      8.9kb          8.9kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.19.04         MaU2tuZbS0Cnr_xnsnZFeg   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.19.04         y3-XdOxTQhiFJ418R8vLyQ   1   0          6            0     28.5kb         28.5kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.19.04         oGv9YqqVQTusDTVhdOp8QQ   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m4_submissions_2024-07-05_17.19.04         zfB8iEjbSVu_PV1OC96RPA   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.19.04         5vvT2bwSSs-p1qqXuDCdgw   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.19.04         jLiBUnsnQhWk-6fodCG8nw   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.19.04         sP96nbMYTfOo_idi6crukA   1   0          0            0       208b           208b
green  open   dev_tanf_t1_submissions_2024-07-05_17.19.04        grF44EQbSZO3Gd5MOIx1sw   1   0        817            0      259kb          259kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.19.04        rCXW-xARQsidOO2At6K8Ag   1   0        884            0    302.9kb        302.9kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.19.04        -FdmCStMQcSbj05MQFx-Aw   1   0       1380            0      284kb          284kb
green  open   dev_tanf_t4_submissions_2024-07-05_17.19.04        cERybc1CRNeJWvUPA_Mfug   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.19.04        dsG23wOJR5GzCbw9g6NaTQ   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.19.04        2qLii1GmSSCeKaRpaW1vWA   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.19.04        emROGjIfQti7F4XL_lyBhA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.19.04 W-Z98uOzSI2ayP6E8PFUGg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.19.04 2hgjlY4eRI2jocJkZLF_rQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.19.04 3xy9iWisRZWnsm4qqj6Fow   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.19.04 6weq13MQTymTH0yaB3SJXA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.19.04 DzpKU2zpTLO8UUYOubnzjA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.19.04 CiEiyGGBQXa-pUnGwvEM9g   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.19.04 3NFTCxRHTDWfbLkCSbVyRw   1   0          0            0       208b           208b
```

#### Clean and Re-parse All with Same Indices
1. Execute `python manage.py clean_and_reparse -a`
2. The expected results for this command will match the initial result from above.

```
health status index                   uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1               VKeA-BPcSQmJJl_AbZr8gQ   1   0          1            0      4.9kb          4.9kb
yellow open   dev_ssp_m1_submissions  mDIiQxJrRdq0z7W9H_QUYg   1   1          5            0       24kb           24kb
yellow open   dev_ssp_m2_submissions  OUrgAN1XRKOJgJHwr4xm7w   1   1          6            0     33.6kb         33.6kb
yellow open   dev_ssp_m3_submissions  60fCBXHGTMK31MyWw4t2gQ   1   1          8            0     32.4kb         32.4kb
yellow open   dev_tanf_t1_submissions 19f_lawWQKSeuwejo2Qgvw   1   1        817            0    288.2kb        288.2kb
yellow open   dev_tanf_t2_submissions dPj2BdNtSJyAxCqnMaV2aw   1   1        884            0    414.4kb        414.4kb
yellow open   dev_tanf_t3_submissions e7bEl0AURPmcZ5kiFwclcA   1   1       1380            0    355.2kb        355.2kb
```

#### Clean and Re-parse FY 2024 New Indices and Keep Old Indices
1. Execute `python manage.py clean_and_reparse -y 2024 -n`
2. The expected results here are much different with respect to Elastic. Again, Postgres is the ground truth and it's counts should never change. Because this is the first time we execute this command and therfore are creating our Elastic aliases the result returned from the [indices](http://localhost:9200/_cat/indices/?pretty&v&s=index) url might be confusing. See below.

```
health status index                                              uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1                                          VKeA-BPcSQmJJl_AbZr8gQ   1   0          2            0      9.1kb          9.1kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.26.26         SAQJYr6dQsOWCbpAFjGHRg   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.26.26         Bq4D6YUKQW-pNyzdbYJROA   1   0          6            0     28.5kb         28.5kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.26.26         6DIWCtYkSOSkjPpEnUEgow   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m4_submissions_2024-07-05_17.26.26         A9OcMj27RmGBdLHIj9ugaA   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.26.26         fh0ItaqIT4-xQqBVLI6vFg   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.26.26         Q_1-HXQYQ8-UsI15Qxzg5A   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.26.26         CBNpxpgSS7agzFVg4YV8Wg   1   0          0            0       208b           208b
green  open   dev_tanf_t1_submissions_2024-07-05_17.26.26        NRsIsXZbRMaZG7rERONtyA   1   0          2            0     17.6kb         17.6kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.26.26        tK8_BCgIR2iogOn4y9GLzA   1   0          2            0     16.9kb         16.9kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.26.26        MEpnURPnTwqItuQXEtc6sg   1   0          4            0     21.4kb         21.4kb
green  open   dev_tanf_t4_submissions_2024-07-05_17.26.26        JLUCat_MQOG73lJyJ8SLcg   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.26.26        RI69-6F7QBKHMJ1LpXuyxA   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.26.26        r5FoR6QyTe-UXLC6tjvbbA   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.26.26        O8TxCKVHRJ66R7CD8k06OQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.26.26 t_PQyvFfTLCLYWKDVQfcYQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.26.26 CDRXMuEzRmuLJ7vutTq2dA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.26.26 RDVORzDnQs6t6q6Huhr2YQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.26.26 oG-FtyMJSJKgAu-15476zg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.26.26 ABt7eBV_SbSYFm0wFxNoBA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.26.26 pKIIW7h8SXGwFwwJoiEwNA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.26.26 crc6cuIHQfmxIUtY38Jrzw   1   0          0            0       208b           208b
```

- While the DAC reports the correct number of records for all submitted types, Elastic does not. This is because we only reparsed a subset of the entire collection of datafiles for the first time we executed the `clean_and_reparse` command. Therefore, Elastic only has documents for the subset of resubmitted files. If we had already executed the command: `python manage.py clean_and_reparse -a -n` and then executed `python manage.py clean_and_reparse -y 2024 -n`, we would see what you might have initially expected to see.

```
health status index                                              uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   .kibana_1                                          VKeA-BPcSQmJJl_AbZr8gQ   1   0          2            0      9.1kb          9.1kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.34.34         -85xFrpTRE-HM976xagEEw   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m1_submissions_2024-07-05_17.35.26         801ZSKT4QfmWsEfs4IJzZQ   1   0          5            0     19.7kb         19.7kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.34.34         MU-_ykxBTWC-ACIyv9KMzg   1   0          6            0     28.5kb         28.5kb
green  open   dev_ssp_m2_submissions_2024-07-05_17.35.26         yoLP5BO0SHakA5xK6rATSg   1   0          6            0     28.6kb         28.6kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.34.34         -H31JvnISjW9CfR3PZgYNA   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m3_submissions_2024-07-05_17.35.26         IDL_o-UhTCujQRYCnFdoRg   1   0          8            0     24.4kb         24.4kb
green  open   dev_ssp_m4_submissions_2024-07-05_17.34.34         vMBtI4zuQDab_ddh8Qnohw   1   0          0            0       208b           208b
green  open   dev_ssp_m4_submissions_2024-07-05_17.35.26         5p5QNgYjRvuGT-Q_2MOIiQ   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.34.34         6RKRT8rRSt2WzbbhymzcyA   1   0          0            0       208b           208b
green  open   dev_ssp_m5_submissions_2024-07-05_17.35.26         K2ggq99MTpeqwpRgoHtHmg   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.34.34         TsXMcw0nS3m5iY-ED5QWxg   1   0          0            0       208b           208b
green  open   dev_ssp_m6_submissions_2024-07-05_17.35.26         U2d4dHgvSNSVIt35pSRisw   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.34.34         3Nnu9-FCSq-QzOFB1CGWPg   1   0          0            0       208b           208b
green  open   dev_ssp_m7_submissions_2024-07-05_17.35.26         7YFpOJTARkC57MKX4t8yBQ   1   0          0            0       208b           208b
green  open   dev_tanf_t1_submissions_2024-07-05_17.34.34        ZW50-uEFT4qCd4Vhih6ctw   1   0        817            0    259.1kb        259.1kb
green  open   dev_tanf_t1_submissions_2024-07-05_17.35.26        i-gwSg4CQDeb4qZX5k0-lQ   1   0          2            0     17.6kb         17.6kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.34.34        2euBGxoERx-WqCbeAcEZSA   1   0        884            0      303kb          303kb
green  open   dev_tanf_t2_submissions_2024-07-05_17.35.26        IIRKApfoQomA2lD3UPnc2A   1   0          2            0     16.9kb         16.9kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.34.34        Cg1hx5tZQoOCG0rvhn-EXw   1   0       1380            0      284kb          284kb
green  open   dev_tanf_t3_submissions_2024-07-05_17.35.26        Dh_Jp8pqTjqANH16f-MBow   1   0          4            0     21.4kb         21.4kb
green  open   dev_tanf_t4_submissions_2024-07-05_17.34.34        f98ktG4SSfqg158IV-M7sQ   1   0          0            0       208b           208b
green  open   dev_tanf_t4_submissions_2024-07-05_17.35.26        k57-clsKR9SmJC3uCiRV-g   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.34.34        AlFw3nSPQ2i8rKr8O90u4Q   1   0          0            0       208b           208b
green  open   dev_tanf_t5_submissions_2024-07-05_17.35.26        7dMKfk0HQZChObZJJ_QOAQ   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.34.34        4z_lm1AoSVuANRw6t-0rdA   1   0          0            0       208b           208b
green  open   dev_tanf_t6_submissions_2024-07-05_17.35.26        vZgIsisvQNmyYnoYGO3FZA   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.34.34        I8hUgOrpRZOo17PQfXCMvg   1   0          0            0       208b           208b
green  open   dev_tanf_t7_submissions_2024-07-05_17.35.26        eBzAC2_8TuWKEXV3dVHqkg   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.34.34 Ow-PJ5EFTlKxr_i_mIEDNQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t1_submissions_2024-07-05_17.35.26 dVl9JE3nRb-b13e2c3F2tQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.34.34 tBzS6osATCalmzeTQSjYvw   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t2_submissions_2024-07-05_17.35.26 8eWs8ifQTwWDLWIeVGgqFA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.34.34 j-tXfoSFT2azhxFCWCJUyA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t3_submissions_2024-07-05_17.35.26 Vcqg36L9S36gW_ABmwPQZQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.34.34 Z-PGJ49WT0CigQnOM27EWQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t4_submissions_2024-07-05_17.35.26 3UtjGJT2Q2KHMzlCKCZc9Q   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.34.34 2cXdkzeMQSmLwGh-ZzroLw   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t5_submissions_2024-07-05_17.35.26 _U-iMH9tTX6Pa5HlFdy_GA   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.34.34 cUU4FrwaT6i4m1B_0l6emw   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t6_submissions_2024-07-05_17.35.26 89TlmOLSScaneSKS5PX2ZQ   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.34.34 9g7k4xQPQ_OQ5WBTmxMB-w   1   0          0            0       208b           208b
green  open   dev_tribal_tanf_t7_submissions_2024-07-05_17.35.26 zXmOuWelRWGF0oZy-DLK3w   1   0          0            0       208b           208b
```

### Cloud.gov Examples
Running the `clean_and_reparse` command in a Cloud.gov environment will require the executor to do some exploratory data analysis for the environment to verify things are running correctly. With that said, the logic and general expected results for the local example commands above will be a one to one match with same command executed in Cloud.gov. Below are the general steps a system admin will follow to execute a desired command and also verify the results of the command.

1. System admin logs in to the appropriate backend application. E.g. `tdp-backend-raft`.
2. System admin has the DAC open and verifies the counts of records, and other models before executing command.
3. System admin logs into the environments Elastic proxy. E.g. `cf ssh tdp-elastic-proxy-dev`.
4. System admin queries the indices for their counts from the Elastic proxy: `curl http://localhost:8080/_cat/indices/?pretty&v&s=index`
5. System admin executes the `clean_and_reparse` Django command from the backend app. E.g `python manage.py clean_and_reparse -a -n`.
6. System admin verifies the DAC is consistent and the Elastic indices match their expectations.
