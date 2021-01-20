# Report metadata

Accepts s3 slugs and maintains every prior version of the file


**Request**:

`POST` `/v1/reports/`

Parameters:
```json
{

            "original_filename":"filename", //name of the file before it was uploaded to s3.
            "slug":"hdslajhfdaksdjflajlsdfa",
            "extension":"txt",//optional
            "user":"lnsdfkldlkajdfa",// uuid
            "stt":15 //stt id,
            "year": 2020,
            "quarter":"Q1", // any of Q1,Q2,Q3,Q4
            "section":"Active Case Data", // there are a total of 4 sections. 
                                          //This can be "Active Case Data","Close Case Data",
                                          // "Aggregate Data", or "Stratum Data"
}

```

*Note:*

- Authorization Protected 
- Only OFA admin and OFA analyst roles can access this end point.

**Response**:

```json
Content-Type application/json
200 Ok

{

            "original_filename":"filename", 
            "slug":"hdslajhfdaksdjflajlsdfa",
            "extension":"txt",
            "user":"lnsdfkldlkajdfa",
            "stt":15 
            "year": 2020,
            "quarter":"Q1", 
            "section":"Active Case Data", 
            "version":2
}
```

This will return a JSON response with the report file meta data composed of the following:
+ original_filename : Name of the file before being uploaded
+ slug : String identifying the file in s3
+ extension : The files extension, if none is provided or the file has no extension, we assume text
+ user : A UUID Identifying the user who uploaded this file.
+ stt : A numeric ID representing the STT this report is for
+ year : The year this is a report for
+ quarter : The quarter this is a report for as "Q1", etc
+ section : The section of the report this file is a part of.
+ version : the version of this file

----
