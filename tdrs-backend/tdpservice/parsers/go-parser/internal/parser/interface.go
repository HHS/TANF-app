package parser

type Parser interface {
	Parse()
}

type Decoder interface {
	Decode() RawRow
	GetHeader() RawRow
	GetRecordType(data string) string
}
