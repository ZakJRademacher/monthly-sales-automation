import {execFileSync} from 'node:child_process';
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
const navy='#20323C',blue='#126F69',muted='#647579',amber='#FFF2CD';
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
const categoryHeader=18,regionHeader=categoryHeader+br.drivers.category.length+4;
// Matched-period inputs and arithmetic live beside the monthly inputs, not in a terminal audit.
const calc=detail;
calc.getRange('O2').values=[['Matched-period inputs & calculations']];
calc.getRange('O3').values=[[`${bs.current_start} to ${bs.current_end}; prior ${bs.prior_start} to ${bs.prior_end}`]];
calc.getRange('O5:R5').values=[['Measure','Current period','Prior year','Change']];
calc.getRange('O6:R8').values=[['Sales',bs.current.sales_units/10000,bs.prior?bs.prior.sales_units/10000:null,null],['Orders',bs.current.orders,bs.prior?bs.prior.orders:null,null],['Average order value',null,null,null]];
calc.getRange('P8:Q8').formulas=[['=IF(P7=0,"n.a.",P6/P7)',bs.prior?'=IF(Q7=0,"n.a.",Q6/Q7)':'="n.a."']];
for(let row=6;row<=8;row++)calc.getRange(`R${row}`).formulas=[[bs.prior?`=IF(OR(P${row}="n.a.",Q${row}=0,Q${row}="n.a."),"n.a.",P${row}/Q${row}-1)`:'="n.a."']];
calc.getRange('P6:Q6').setNumberFormat(fmt);calc.getRange('P7:Q7').setNumberFormat('#,##0');calc.getRange('P8:Q8').setNumberFormat(fmt);calc.getRange('R6:R8').setNumberFormat('0.0%');
calc.getRange('O11:P13').values=[['Sales change',null],['Order-volume contribution',null],['Average-order contribution',null]];
calc.getRange('P11:P13').formulas=bs.prior?[['=P6-Q6'],['=IF(Q7=0,"n.a.",(P7-Q7)*Q8)'],['=IF(OR(Q7=0,P7=0),"n.a.",P7*(P8-Q8))']]:[['="n.a."'],['="n.a."'],['="n.a."']];
calc.getRange('P11:P13').setNumberFormat(fmt);
calc.getRange('O15').values=[['Arithmetic attribution: volume at prior AOV, then current orders at changed AOV. Not causal evidence.']];
for(const [scope,header] of [['category',categoryHeader],['region',regionHeader]]){
 const rows=br.drivers[scope],last=header+rows.length;
 calc.getRange(`O${header}:S${header}`).values=[[scope==='category'?'Category':'Region','Current sales','Prior sales','Sales change','Change %']];
 if(rows.length)calc.getRange(`O${header+1}:S${last}`).values=rows.map(r=>[literal(r.member),r.current_sales_units/10000,r.prior_sales_units===null?null:r.prior_sales_units/10000,null,null]);
 for(let row=header+1;row<=last;row++)calc.getRange(`R${row}:S${row}`).formulas=[[bs.prior?`=P${row}-Q${row}`:'="n.a."',bs.prior?`=IF(Q${row}=0,"n.a.",R${row}/Q${row})`:'="n.a."']];
 calc.getRange(`P${header+1}:R${Math.max(last,header+1)}`).setNumberFormat(fmt);calc.getRange(`S${header+1}:S${Math.max(last,header+1)}`).setNumberFormat('0.0%');head(calc,`O${header}:S${header}`);
}
calc.getRange('O1:S42').format.font={name:'Arial',size:10,color:navy};
calc.getRange('O1:O42').format.columnWidth=30;calc.getRange('P1:S42').format.columnWidth=20;
head(calc,'O5:R5');
head(calc,`O${categoryHeader}:S${categoryHeader}`);head(calc,`O${regionHeader}:S${regionHeader}`);

const lastReviewRow=48+Math.max(br.actions.length,1)*3;
business.showGridLines=false;business.tabColor=navy;
business.getRange(`A1:P${lastReviewRow}`).format={fill:'#F8F6F1',font:{name:'Arial',size:10,color:navy},rowHeight:23,columnWidth:9,verticalAlignment:'center'};
business.getRange(`A1:A${lastReviewRow}`).format.columnWidth=3;
business.getRange(`P1:P${lastReviewRow}`).format.columnWidth=3;
function label(range,text,{size=10,color=navy,bold=false,fill=null}={}){
 const r=business.getRange(range);r.merge();r.values=[[text]];r.format.font={name:'Arial',size,color,bold};if(fill)r.format.fill=fill;return r;
}
function linked(range,formula,format,size=24){const r=label(range,'',{size,bold:true});r.formulas=[[formula]];r.setNumberFormat(format);return r;}
function sign(r){r.conditionalFormats.add('cellIs',{operator:'lessThan',formula:0,format:{font:{color:'#B74732'}}});r.conditionalFormats.add('cellIs',{operator:'greaterThan',formula:0,format:{font:{color:'#126F69'}}});}
label('B2:O2','FIELDNOTES / SALES',{size:10,color:muted,bold:true});
label('B3:O4','The monthly sales review',{size:28});
label('B5:O5',`${bs.current_start} to ${bs.current_end}  /  vs ${bs.prior_start} to ${bs.prior_end}`,{size:10,color:muted});
business.getRange('B6:O6').format.borders={bottom:{style:'thin',color:'#C9C8BF'}};
for(const [left,right,row,name,format] of [['B','E',6,'SALES',fmt],['G','J',7,'ORDERS','#,##0'],['L','O',8,'AVERAGE ORDER',fmt]]){
 business.getRange(`${left}8:${right}13`).format.fill='#FFFFFF';
 label(`${left}8:${right}8`,name,{color:muted,bold:true});
 linked(`${left}9:${right}10`,`='Monthly detail'!P${row}`,format);
 const change=linked(`${left}11:${right}11`,`='Monthly detail'!R${row}`,'+0.0%;-0.0%;0.0%',14);sign(change);
 label(`${left}12:${right}12`,'vs same period last year',{size:9,color:muted});
 const prior=label(`${left}13:${right}13`,'',{size:9,color:muted});prior.formulas=[[bs.prior?`="Prior: "&TEXT('Monthly detail'!Q${row},"${row===7?'#,##0':'#,##0.00'}")`:'="Prior-year delivery missing"']];
}
label('B15:O16',br.headline,{size:18,bold:true});
label('B17:O18',br.interpretation,{color:muted}).format.wrapText=true;
for(const [scope,header,from,to] of [['category',categoryHeader,'B20','H33'],['region',regionHeader,'J20','O33']]){
 const rows=br.drivers[scope];
 if(!rows.length)continue;
 const chart=business.charts.add('bar',calc.getRange(`O${header}:Q${header+rows.length}`));
 chart.title=(scope==='category'?'Category':'Region')+' sales';chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=13;
 chart.legend={position:'bottom',textStyle:{typeface:'Arial',fontSize:10}};
 chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:10}};
 chart.yAxis={numberFormatCode:'#,##0,"k"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
 chart.series.items[0].fill='#126F69';chart.series.items[1].fill='#B8C1C7';chart.setPosition(from,to);
}
label('B34:O34','Sales in source monetary units. Historical sample; currency unspecified.',{size:9,color:muted});
label('B36:O36','01 / HOW THE TOTAL CHANGED',{bold:true});
const bridge=[['B','E','Order-volume effect',12],['G','J','Average-order effect',13],['L','O','Net sales change',11]];
for(const [l,r,name,row] of bridge){label(`${l}38:${r}38`,name,{size:10,color:muted});const v=linked(`${l}39:${r}40`,`='Monthly detail'!P${row}`,'+#,##0.00;-#,##0.00;0.00',18);sign(v);}
label('B42:O43','The bridge is an arithmetic decomposition, not proof of cause. Category and region views overlap; do not add their declines.',{size:9,color:muted}).format.wrapText=true;
label('B45:O45','02 / REVIEW FIRST',{bold:true});
if(!br.actions.length)label('B47:O48',bs.prior?'No declining segments in this comparison.':'Supply the prior-year delivery before ranking declines.',{color:muted}).format.wrapText=true;
for(const [i,r] of br.actions.entries()){
 const row=47+i*3;
 label(`B${row}:G${row}`,`${String(r.priority).padStart(2,'0')}  ${r.segment} / ${r.scope}`,{bold:true});
 const delta=label(`L${row}:O${row}`,r.sales_change,{bold:true,color:'#B74732',size:12});delta.setNumberFormat('+#,##0.00;-#,##0.00;0.00');delta.format.horizontalAlignment='right';
 label(`B${row+1}:O${row+1}`,r.reason,{size:10,color:muted});
 label(`B${row+2}:O${row+2}`,'Check: '+r.product_ids_to_check,{size:9,color:muted});
}
title(main,'Sales history & coverage');
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
detail.tables.add(`A5:J${end}`,true,'MonthlyInputs').style='TableStyleLight1';head(detail,'A5:J5');detail.freezePanes.freezeRows(5);
detail.getRange('A2:J2').merge();detail.getRange('A3:J3').merge();
title(review,'Category review & saved notes');
review.getRange('A3').values=[['Edit yellow Owner / Review status / Review note cells. Export this sheet as CSV UTF-8 and import notes before refreshing.']];review.getRange('A3').format.font={size:10,color:muted};
review.getRange('A5:G5').values=[['Month key','Category','Sales','Owner','Review status','Review note','Next action']];
const ne=notes.length+5;
review.getRange(`A6:G${ne}`).values=notes.map(x=>[x.month,literal(x.category),x.sales_units/10000,literal(x.owner),x.status,literal(x.note),null]);
for(let row=6;row<=ne;row++)review.getRange(`G${row}`).formulas=[[`=IF(E${row}="Reviewed",IF(AND(D${row}<>"",F${row}<>""),"Complete","Add owner and note"),IF(D${row}="","Assign owner","Review period"))`]];
review.getRange(`A6:A${ne}`).setNumberFormat('@');review.getRange(`C6:C${ne}`).setNumberFormat(fmt);review.getRange(`E6:E${ne}`).dataValidation={rule:{type:'list',values:['Not started','In progress','Reviewed']}};
review.getRange('A5:A150').format.columnWidth=16;review.getRange('B5:B150').format.columnWidth=24;review.getRange('D5:D150').format.columnWidth=21;review.getRange('E5:E150').format.columnWidth=19;review.getRange('F5:F150').format.columnWidth=44;review.getRange('G5:G150').format.columnWidth=25;
review.tables.add(`A5:G${ne}`,true,'CategoryReview').style='TableStyleLight1';head(review,'A5:G5');review.getRange(`D6:F${ne}`).format.fill=amber;review.getRange(`F6:F${ne}`).format.wrapText=true;review.getRange(`A6:G${ne}`).format.rowHeight=30;review.freezePanes.freezeRows(5);
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
const chart=main.charts.add('line',detail.getRange(`L${chartHeader}:M${chartHeader+count}`));chart.title='Last 12 observed months · sales';chart.hasLegend=false;chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=12;chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:9}};chart.yAxis={numberFormatCode:'#,##0,"K"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};chart.series.items[0].line={fill:blue,style:'solid',width:2};chart.setPosition('D5','J13');
wb.recalculate();
if(bs.prior&&Math.abs(calc.getRange('P11').values[0][0]-bs.sales_change_units/10000)>0.000001)throw Error('Business review change mismatch');
if(bs.prior&&bs.current.orders&&bs.prior.orders){
 const originalReview=calc.getRange('P6').values[0][0];calc.getRange('P6').values=[[originalReview+100]];wb.recalculate();
 if(Math.abs(calc.getRange('P11').values[0][0]-(bs.sales_change_units/10000+100))>.000001)throw Error('Business review formulas do not propagate');
 if(Math.abs(business.getRange('B9').values[0][0]-(originalReview+100))>.000001)throw Error('Dashboard card does not propagate');
 calc.getRange('P6').values=[[originalReview]];wb.recalculate();
}
const baseline=m.sales_units/10000;
if(Math.abs(main.getRange('B11').values[0][0]-baseline)>0.000001)throw Error('Workbook total mismatch');
const original=detail.getRange('E6').values[0][0];detail.getRange('E6').values=[[original+100]];wb.recalculate();
if(Math.abs(main.getRange('B11').values[0][0]-(baseline+100))>0.000001)throw Error('Refresh total formula does not propagate');detail.getRange('E6').values=[[original]];
const saved=review.getRange('D6:F6').values;review.getRange('D6:F6').values=[['','Reviewed','']];wb.recalculate();if(review.getRange('G6').values[0][0]!=='Add owner and note')throw Error('Review guard failed');
review.getRange('D6:F6').values=[['Test owner','Reviewed','Test evidence']];wb.recalculate();if(review.getRange('G6').values[0][0]!=='Complete')throw Error('Review completion failed');review.getRange('D6:F6').values=saved;wb.recalculate();
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final formula errors'});
const inspected=await wb.inspect({kind:'table',range:'Monthly detail!O5:R13',include:'values,formulas',tableMaxRows:8,tableMaxCols:2,maxChars:2500});
const verification={engine:'artifact-tool',totalMatchesSource:true,inputChangePropagates:true,reviewGuardWorks:true,temporaryInputsRestored:true,nativeExcelRecalculationTested:false,errorScan:errors.ndjson,headlineInspect:inspected.ndjson};
await fs.writeFile(path.join(stage,'workbook-verification.json'),JSON.stringify(verification,null,2)+'\n');
if(render)for(const [s,range,file] of [[business,`A1:P${lastReviewRow}`,'excel-sales-review.png'],[business,'A1:P35','excel-sales-overview.png'],[main,'A1:J35','excel-monthly-report.png'],[detail,'A1:J19','excel-monthly-detail.png'],[detail,'O1:S32','excel-matched-calculations.png'],[review,'A1:G14','excel-category-review.png']]){
 const blob=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});await fs.writeFile(path.join(stage,file),new Uint8Array(await blob.arrayBuffer()));
}
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(stage,`monthly-sales_${m.last_month}.xlsx`));
execFileSync(process.env.PYTHON || 'python', [path.join(root,'tools/normalize_workbook.py'), path.join(stage,`monthly-sales_${m.last_month}.xlsx`)]);
console.log(JSON.stringify({sales:baseline,lastMonth:m.last_month,rows:m.lines,formulaErrorScan:errors.ndjson}));
