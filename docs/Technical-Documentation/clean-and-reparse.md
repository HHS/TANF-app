# Clean and Re-parse DataFiles

## Background
As TDP has evolved so has it's validation mechanisms, messages, and expansiveness. As such, many of the datafiles locked in the database and S3
have not undergone TDP's latest and most stringent validation processes. Because data quality is so important to all TDP stakeholders
we wanted to introduce a way to re-parse and subsequently re-validate datafiles that have already been submitted to TDP to enhance the integrity
and the quality of the submissions. The following lays out the process TDP takes to automate and execute this process, and how this process can
be tested locally and in our deployed environments.

# Clean and Re-parse Flow
As a safety measure, this process must ALWAYS be executed manually by a system administrator. Once executed, all processes thereafter are completely
automated. The steps below outline how this process executes.

1. System admin logs in to the appropriate backend application. E.g. `tdp-backend-raft`.
    - See [OFA Admin Backend App Login](#OFA-Admin-Backend-App-Login) instructions below
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
index                   docs.count
.kibana_1                        1
dev_ssp_m1_submissions           5
dev_ssp_m2_submissions           6
dev_ssp_m3_submissions           8
dev_tanf_t1_submissions        817
dev_tanf_t2_submissions        884
dev_tanf_t3_submissions       1380
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

#### Clean and Re-parse All with New Indices and Deleting Old Indices
1. Execute `python manage.py clean_and_reparse -a -n -d`
2. The expected results for this command will be exactly the same as above. The only difference is that no matter how many times you execute this command, you should only see 21 indices in Elastic with the `dev` prefix.

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
index                                       docs.count
.kibana_1                                            2
dev_ssp_m1_submissions_2024-07-05_17.26.26           5
dev_ssp_m2_submissions_2024-07-05_17.26.26           6
dev_ssp_m3_submissions_2024-07-05_17.26.26           8
dev_tanf_t1_submissions_2024-07-05_17.26.26          2
dev_tanf_t2_submissions_2024-07-05_17.26.26          2
dev_tanf_t3_submissions_2024-07-05_17.26.26          4
```

- While the DAC reports the correct number of records for all submitted types, Elastic does not. This is because we only reparsed a subset of the entire collection of datafiles for the first time we executed the `clean_and_reparse` command. Therefore, Elastic only has documents for the subset of resubmitted files. If we had already executed the command: `python manage.py clean_and_reparse -a -n` and then executed `python manage.py clean_and_reparse -y 2024 -n`, we would see what you might have initially expected to see.

```
index                                       docs.count
.kibana_1                                            2
dev_ssp_m1_submissions_2024-07-05_17.34.34           5
dev_ssp_m1_submissions_2024-07-05_17.35.26           5
dev_ssp_m2_submissions_2024-07-05_17.34.34           6
dev_ssp_m2_submissions_2024-07-05_17.35.26           6
dev_ssp_m3_submissions_2024-07-05_17.34.34           8
dev_ssp_m3_submissions_2024-07-05_17.35.26           8
dev_tanf_t1_submissions_2024-07-05_17.34.34        817
dev_tanf_t1_submissions_2024-07-05_17.35.26          2
dev_tanf_t2_submissions_2024-07-05_17.34.34        884
dev_tanf_t2_submissions_2024-07-05_17.35.26          2
dev_tanf_t3_submissions_2024-07-05_17.34.34       1380
dev_tanf_t3_submissions_2024-07-05_17.35.26          4
```

## Cloud.gov Examples
Running the `clean_and_reparse` command in a Cloud.gov environment will require the executor to do some exploratory data analysis for the environment to verify things are running correctly. With that said, the logic and general expected results for the local example commands above will be a one to one match with same command executed in Cloud.gov. Below are the general steps a system admin will follow to execute a desired command and also verify the results of the command.

1. System admin logs in to the appropriate backend application. E.g. `tdp-backend-raft`.
2. System admin has the DAC open and verifies the counts of records, and other models before executing command.
3. System admin logs into the environments Elastic proxy. E.g. `cf ssh tdp-elastic-proxy-dev`.
4. System admin queries the indices for their counts from the Elastic proxy: `curl http://localhost:8080/_cat/indices/?pretty&v&s=index`
5. System admin executes the `clean_and_reparse` Django command from the backend app. E.g `python manage.py clean_and_reparse -a -n`.
6. System admin verifies the DAC is consistent and the Elastic indices match their expectations.

## OFA Admin Backend App Login

### 0. Disconnect from VPN. 

### 1. Authenticate with Cloud.gov
API endpoint: api.fr.cloud.gov
```bash
$ cf login -a api.fr.cloud.gov  --sso

Temporary Authentication Code ( Get one at https://login.fr.cloud.gov/passcode ): <one-time passcode redacted>

Authenticating...
OK


Select an org:
1. hhs-acf-ofa
2. sandbox-hhs

Org (enter to skip): 1
1
Targeted org hhs-acf-ofa.

Select a space:
1. tanf-dev
2. tanf-prod
3. tanf-staging

Space (enter to skip): 1
1
Targeted space tanf-dev.

API endpoint:   https://api.fr.cloud.gov
API version:    3.170.0
user:           <USER_NAME>
org:            hhs-acf-ofa
space:          tanf-dev
```

### 2. SSH into Backend App
1. Get the app GUID
    ```bash
    $ cf curl v3/apps/$(cf app tdp-backend-qasp --guid)/processes | jq --raw-output '.resources | .[]? | select(.type == "web").guid'
    
    <PROCESS_GUID redacted>
    ```

2. Get the SSH code
    ```bash
    $ cf ssh-code

    <SSH_CODE redacted>
    ```

3. SSH into the App
    ```bash
    $ ssh -p 2222 cf:<PROCESS_GUID redacted>/0@ssh.fr.cloud.gov

    The authenticity of host '[ssh.fr.cloud.gov]:2222 ([2620:108:d00f::fcd:e8d8]:2222)' can't be established.
    RSA key fingerprint is <KEY redacted>.
    This key is not known by any other names
    Please type 'yes', 'no' or the fingerprint: yes
    Could not create directory '/u/.ssh' (No such file or directory).
    Failed to add the host to the list of known hosts (/u/.ssh/known_hosts).
    cf:<PROCESS_GUID redacted>/0@ssh.fr.cloud.gov's password:<SSH_CODE - will be invisible>
    ```

### 3. Activate Interactive Shell
```bash
$ /tmp/lifecycle/shell
```

### 4. Display Help for Re-parse Command
```bash
$ python manage.py clean_and_reparse -h

usage: manage.py clean_and_parse [-h] [-q {Q1,Q2,Q3,Q4}] [-y FISCAL_YEAR] [-a] [-n] [-d] [--configuration CONFIGURATION] [--version] [-v {0,1,2,3}] [--settings SETTINGS] [--pythonpath PYTHONPATH] [--traceback] [--no-color] [--force-color] [--skip-checks]

Delete and re-parse a set of datafiles. All re-parsed data will be moved into a new set of Elastic indexes.

options:
  -h, --help            show this help message and exit
  -q {Q1,Q2,Q3,Q4}, --fiscal_quarter {Q1,Q2,Q3,Q4}
                        Re-parse all files in the fiscal quarter, e.g. Q1.
  -y FISCAL_YEAR, --fiscal_year FISCAL_YEAR
                        Re-parse all files in the fiscal year, e.g. 2021.
  -a, --all             Clean and re-parse all datafiles. If selected, fiscal_year/quarter aren't necessary.
  -n, --new_indices     Move re-parsed data to new Elastic indices.
  -d, --delete_indices  Requires new_indices. Delete the current Elastic indices.
  --configuration CONFIGURATION
                        The name of the configuration class to load, e.g. "Development". If this isn't provided, the DJANGO_CONFIGURATION environment variable will be used.
  --version             show program's version number and exit
  -v {0,1,2,3}, --verbosity {0,1,2,3}
                        Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output
  --settings SETTINGS   The Python path to a settings module, e.g. "myproject.settings.main". If this isn't provided, the DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PYTHONPATH
                        A directory to add to the Python path, e.g. "/home/djangoprojects/myproject".
  --traceback           Raise on CommandError exceptions
  --no-color            Don't colorize the command output.
  --force-color         Force colorization of the command output.
  --skip-checks         Skip system checks.
```