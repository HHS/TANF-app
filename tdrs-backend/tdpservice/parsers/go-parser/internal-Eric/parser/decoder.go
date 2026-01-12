package parser

import (
	"bufio"
	"iter"
	"log"
	"os"
	"reflect"
	"strings"
)

type Position struct {
	RowNum int
	ColNum int
}

type RawRow struct {
	Data       interface{}
	RawLen     int
	DecodedLen int
	RowNum     int
	RecordType string
}

func (rr *RawRow) ValueAt(pos Position) interface{} {
	v := reflect.ValueOf(rr.Data)
	switch v.Kind() {
	case reflect.Slice, reflect.Array, reflect.String:
		return v.Slice(pos.RowNum, pos.ColNum)
	default:
		// Should we return error
		return nil
	}
}

func (rr *RawRow) ValueAtIs(pos Position, expected interface{}) bool {
	return rr.ValueAt(pos) == expected
}

type DecoderBase struct {
	File          *os.File
	CurrentRowNum int
}

func (db *DecoderBase) Lines() iter.Seq[string] {
	return func(yield func(line string) bool) {
		// TODO: uncomment this when actually pulling from S3
		// defer os.Remove(db.File.Name())
		defer db.File.Close()

		scanner := bufio.NewScanner(db.File)
		for scanner.Scan() {
			text := scanner.Text()
			if !yield(text) {
				return // Stop iteration if the consumer breaks the loop
			}
		}
		if err := scanner.Err(); err != nil {
			log.Printf("error during file scanning: %v\n", err)
		}
	}
}

type Utf8Decoder struct {
	*DecoderBase
	next func() (string, bool)
	stop func()
}

func NewUtf8Decoder(base *DecoderBase) *Utf8Decoder {
	d := &Utf8Decoder{DecoderBase: base}
	d.next, d.stop = iter.Pull(d.Lines())
	return d
}

func (d *Utf8Decoder) Close() {
	if d.stop != nil {
		d.stop()
	}
}

func (d *Utf8Decoder) Decode() RawRow {
	rawData, ok := d.next()
	if !ok {
		return RawRow{}
	}
	d.CurrentRowNum++
	rawLen := len(rawData)
	decodedData := strings.TrimRight(rawData, "\r\n")
	decodedLen := len(decodedData)
	recordType := d.GetRecordType(decodedData)
	return RawRow{
		Data:       decodedData,
		RowNum:     d.CurrentRowNum,
		RecordType: recordType,
		RawLen:     rawLen,
		DecodedLen: decodedLen,
	}
}

func (d *Utf8Decoder) GetHeader() RawRow {
	rawData, ok := d.next()
	if !ok {
		return RawRow{}
	}
	decodedData := strings.TrimRight(rawData, "\r\n")
	return RawRow{
		Data:       decodedData,
		RowNum:     0,
		RecordType: "HEADER",
		RawLen:     len(rawData),
		DecodedLen: len(decodedData),
	}
}

func (d *Utf8Decoder) GetRecordType(data string) string {
	if strings.HasPrefix(data, "HEADER") {
		return "HEADER"
	}
	if strings.HasPrefix(data, "TRAILER") {
		return "TRAILER"
	}
	return data[:2]
}
