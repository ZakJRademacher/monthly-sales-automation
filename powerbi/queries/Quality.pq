let
    Pointer = Json.Document(File.Contents(DataFolder & "/latest.json")),
    Snapshot = if Pointer[contract_version] = 1 then Pointer[snapshot] else error "Unsupported data contract",
    Source = Csv.Document(File.Contents(DataFolder & "/snapshots/" & Snapshot & "/Quality.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"Metric", type text}, {"Value", Int64.Type}}, "en-US")
in
    Typed
