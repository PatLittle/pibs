import {resolve,collect,validate,chartLayout,label} from './model.mjs';
import {enumText} from './vocabulary.mjs';
import {additionalInformation} from './markdown.mjs';
import {buildXMP,documentTitle} from './metadata.mjs';
const A4=[595.28,841.89],MARGIN=44;
const plain=value=>String(value??'').replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g,'$1 ($2)').replace(/\*\*|\*|`/g,'').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/\t/g,'  ');
const selected=(value,mode)=>mode==='bil'?[value?.en||'',value?.fr||'']:[value?.[mode]||''];
export function pdfBlocks(doc,schema,{mode='bil'}={}){
 const blocks=[],root=doc.payload;
 function walk(value,definition,depth=0,key=''){
  const rule=resolve(schema,definition);if(rule['x-hidden']||rule['x-ui']==='id'||rule['x-guidance'])return;
  const labels=rule['x-label']||{en:key,fr:key};
  if(rule['x-ui']==='bilingual'){
   if(rule['x-template']==='additional_information')value={en:additionalInformation(doc,value,'en'),fr:additionalInformation(doc,value,'fr')};
   if(!value?.en&&!value?.fr&&(rule.properties.en.minLength||0)===0)return;
   blocks.push({type:'field',labels:selected(labels,mode),values:selected(value,mode).map(plain),depth});return;
  }
  if(rule.type==='array'){
   if(!value?.length)return;blocks.push({type:'heading',values:selected(labels,mode),depth});
   for(const item of value)walk(item,rule.items,depth+1);return;
  }
  if(rule.type==='object'){
   if(key&&key!=='payload')blocks.push({type:'heading',values:selected(labels,mode),depth});
   for(const[k,field]of Object.entries(rule.properties||{})){
    if(k==='reports_to'&&value?.[k]){const manager=collect(root,'person').find(p=>p.id===value[k]);blocks.push({type:'field',labels:selected(field['x-label'],mode),values:[manager?.name||value[k],manager?.name||value[k]].slice(0,mode==='bil'?2:1),depth});continue;}
    if(key==='additional_information'&&k!=='standard_text')continue;
    walk(value?.[k],field,depth+1,k);
   }
   return;
  }
  if(value===''||value===undefined||value===null)return;
  let values;
  if(rule.enum){values=(mode==='bil'?['en','fr']:[mode]).map(l=>rule['x-enum-labels']?.[value]?.[l]||enumText(value).split(' / ')[l==='fr'?1:0]||value);}
  else if(typeof value==='boolean')values=mode==='bil'?[value?'Yes':'No',value?'Oui':'Non']:[mode==='fr'?(value?'Oui':'Non'):(value?'Yes':'No')];
  else values=mode==='bil'?[plain(value),plain(value)]:[plain(value)];
  blocks.push({type:'field',labels:selected(labels,mode),values,depth});
 }
 walk(root,schema.$defs[root.kind],0,'payload');return blocks;
}
export async function createPDF(doc,schema,{mode='bil',PDFLib,fontkit,regularBytes,boldBytes,form=null,now=new Date().toISOString()}={}){
 if(!['en','fr','bil'].includes(mode))throw Error('Choose EN, FR or BIL.');
 const {PDFDocument,PDFName,PDFString,rgb}=PDFLib;
 const document=await PDFDocument.create();document.registerFontkit(fontkit);
 const regular=await document.embedFont(regularBytes,{subset:true}),bold=await document.embedFont(boldBytes,{subset:true}),charset=new Set(regular.getCharacterSet());
 function safe(text){text=plain(text);const missing=[...text].filter(c=>c!=='\n'&&c!=='\r'&&!charset.has(c.codePointAt(0)));if(missing.length)throw Error('The PDF font cannot render: '+[...new Set(missing)].join(' ')+'. The document is preserved.');return text;}
 function wrap(text,font,size,width){
  const lines=[];for(const paragraph of safe(text||'—').split(/\r?\n/)){
   if(!paragraph){lines.push('');continue;}let line='';
   for(let word of paragraph.split(/\s+/)){
    if(font.widthOfTextAtSize(word,size)>width){if(line){lines.push(line);line='';}let chunk='';for(const char of word){if(chunk&&font.widthOfTextAtSize(chunk+char,size)>width){lines.push(chunk);chunk='';}chunk+=char;}word=chunk;}
    if(line&&font.widthOfTextAtSize(line+' '+word,size)>width){lines.push(line);line=word;}else line+=(line?' ':'')+word;
   }lines.push(line);
  }return lines;
 }
 const complete=validate(doc,schema).length===0,status=complete?'review_ready':'draft',title=documentTitle(doc,mode);let page,y,pageNumber=0;
 const ink=rgb(.14,.2,.28),muted=rgb(.32,.38,.45),lineColor=rgb(.7,.75,.79);
 function newPage(size=A4){page=document.addPage(size);pageNumber++;y=size[1]-MARGIN;
  page.drawText('Document Studio   |   '+mode.toUpperCase()+'   |   '+(complete?'Review copy / Copie pour examen':'DRAFT / BROUILLON'),{x:MARGIN,y:y-7,font:regular,size:8,color:muted});y-=28;
  page.drawLine({start:{x:MARGIN,y},end:{x:size[0]-MARGIN,y},color:lineColor,thickness:.6});y-=22;
 }
 const available=A4[0]-MARGIN*2;
 function heading(value,level=0){const size=level===0?18:level===1?14:11;const lines=wrap(value,bold,size,available);const h=lines.length*(size+4)+14;if(y-h<MARGIN+25)newPage();for(const l of lines){page.drawText(l,{x:MARGIN,y:y-size,font:bold,size,color:ink});y-=size+4;}y-=10;}
 newPage();heading(title,0);
 if(form){const note=mode==='fr'?'Document de préparation. Vérifier le format officiel et les approbations exigées.':mode==='en'?'Preparation copy. Check the required official format and approvals.':'Preparation copy / Document de préparation. Check official format / Vérifier le format officiel.';for(const l of wrap(form.number+' · '+note,regular,8,available)){page.drawText(l,{x:MARGIN,y:y-9,font:regular,size:8,color:muted});y-=11;}y-=8;}
 for(const block of pdfBlocks(doc,schema,{mode})){
  if(block.type==='heading'){heading(block.values.filter(Boolean).join(' / '),Math.min(2,block.depth+1));continue;}
  const columns=mode==='bil'?2:1,gap=columns===2?22:0,width=(available-gap)/columns,prepared=[];
  for(let c=0;c<columns;c++)prepared.push({labels:wrap(block.labels[c]||'',bold,8.4,width),values:wrap(block.values[c]||'—',regular,9.7,width)});
  let labelHeight=Math.max(...prepared.map(c=>c.labels.length))*11+5;
  if(y-labelHeight-24<MARGIN+25)newPage();
  for(let c=0;c<columns;c++){const x=MARGIN+c*(width+gap);let baseline=y;for(const l of prepared[c].labels){page.drawText(l,{x,y:baseline-8.4,font:bold,size:8.4,color:ink});baseline-=11;}}
  y-=labelHeight;let offset=0,maxLines=Math.max(...prepared.map(c=>c.values.length));
  while(offset<maxLines){let fit=Math.floor((y-MARGIN-27)/13);if(fit<1){newPage();fit=Math.floor((y-MARGIN-27)/13);}const end=Math.min(maxLines,offset+fit);
   for(let c=0;c<columns;c++){let baseline=y;const x=MARGIN+c*(width+gap);for(let i=offset;i<end;i++){const l=prepared[c].values[i]||'';if(l)page.drawText(l,{x,y:baseline-10,font:regular,size:9.7,color:ink});baseline-=13;}}
   y-=(end-offset)*13;offset=end;if(offset<maxLines)newPage();
  }
  y-=10;page.drawLine({start:{x:MARGIN,y},end:{x:A4[0]-MARGIN,y},color:lineColor,thickness:.25});y-=14;
 }
 const people=collect(doc.payload,'person');
 if(people.length){
  const layout=chartLayout(people),scale=Math.min(.8,14000/Math.max(layout.width,layout.height)),size=[Math.max(841.89,layout.width*scale+MARGIN*2+20),Math.max(595.28,layout.height*scale+MARGIN*2+65)],byId=new Map(layout.nodes.map(n=>[n.person.id,n]));
  newPage(size);page.drawText(mode==='fr'?'Chaîne de commandement':mode==='en'?'Chain of command':'Chain of command / Chaîne de commandement',{x:MARGIN,y:y-8,font:bold,size:12,color:ink});y-=25;const top=y;
  for(const edge of layout.edges){const a=byId.get(edge.source),b=byId.get(edge.target);page.drawLine({start:{x:MARGIN+(a.x+170)*scale,y:top-(a.y+225)*scale},end:{x:MARGIN+(b.x+170)*scale,y:top-b.y*scale},color:muted,thickness:1});}
  for(const node of layout.nodes){const x=MARGIN+(node.x+10)*scale,topY=top-node.y*scale,w=320*scale,h=225*scale;page.drawRectangle({x,y:topY-h,width:w,height:h,borderColor:lineColor,borderWidth:1});let baseline=topY-12*scale;
   const p=node.person,position=selected(p.position_title,mode).join(' / '),unit=selected(p.organization,mode).join(' / '),programs=(p.programs||[]).map(a=>a.program_id+' · '+selected(a.program_title,mode).join(' / ')).join('\n');
   for(const[value,font,size]of [[p.name,bold,11],[position,regular,9],[[p.classification_group,p.classification_level].filter(Boolean).join('-'),regular,8],[unit,regular,8],[programs,bold,8]]){for(const l of wrap(value||' ',font,size*scale,w-18*scale)){if(baseline-size*scale<topY-h+5*scale)break;page.drawText(l,{x:x+9*scale,y:baseline-size*scale,font,size:size*scale,color:ink});baseline-=(size+3)*scale;}baseline-=3*scale;}
  }

 }
 const pages=document.getPages();for(let i=0;i<pages.length;i++){const p=pages[i];p.drawText('Document Studio · '+doc.document_id+' · '+(i+1)+' / '+pages.length,{x:MARGIN,y:22,font:regular,size:7,color:muted});}
 document.setTitle(title);if(doc.metadata?.creators?.length)document.setAuthor(doc.metadata.creators.join('; '));document.setSubject(doc.metadata?.description?.[mode==='fr'?'fr':'en']||form?.title?.[mode==='fr'?'fr':'en']||'');document.setKeywords(doc.metadata?.keywords||[]);document.setCreator('PIBS Document Studio');document.setProducer('pdf-lib 1.17.1 / Document Studio');document.setCreationDate(doc.metadata?.creation_date?new Date(doc.metadata.creation_date+'T00:00:00Z'):new Date(now));document.setModificationDate(new Date(now));document.catalog.set(PDFName.of('Lang'),PDFString.of(mode==='bil'?'mul':mode));
 const packet=buildXMP(doc,{mode,status,form,now}),metadata=document.context.stream(new TextEncoder().encode(packet),{Type:'Metadata',Subtype:'XML'});document.catalog.set(PDFName.of('Metadata'),document.context.register(metadata));
 return document.save({useObjectStreams:false});
}
let libraries;
function loadScript(path){return new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=new URL(path,import.meta.url);script.onload=resolve;script.onerror=()=>reject(Error('PDF library could not load.'));document.head.append(script);});}
export async function browserPDF(doc,schema,options={}){
 libraries ||= Promise.all([loadScript('./vendor/pdf-lib.min.js'),loadScript('./vendor/fontkit.umd.min.js'),...['Regular','Bold'].map(async name=>{const r=await fetch(new URL('./fonts/NotoSans-'+name+'.ttf',import.meta.url));if(!r.ok)throw Error('PDF font could not load.');return new Uint8Array(await r.arrayBuffer());})]);
 const result=await libraries;return createPDF(doc,schema,{...options,PDFLib:globalThis.PDFLib,fontkit:globalThis.fontkit,regularBytes:result[2],boldBytes:result[3]});
}
