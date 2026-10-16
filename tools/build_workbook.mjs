import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(process.env.ARTIFACT_RUNTIME_ROOT ? path.join(process.env.ARTIFACT_RUNTIME_ROOT,'package.json') : import.meta.url);
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const stage=path.resolve(process.argv[2]);
const render=process.argv.includes('--render');
const a=JSON.parse(await fs.readFile(path.join(stage,'analysis.json'),'utf8'));
const m=a.metrics,months=a.reports.monthly,notes=a.reports.category_month;
const wb=Workbook.create();
const business=wb.worksheets.add('Sales review');
const main=wb.worksheets.add('Monthly report'),detail=wb.worksheets.add('Monthly detail'),review=wb.worksheets.add('Category review');
const navy='#213047',blue='#3667AF',muted='#68798D',amber='#FFF2CD';
const fmt='#,##0.00;[Red](#,##0.00)';
const date=key=>new Date(key+'-01T12:00:00Z');
const literal=value=>typeof value==='string'&&value.startsWith('=')?"'"+value:value;
for(const [s,range] of [[main,'A1:K36'],[detail,`A1:M${months.length+6}`],[review,`A1:G${notes.length+6}`]]){
 s.showGridLines=false;s.getRange(range).format.font={name:'Arial',size:10,color:navy};s.getRange(range).format.rowHeight=24;s.getRange(range).format.verticalAlignment='center';s.getRange(range).format.columnWidth=17;
}
main.tabColor=navy;
business.tabColor=navy;
function title(s,text){s.getRange('A2').values=[[text]];s.getRange('A2').format.font={size:16,bold:true,color:navy};}
function head(s,range){s.getRange(range).format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:38,wrapText:true,horizontalAlignment:'center',verticalAlignment:'center'};}
const br=a.business_review,bs=br.summary;
const categoryHeader=18,regionHeader=categoryHeader+br.drivers.category.length+4,actionHeader=regionHeader+br.drivers.region.length+4;
const actionStart=actionHeader+1,footerRow=actionStart+Math.max(br.actions.length,1)+3,lastReviewRow=footerRow+1;
business.showGridLines=false;business.getRange(`A1:F${lastReviewRow}`).format={font:{name:'Arial',size:10,color:navy},rowHeight:24,verticalAlignment:'center',columnWidth:18};
business.getRange(`A1:A${lastReviewRow}`).format.columnWidth=28;business.getRange(`C1:C${lastReviewRow}`).format.columnWidth=22;business.getRange(`F1:F${lastReviewRow}`).format.columnWidth=52;
title(business,'Sales review Â· '+bs.month);
business.getRange('A3').values=[[`${bs.current_start}â€“${bs.current_end} versus ${bs.prior_start}â€“${bs.prior_end} | Historical sample | Source monetary units`]];business.getRange('A3').format.font={size:9,color:muted,italic:true};
business.getRange('A5:D5').values=[['Measure','Current period','Prior year','Change']];
business.getRange('A6:D8').values=[['Sales',bs.current.sales_units/10000,bs.prior?bs.prior.sales_units/10000:null,null],['Orders',bs.current.orders,bs.prior?bs.prior.orders:null,null],['Average order value',null,null,null]];
business.getRange('B8:C8').formulas=[['=IF(B7=0,"n.a.",B6/B7)',bs.prior?'=IF(C7=0,"n.a.",C6/C7)':'="n.a."']];
for(let row=6;row<=8;row++)business.getRange(`D${row}`).formulas=[[bs.prior?`=IF(OR(B${row}="n.a.",C${row}=0,C${row}="n.a."),"n.a.",B${row}/C${row}-1)`:'="n.a."']];
business.getRange('B6:C6').setNumberFormat(fmt);business.getRange('B7:C7').setNumberFormat('#,##0');business.getRange('B8:C8').setNumberFormat(fmt);business.getRange('D6:D8').setNumberFormat('0.0%');business.getRange('B6:C7').format.font.color=blue;
business.getRange('A10:B12').values=[['Sales change',null],['Order-volume contribution',null],['Average-order contribution',null]];
business.getRange('B10:B12').formulas=bs.prior?[['=B6-C6'],['=IF(C7=0,"n.a.",(B7-C7)*C8)'],['=IF(OR(C7=0,B7=0),"n.a.",B7*(B8-C8))']]:[['="n.a."'],['="n.a."'],['="n.a."']];business.getRange('B10:B12').setNumberFormat(fmt);
business.getRange('A14').values=[[br.headline]];business.getRange('A14').format.font={bold:true,size:12};
business.getRange('A15').values=[[br.interpretation]];business.getRange('A15').format.font={size:9,color:muted};
for(const [scope,header] of [['category',categoryHeader],['region',regionHeader]]){
 const rows=br.drivers[scope],endRow=header+rows.length;
 business.getRange(`A${header}:E${header}`).values=[[scope==='category'?'Category':'Region','Current sales','Prior sales','Sales change','Change %']];
 business.getRange(`A${header+1}:E${endRow}`).values=rows.map(r=>[literal(r.member),r.current_sales_units/10000,r.prior_sales_units===null?null:r.prior_sales_units/10000,null,null]);
 for(let row=header+1;row<=endRow;row++){
  business.getRange(`D${row}:E${row}`).formulas=[[bs.prior?`=B${row}-C${row}`:'="n.a."',bs.prior?`=IF(C${row}=0,"n.a.",D${row}/C${row})`:'="n.a."']];
 }
 business.getRange(`B${header+1}:D${endRow}`).setNumberFormat(fmt);business.getRange(`E${header+1}:E${endRow}`).setNumberFormat('0.0%');business.getRange(`B${header+1}:C${endRow}`).format.font.color=blue;head(business,`A${header}:E${header}`);
 business.getRange(`D${header+1}:D${endRow}`).conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#A32626'}}});
}
business.getRange(`A${actionHeader-1}`).values=[['Review first Â· refreshed from the latest CSVs']];business.getRange(`A${actionHeader-1}`).format.font={bold:true,size:12};
business.getRange(`A${actionHeader}:F${actionHeader}`).values=[['Priority','View','Segment','Sales change','Pattern','Product IDs to check']];head(business,`A${actionHeader}:F${actionHeader}`);
if(br.actions.length){
 const ae=actionStart+br.actions.length-1;
 business.getRange(`A${actionStart}:F${ae}`).values=br.actions.map(r=>[r.priority,r.scope,literal(r.segment),r.sales_change,r.reason,literal(r.product_ids_to_check)]);
 business.getRange(`D${actionStart}:D${ae}`).setNumberFormat(fmt);business.getRange(`A${actionStart}:F${ae}`).format.wrapText=true;business.getRange(`A${actionStart}:F${ae}`).format.rowHeight=50;
}else business.getRange(`A${actionStart}`).values=[[bs.prior?'No negative segment changes in this comparison.':'Supply the matching prior-year file before ranking declines.']];
business.getRange(`A${footerRow}`).values=[['Category and region views overlap. Review leads are not additive lost sales.']];business.getRange(`A${lastReviewRow}`).values=[['Trace the listed product IDs to source orders; observed changes do not establish a cause.']];business.getRange(`A${footerRow}:A${lastReviewRow}`).format.font={size:9,color:muted};head(business,'A5:D5');
title(main,'Monthly sales refresh');
main.getRange('A3').values=[[`Full observed-month view | Through ${m.last_month} | Historical sample data`]];main.getRange('A3').format.font={color:muted,italic:true};
main.getRange('A5:B5').values=[['Metric','Value']];
main.getRange('A6:B12').values=[['Report month',null],['Latest month sales',null],['Latest month orders',null],['Latest average order',null],['Full-month sales YoY',null],['Observed total sales',null],['Distinct orders',m.orders]];
const end=5+months.length;
main.getRange('B6:B11').formulas=[[`='Monthly detail'!A${end}`],[`='Monthly detail'!E${end}`],[`='Monthly detail'!D${end}`],[`='Monthly detail'!J${end}`],[`='Monthly detail'!I${end}`],[`=SUM('Monthly detail'!E6:E${end})`]];
main.getRange('A5:A16').format.columnWidth=29;main.getRange('B5:B16').format.columnWidth=20;main.getRange('B6').setNumberFormat('mmm yyyy');main.getRange('B7').setNumberFormat(fmt);main.getRange('B8').setNumberFormat('#,##0');main.getRange('B9').setNumberFormat(fmt);main.getRange('B10').setNumberFormat('0.0%');main.getRange('B11').setNumberFormat(fmt);main.getRange('B12').setNumberFormat('#,##0');
main.getRange('A14').values=[['Amounts use source monetary units; currency is unspecified.']];
main.getRange('A15').values=[['Full observed months; see Sales review for matching day-of-month cutoffs.']];
main.getRange('A16').values=[[m.missing_months?`${m.missing_months} missing monthly file(s): inspect coverage before comparing periods.`:'All monthly files between the first and latest delivery are present.']];
main.getRange('A14:A16').format.font={size:9,color:muted};
title(detail,'Monthly inputs & calculations');
detail.getRange('A3').values=[['Source: kaggle.com/datasets/rohitsahoo/sales-forecasting (GPL 2). Dates: day/month/year. Sales: source units.']];detail.getRange('A3').format.font={size:9,color:muted,italic:true};
detail.getRange('A5:J5').values=[['Month','Coverage','Lines','Orders','Sales','Prior month sales','Sales MoM','Prior year sales','Sales YoY','Average order']];
detail.getRange(`A6:J${end}`).values=months.map(x=>[date(x.month),x.coverage,x.lines,x.orders,x.sales_units===null?null:x.sales_units/10000,null,null,null,null,null]);
for(let row=6;row<=end;row++){
 detail.getRange(`F${row}`).formulas=[[row===6?'=""':`=IF(B${row-1}="Missing file","",E${row-1})`]];
 detail.getRange(`G${row}`).formulas=[[`=IF(OR(B${row}="Missing file",F${row}="",F${row}=0),"n.a.",E${row}/F${row}-1)`]];
 detail.getRange(`H${row}`).formulas=[[row<18?'=""':`=IF(B${row-12}="Missing file","",E${row-12})`]];
 detail.getRange(`I${row}`).formulas=[[`=IF(OR(B${row}="Missing file",H${row}="",H${row}=0),"n.a.",E${row}/H${row}-1)`]];
 detail.getRange(`J${row}`).formulas=[[`=IF(OR(B${row}="Missing file",D${row}=0),"n.a.",E${row}/D${row})`]];
}
detail.getRange(`A6:A${end}`).setNumberFormat('mmm yyyy');detail.getRange(`C6:D${end}`).setNumberFormat('#,##0');
for(const c of ['E','F','H','J'])detail.getRange(`${c}6:${c}${end}`).setNumberFormat(fmt);
for(const c of ['G','I'])detail.getRange(`${c}6:${c}${end}`).setNumberFormat('0.0%');
detail.getRange(`B6:E${end}`).format.font.color=blue;
detail.getRange(`B6:B${end}`).conditionalFormats.add('containsText',{text:'Missing file',format:{fill:'#FCE3E3',font:{color:'#A32626',bold:true}}});
detail.tables.add(`A5:J${end}`,true,'MonthlyInputs');head(detail,'A5:J5');detail.freezePanes.freezeRows(5);
title(review,'Category review & saved notes');
review.getRange('A3').values=[['Edit yellow Owner / Review status / Review note cells. Export this sheet as CSV UTF-8 and import notes before refreshing.']];review.getRange('A3').format.font={size:10,color:muted};
review.getRange('A5:G5').values=[['Month key','Category','Sales','Owner','Review status','Review note','Next action']];
const ne=notes.length+5;
review.getRange(`A6:G${ne}`).values=notes.map(x=>[x.month,literal(x.category),x.sales_units/10000,literal(x.owner),x.status,literal(x.note),null]);
for(let row=6;row<=ne;row++)review.getRange(`G${row}`).formulas=[[`=IF(E${row}="Reviewed",IF(AND(D${row}<>"",F${row}<>""),"Complete","Add owner and note"),IF(D${row}="","Assign owner","Review period"))`]];
review.getRange(`A6:A${ne}`).setNumberFormat('@');review.getRange(`C6:C${ne}`).setNumberFormat(fmt);review.getRange(`E6:E${ne}`).dataValidation={rule:{type:'list',values:['Not started','In progress','Reviewed']}};
review.getRange('A5:A150').format.columnWidth=16;review.getRange('B5:B150').format.columnWidth=24;review.getRange('D5:D150').format.columnWidth=21;review.getRange('E5:E150').format.columnWidth=19;review.getRange('F5:F150').format.columnWidth=44;review.getRange('G5:G150').format.columnWidth=25;
review.tables.add(`A5:G${ne}`,true,'CategoryReview');head(review,'A5:G5');review.getRange(`D6:F${ne}`).format.fill=amber;review.getRange(`F6:F${ne}`).format.wrapText=true;review.getRange(`A6:G${ne}`).format.rowHeight=30;review.freezePanes.freezeRows(5);
// The last observed year is linked to the all-period calculation table.
main.getRange('A20:G20').values=[['Month','Lines','Orders','Sales','Sales MoM','Sales YoY','Coverage']];
const count=Math.min(12,months.length),start=months.length-count;
const chartHeader=end+3;
detail.getRange(`L${chartHeader}:M${chartHeader}`).values=[['Month','Sales']];
for(let i=0;i<count;i++){
 const source=6+start+i,row=21+i;
 main.getRange(`A${row}:G${row}`).formulas=[[`='Monthly detail'!A${source}`,`='Monthly detail'!C${source}`,`='Monthly detail'!D${source}`,`=IF('Monthly detail'!B${source}="Missing file","",'Monthly detail'!E${source})`,`='Monthly detail'!G${source}`,`='Monthly detail'!I${source}`,`='Monthly detail'!B${source}`]];
 const helper=chartHeader+1+i;
 detail.getRange(`L${helper}`).formulas=[[`=TEXT(A${source},"mmm yy")`]];
 if(months[start+i].coverage==='Missing file')detail.getRange(`M${helper}`).values=[[null]];
 else detail.getRange(`M${helper}`).formulas=[[`=E${source}`]];
}
main.getRange(`A21:A${20+count}`).setNumberFormat('mmm yyyy');main.getRange(`B21:C${20+count}`).setNumberFormat('#,##0');main.getRange(`D21:D${20+count}`).setNumberFormat(fmt);main.getRange(`E21:F${20+count}`).setNumberFormat('0.0%');head(main,'A5:B5');head(main,'A20:G20');
main.getRange('A35').values=[['Refresh creates a dated version. Review notes are stored separately and rejoined by month + category.']];main.getRange('A35').format.font={size:9,color:muted};
const chart=main.charts.add('line',detail.getRange(`L${chartHeader}:M${chartHeader+count}`));chart.title='Last 12 observed months Â· sales';chart.hasLegend=false;chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=12;chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:9}};chart.yAxis={numberFormatCode:'#,##0,"K"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};chart.series.items[0].line={fill:blue,style:'solid',width:2};chart.setPosition('D5','J13');
wb.recalculate();
if(bs.prior&&Math.abs(business.getRange('B10').values[0][0]-bs.sales_change_units/10000)>0.000001)throw Error('Business review change mismatch');
if(bs.prior&&bs.current.orders&&bs.prior.orders){
 const originalReview=business.getRange('B6').values[0][0];business.getRange('B6').values=[[originalReview+100]];wb.recalculate();
 if(Math.abs(business.getRange('B10').values[0][0]-(bs.sales_change_units/10000+100))>.000001)throw Error('Business review formulas do not propagate');
 business.getRange('B6').values=[[originalReview]];wb.recalculate();
}
const baseline=m.sales_units/10000;
if(Math.abs(main.getRange('B11').values[0][0]-baseline)>0.000001)throw Error('Workbook total mismatch');
const original=detail.getRange('E6').values[0][0];detail.getRange('E6').values=[[original+100]];wb.recalculate();
if(Math.abs(main.getRange('B11').values[0][0]-(baseline+100))>0.000001)throw Error('Refresh total formula does not propagate');detail.getRange('E6').values=[[original]];
const saved=review.getRange('D6:F6').values;review.getRange('D6:F6').values=[['','Reviewed','']];wb.recalculate();if(review.getRange('G6').values[0][0]!=='Add owner and note')throw Error('Review guard failed');
review.getRange('D6:F6').values=[['Test owner','Reviewed','Test evidence']];wb.recalculate();if(review.getRange('G6').values[0][0]!=='Complete')throw Error('Review completion failed');review.getRange('D6:F6').values=saved;wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final formula errors'});
const inspected=await wb.inspect({kind:'table',range:'Monthly report!A5:B12',include:'values,formulas',tableMaxRows:8,tableMaxCols:2,maxChars:2500});
const verification={engine:'artifact-tool',totalMatchesSource:true,inputChangePropagates:true,reviewGuardWorks:true,temporaryInputsRestored:true,nativeExcelRecalculationTested:false,errorScan:errors.ndjson,headlineInspect:inspected.ndjson};
await fs.writeFile(path.join(stage,'workbook-verification.json'),JSON.stringify(verification,null,2)+'\n');
if(render)for(const [s,range,file] of [[business,`A1:F${lastReviewRow}`,'excel-sales-review.png'],[main,'A1:J35','excel-monthly-report.png'],[detail,'A1:J19','excel-monthly-detail.png'],[review,'A1:G14','excel-category-review.png']]){
 const blob=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});await fs.writeFile(path.join(stage,file),new Uint8Array(await blob.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(stage,`monthly-sales_${m.last_month}.xlsx`));
console.log(JSON.stringify({sales:baseline,lastMonth:m.last_month,rows:m.lines,formulaErrorScan:errors.ndjson}));
