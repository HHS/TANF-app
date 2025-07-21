"""Class definition for record duplicate class and helper classes."""
from tdpservice.parsers.dataclasses import RawRow
from tdpservice.parsers.duplicate_detectors import DuplicateDetectorFactory


class DuplicateManager:
    """Manages all DuplicateDetectors and their errors."""

    def __init__(self, generate_error):
        self.duplicate_detectors = dict()
        self.generate_error = generate_error
        ################################################################################################################
        # WARNING
        self.generated_errors = dict()
        # Do not change/re-assign the dictionary unless you exactly know what you're doing! This object is a one to many
        # relationship. That is, each DuplicateDetector has a reference to this dictionary so that it can store
        # it's generated duplicate errors which avoids needing the DuplicateManager to loop over all
        # DuplicateDetectors to get their errors which is a serious performance boost.
        ################################################################################################################
        self.duplicate_detector_factory = DuplicateDetectorFactory()

    def add_record(self, record, detector_hash, schema, row: RawRow, line_number):
        """Add record to DuplicateDetector and return whether the record has/created errors.

        @param record: a Django model representing a datafile record
        @param detector_hash: a hash value representing the @record's associated detector
        @param schema: the schema from which the record was created
        @param row: the RawRow the decoder parsed from the datafile
        @param line_number: the line number the record was generated from in the datafile
        """
        if detector_hash not in self.duplicate_detectors:
            duplicate_detector = self.duplicate_detector_factory.create(
                schema, detector_hash, self.generated_errors, self.generate_error
            )
            self.duplicate_detectors[detector_hash] = duplicate_detector
        self.duplicate_detectors[detector_hash].add_member(
            record, schema, row, line_number
        )

    def get_generated_errors(self):
        """Return all errors from all DuplicateDetectors."""
        generated_errors = list()
        for errors in self.generated_errors.values():
            generated_errors.extend(errors)
        return generated_errors

    def clear_errors(self):
        """Clear all generated errors."""
        # We MUST call .clear() here instead of re-assigning a new dict() because the duplicate_detectors have a
        # reference to this dictionary. Re-assigning the dictionary means the duplicate_detectors lose their
        # reference.
        self.generated_errors.clear()

    def get_records_to_remove(self):
        """Return dictionary of model:[errors]."""
        records_to_remove = dict()
        for duplicate_detector in self.duplicate_detectors.values():
            for (
                model,
                ids,
            ) in duplicate_detector.get_records_for_post_parse_deletion().items():
                records_to_remove.setdefault(model, []).extend(ids)

        return records_to_remove

    def update_removed(self, detector_hash, should_remove, was_removed):
        """Notify DuplicateDetectors whether detector_hash could or could not be removed from memory."""
        duplicate_detector = self.duplicate_detectors.get(detector_hash, False)
        if duplicate_detector:
            if was_removed and not should_remove:
                duplicate_detector.set_should_remove_from_db(False)
            elif not was_removed and should_remove:
                duplicate_detector.set_should_remove_from_db(True)

    def get_num_dup_errors(self, detector_hash):
        """Return the number of duplicate errors for a specific duplicate detector."""
        if detector_hash in self.duplicate_detectors:
            return self.duplicate_detectors.get(detector_hash).get_num_errors()
        return 0
