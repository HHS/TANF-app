file = '''T12020101111111115423001401401120513110685300000000000006180060000000000000000000000000000000000222222000000002229012                                       
T2202010111111111541219850512WTTTT@#Y92212222222221012212110065422011400000000000000000000000000000000000000000000000000000000000000000000000000000000000000
T320201011111111154120180118WTTTTTW@W22122222204398100000000120160518WTTTT9T9W22122222204398100000000                                                       
T320201011111111154120190206WTTTT@B#W22122212204398100000000120120127WTTTT@WT022122212204302100000000                                                       
T12020101111111115423001401401120513110685300000000000006180060000000000000000000000000000000000222222000000002229012                                       
T2202010111111111541219850512WTTTT@#Y92212222222221012212110065482011400000000000000000000000000000000000000000000000000000000000000070000000000000000000000
T320201011111111154120180118WTTTTTW@W22122222208398100000000120170518WTTTT9T9W22122222206398100000000                                                       
T320201011111111154120190206WTTTT@B#W22122212704398100000090120120127WTTTT@WT022122212205302100000000                                       '''

class Record:
    def __init__(self, line, id):
        self.id = id
        self.line = line
        self.record_type = line[0:2]
        self.case_number = line[8:19]
        self.rpt_month_year = line[2:8]


class RecordDuplicateManager:

    def __init__(self):
        self.exact_matches = set()
        self.partial_matches = set()
        self.related_matches = set()
        self.records_to_omit = set()
    
    def check_hash(self, record_id, line_hash, partial_hash, related_hash):
        should_omit = False
        should_omit = line_hash in self.exact_matches      
        should_omit = partial_hash in self.partial_matches      
        should_omit = related_hash in self.related_matches

        if should_omit:
            self.records_to_omit.add(record_id)

        self.exact_matches.add(line_hash)
        self.partial_matches.add(partial_hash)
        self.related_matches.add(related_hash)


dup_manager = RecordDuplicateManager()
ids = list()
for id, line in enumerate(file.split('\n')):
    record = Record(line, id)
    ids.append(id)
    line_hash = hash(line)
    partial_hash = hash(record.record_type + record.rpt_month_year + record.case_number)
    related_hash = hash(record.rpt_month_year + record.case_number)
    dup_manager.check_hash(record.id, line_hash, partial_hash, related_hash)

print(dup_manager.records_to_omit)
print(ids)

