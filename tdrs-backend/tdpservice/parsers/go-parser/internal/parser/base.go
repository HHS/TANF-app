package parser

import (
	"go-parser/parser/internal/db"
	"os"
)

type BaseParser struct {
	Datafile db.DataFilesDatafile
	Dfs db.ParsersDatafilesummary
	Decoder Decoder
	ErrorGeneratorFactory interface{} // TODO: Replace with error generator interface later
	Section Section
	ProgramType ProgramType
	IsActiveOrClosed bool

	CurrentRow interface{} // TODO: Create row interface to abstract datafile rows
	CurrentRowNum int

	// Specifying unsaved_records here may or may not work for FRA files. If not, we can move it down the
	// inheritance hierarchy.
	UnsavedRecords map[string]interface{}
	UnsavedParserErrors map[string]db.ParserError
	NumErrors int

	// Track cases that have already been serialized that need to be removed because of a case consistency error.
	SerializedCases map[string]struct{}
}

func (bp *BaseParser) InitDecoder() error {
	file, err := os.Open("/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP1.TS06")
	if err != nil {
		return err
	}
	bp.Decoder = NewUtf8Decoder(&DecoderBase{File: file})
	return nil
}
