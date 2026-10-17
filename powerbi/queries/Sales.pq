let
    Pointer = Json.Document(File.Contents(DataFolder & "/latest.json")),
    Snapshot = if Pointer[contract_version] = 1 then Pointer[snapshot] else error "Unsupported data contract",
    Source = Csv.Document(File.Contents(DataFolder & "/snapshots/" & Snapshot & "/Sales.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"LineID", type text}, {"OrderID", type text}, {"OrderDate", type date}, {"ShipDate", type date}, {"Category", type text}, {"Region", type text}, {"ProductID", type text}, {"SalesUnits", Int64.Type}, {"SourceFile", type text}, {"SourceRow", Int64.Type}}, "en-US")
in
    Typed
