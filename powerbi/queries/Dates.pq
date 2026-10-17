let
    Pointer = Json.Document(File.Contents(DataFolder & "/latest.json")),
    Snapshot = if Pointer[contract_version] = 1 then Pointer[snapshot] else error "Unsupported data contract",
    Source = Csv.Document(File.Contents(DataFolder & "/snapshots/" & Snapshot & "/Dates.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Date", type date}, {"Year", Int64.Type}, {"MonthNumber", Int64.Type}, {"MonthLabel", type text}, {"YearMonth", type text}}, "en-US")
in
    Typed
