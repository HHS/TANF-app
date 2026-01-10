package main

import (
	"fmt"

	"go-parser/parser/internal/parser"

	"github.com/xuri/excelize/v2"
)

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Required if using kwargs from Python Celery producer
type parse struct {
	datafileId int
	reparseId int
}

func (p *parse) ParseKwargs(kwargs map[string]interface{}) error {
	fmt.Println("Parsing kwargs: ", kwargs)
	if len(kwargs) == 0 {
		return nil
	}
	datafileId, ok := kwargs["data_file_id"]
	if !ok {
		return fmt.Errorf("undefined kwarg data_file_id")
	}
	p.datafileId = datafileId.(int)

	reparseId, ok := kwargs["reparse_id"]
	if !ok {
		return fmt.Errorf("undefined kwarg reparse_id")
	}
	p.reparseId = reparseId.(int)
	return nil
}

func (p *parse) RunTask() (interface{}, error) {
	fmt.Println("Running task with datafileId:", p.datafileId, "and reparseId:", p.reparseId)
	return nil, nil
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Simple consumer since parse doesn't use kwargs. However, Go does not allow default values or a Python producer sending
// a None. There is no conversion to Go's nil. Therefore, the Python consumer must always supply valid args for the Go
// consumer. It CAN NOT use "None" as a value ever.
func parseTask(datafileId, reparseId int) (interface{}, error) {
	fmt.Println("Running task with datafileId:", datafileId, "and reparseId:", reparseId)
	return nil, nil
}

func main() {

	// ctx := context.Background()

	// /////////////////// S3 Testing with aws-sdk-go ///////////////////////////
	// fmt.Println("S3 Testing with aws-sdk-go")
	// s3 := storage.NewS3Storage()
	// objs, err := s3.ListObjects(ctx, "tdp-datafiles-localstack")
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// fmt.Println("Objects:", objs)

	// data, err := s3.DownloadLargeObject(ctx, "tdp-datafiles-localstack", "dev/data_files/2021/Q1/1/TAN/Active Case Data/ADS.E2J.FTP1.TS06")
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// delimmiter := []byte("\n")
	// lines := bytes.Split(data, delimmiter)
	// for _, line := range lines {
	// 	fmt.Println(string(line), len(line))
	// }

	// /////////////////// Postgres Testing with sqlc ///////////////////////////
	// fmt.Println("Postgres Testing with sqlc")
	// conn, err := pgx.Connect(ctx, "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable")
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// defer conn.Close(ctx)

	// q := db.New(conn)
	// _ = q

	// stts, err := q.GetSTTs(ctx)
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// for _, stt := range stts {
	// 	fmt.Println(stt)
	// }

	/////////////////// Parser Testing ///////////////////////////
	fmt.Println("Parser Testing")
	f, err := excelize.OpenFile("/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/fra_ofa_test.xlsx")
    if err != nil {
        fmt.Println(err)
        return
    }
    defer func() {
        // Close the spreadsheet.
        if err := f.Close(); err != nil {
            fmt.Println(err)
        }
    }()

	sheet := f.GetSheetName(0)
	rows, err := f.GetRows(sheet)
    if err != nil {
        fmt.Println(err)
        return
    }
	// Cells are ALWAYS a string type
    for _, row := range rows {
        for _, colCell := range row {
            fmt.Print(colCell, "\t")
        }
        fmt.Println()
    }


	bp := parser.BaseParser{}
	err = bp.InitDecoder()
	if err != nil {
		fmt.Println(err)
		return
	}
	var row parser.RawRow
	for {
		row = bp.Decoder.Decode()
		if row == (parser.RawRow{}) {
			break
		}
		fmt.Println(row)
	}


	/////////////////// Redis Testing with gocelery ///////////////////////////
	// fmt.Println("Redis Testing with gocelery")
	// w, err := worker.NewRedisWorker("redis://localhost:6379", map[string]interface{}{
	// 	"tdpservice.scheduling.parser_task.parse": parseTask,
	// })
	// if err != nil {
	// 	log.Fatal(err)
	// }
	// if err := w.Start(); err != nil {
	// 	log.Fatal(err)
	// }
}
