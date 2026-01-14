- Note, all the friendly names on yaml schemas are pretty much wrong

- Logs: Parsing super big file in python with NO validation enabled
```bash
2026-01-14 04:28:09,836 INFO base_parser.py::bulk_create_records:L135 : Created 13597/13597 records.
2026-01-14 04:28:12,392 INFO base_parser.py::bulk_create_records:L135 : Created 13572/13572 records.
2026-01-14 04:28:14,887 INFO base_parser.py::bulk_create_records:L135 : Created 13604/13604 records.
2026-01-14 04:28:17,554 INFO base_parser.py::bulk_create_records:L135 : Created 13586/13586 records.
2026-01-14 04:28:20,268 INFO base_parser.py::bulk_create_records:L135 : Created 13609/13609 records.
2026-01-14 04:28:22,900 INFO base_parser.py::bulk_create_records:L135 : Created 13597/13597 records.
2026-01-14 04:28:25,432 INFO base_parser.py::bulk_create_records:L135 : Created 13594/13594 records.
2026-01-14 04:28:28,102 INFO base_parser.py::bulk_create_records:L135 : Created 13606/13606 records.
2026-01-14 04:28:30,689 INFO base_parser.py::bulk_create_records:L135 : Created 13591/13591 records.
2026-01-14 04:28:33,183 INFO base_parser.py::bulk_create_records:L135 : Created 13587/13587 records.
2026-01-14 04:28:35,730 INFO base_parser.py::bulk_create_records:L135 : Created 13604/13604 records.
2026-01-14 04:28:38,254 INFO base_parser.py::bulk_create_records:L135 : Created 13596/13596 records.
2026-01-14 04:28:40,849 INFO base_parser.py::bulk_create_records:L135 : Created 13572/13572 records.
2026-01-14 04:28:43,329 INFO base_parser.py::bulk_create_records:L135 : Created 13594/13594 records.
2026-01-14 04:28:45,872 INFO base_parser.py::bulk_create_records:L135 : Created 13592/13592 records.
2026-01-14 04:28:48,411 INFO base_parser.py::bulk_create_records:L135 : Created 13585/13585 records.
2026-01-14 04:28:51,047 INFO base_parser.py::bulk_create_records:L135 : Created 13607/13607 records.
2026-01-14 04:28:53,601 INFO base_parser.py::bulk_create_records:L135 : Created 13598/13598 records.
2026-01-14 04:28:56,128 INFO base_parser.py::bulk_create_records:L135 : Created 13590/13590 records.
2026-01-14 04:28:58,688 INFO base_parser.py::bulk_create_records:L135 : Created 13587/13587 records.
2026-01-14 04:29:01,459 INFO base_parser.py::bulk_create_records:L135 : Created 13581/13581 records.
2026-01-14 04:29:03,946 INFO base_parser.py::bulk_create_records:L135 : Created 13607/13607 records.
2026-01-14 04:29:06,527 INFO base_parser.py::bulk_create_records:L135 : Created 13588/13588 records.
2026-01-14 04:29:09,010 INFO base_parser.py::bulk_create_records:L135 : Created 13577/13577 records.
2026-01-14 04:29:11,598 INFO base_parser.py::bulk_create_records:L135 : Created 13585/13585 records.
2026-01-14 04:29:14,119 INFO base_parser.py::bulk_create_records:L135 : Created 13580/13580 records.
2026-01-14 04:29:16,756 INFO base_parser.py::bulk_create_records:L135 : Created 13582/13582 records.
2026-01-14 04:29:18,642 INFO base_parser.py::bulk_create_records:L135 : Created 9390/9390 records.
[2026-01-14 04:29:18,648: WARNING/ForkPoolWorker-1]

TIME TO PARSE: 84.03001284599304 seconds
```





# DISCOVERY! As the size of the database tables increase our insertion speed takes a BIG hit. If I parse the super big file with the GO parser on a fresh database it takes ~4.5 seconds. But if I parse the same file when the T1, T2, and T3 tables have millions of records the parsing time continues to increase linearly. When I had 7,938,910 rows per table the parse was taking ~24 seconds. This is likely due to our database having poor index design. Since we are an extremely write heavy system we should consider removing indexes on record tables.

# UPDATE: I thought the above was due to index overhead but that doesn't seem to be the case. Looking at the Postgres logs I can see that the WAL buffer is filling very fast and causing hangups for it to flush. The default WAL size is 1GB locally. I changed it to 4GB and the parsing time dropped to ~12 seconds consistently with Millions of records per table.
