// XMP is the PDF metadata container. IPTC Core/Extension properties live in its RDF packet.
export const NS={rdf:'http://www.w3.org/1999/02/22-rdf-syntax-ns#',dc:'http://purl.org/dc/elements/1.1/',xmp:'http://ns.adobe.com/xap/1.0/',pdf:'http://ns.adobe.com/pdf/1.3/',xmpMM:'http://ns.adobe.com/xap/1.0/mm/',xmpRights:'http://ns.adobe.com/xap/1.0/rights/',photoshop:'http://ns.adobe.com/photoshop/1.0/',Iptc4xmpCore:'http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/',Iptc4xmpExt:'http://iptc.org/std/Iptc4xmpExt/2008-02-29/',ds:'https://patlittle.github.io/pibs/document-studio/ns/1.0/'};
const xmlName=/^[A-Za-z_][A-Za-z0-9_.-]*$/;
export function xml(value){const s=String(value??'');if(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/.test(s))throw Error('Metadata contains an invalid XML control character.');return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&apos;');}
export function validateMetadata(metadata={}){
 const namespaces={...NS};const keys=new Set();
 for(const item of metadata.additional_properties||[]){
  if(!xmlName.test(item.prefix)||!xmlName.test(item.property)||!/^[A-Za-z][A-Za-z0-9+.-]*:/.test(item.namespace)||['xml','xmlns','rdf','x'].includes(item.prefix))throw Error('Use a valid, non-reserved namespace URI, prefix and property name.');
  if(namespaces[item.prefix]&&namespaces[item.prefix]!==item.namespace)throw Error('A namespace prefix cannot be rebound.');namespaces[item.prefix]=item.namespace;
  const key=item.namespace+'#'+item.property;if(keys.has(key))throw Error('Duplicate additional metadata property: '+key);keys.add(key);
  if(!['text','bag','seq','lang_alt','structure'].includes(item.type))throw Error('Unsupported metadata value type.');
  if(item.type!=='text'){let value;try{value=JSON.parse(item.value);}catch{throw Error('Structured metadata values must be valid JSON.');}if(['bag','seq'].includes(item.type)&&!Array.isArray(value))throw Error('Bag/sequence values must be JSON arrays.');if(['lang_alt','structure'].includes(item.type)&&(!value||typeof value!=='object'||Array.isArray(value)))throw Error('Language/structure values must be JSON objects.');}
 }
 return namespaces;
}
export function documentTitle(doc,mode='bil'){
 const title=doc.metadata?.title,root=doc.payload;
 const base=title?.en||title?.fr?title:(root.institution_name||root.title||root.position_title||{en:root.name||root.kind,fr:root.name||root.kind});
 return mode==='en'?(base.en||base.fr||root.kind):mode==='fr'?(base.fr||base.en||root.kind):[base.en,base.fr].filter(Boolean).join(' / ');
}
export function buildXMP(doc,{mode='bil',status='draft',form=null,now=new Date().toISOString(),instanceID='uuid:'+crypto.randomUUID()}={}){
 const m=doc.metadata||{},namespaces=validateMetadata(m),parts=[],written=new Set();
 const expanded=key=>{const [prefix,name]=key.split(':');return namespaces[prefix]+'#'+name;};
 const scalar=(key,value)=>{if(value===undefined||value===null||value==='')return;parts.push('<'+key+'>'+xml(value)+'</'+key+'>');written.add(expanded(key));};
 const list=(key,values,type='Bag')=>{if(!values?.length)return;parts.push('<'+key+'><rdf:'+type+'>'+values.map(v=>'<rdf:li>'+xml(v)+'</rdf:li>').join('')+'</rdf:'+type+'></'+key+'>');written.add(expanded(key));};
 const langAlt=(key,value)=>{if(!value?.en&&!value?.fr)return;const first=value.en||value.fr;parts.push('<'+key+'><rdf:Alt><rdf:li xml:lang="x-default">'+xml(first)+'</rdf:li>'+Object.entries(value).filter(([,v])=>v).map(([lang,v])=>'<rdf:li xml:lang="'+xml(lang)+'">'+xml(v)+'</rdf:li>').join('')+'</rdf:Alt></'+key+'>');written.add(expanded(key));};
 langAlt('dc:title',m.title?.en||m.title?.fr?m.title:(doc.payload.institution_name||doc.payload.title||{en:documentTitle(doc,'en'),fr:documentTitle(doc,'fr')}));
 langAlt('dc:description',m.description);list('dc:creator',m.creators,'Seq');list('dc:subject',m.keywords);list('dc:language',mode==='bil'?['en','fr']:[mode]);scalar('dc:format','application/pdf');scalar('dc:identifier',doc.document_id);
 langAlt('dc:rights',m.copyright_notice);langAlt('xmpRights:UsageTerms',m.rights_usage_terms);scalar('xmpRights:WebStatement',m.rights_url);
 scalar('xmp:CreatorTool','PIBS Document Studio');scalar('xmp:CreateDate',m.creation_date||now);scalar('xmp:ModifyDate',now);scalar('xmp:MetadataDate',now);scalar('pdf:Producer','pdf-lib 1.17.1 / Document Studio');scalar('pdf:Keywords',(m.keywords||[]).join('; '));
 scalar('xmpMM:DocumentID','urn:document-studio:'+encodeURIComponent(doc.document_id));scalar('xmpMM:InstanceID',instanceID);
 scalar('photoshop:Headline',m.headline||documentTitle(doc,mode));scalar('photoshop:AuthorsPosition',m.creator_job_title);scalar('photoshop:Credit',m.credit);scalar('photoshop:Source',m.source);scalar('photoshop:CaptionWriter',m.caption_writer);scalar('photoshop:Instructions',m.instructions);scalar('photoshop:DateCreated',m.creation_date);
 scalar('Iptc4xmpCore:IntellectualGenre',m.intellectual_genre);scalar('Iptc4xmpCore:CountryCode',m.country_code);list('Iptc4xmpCore:SubjectCode',m.subject_codes);list('Iptc4xmpCore:Scene',m.scene_codes);scalar('Iptc4xmpExt:DigitalSourceType',m.digital_source_type);
 const contact={CiEmailWork:m.contact_email,CiTelWork:m.contact_phone,CiUrlWork:m.contact_url,CiAdrExtadr:m.contact_address,CiAdrCity:m.contact_city,CiAdrRegion:m.contact_region,CiAdrPcode:m.contact_postal_code,CiAdrCtry:m.contact_country};
 if(Object.values(contact).some(Boolean)){parts.push('<Iptc4xmpCore:CreatorContactInfo rdf:parseType="Resource">'+Object.entries(contact).filter(([,v])=>v).map(([k,v])=>'<Iptc4xmpCore:'+k+'>'+xml(v)+'</Iptc4xmpCore:'+k+'>').join('')+'</Iptc4xmpCore:CreatorContactInfo>');written.add(expanded('Iptc4xmpCore:CreatorContactInfo'));}
 scalar('ds:SchemaVersion',doc.schema_version);scalar('ds:DocumentType',doc.payload.kind);scalar('ds:DocumentStatus',status);scalar('ds:LanguageView',mode);scalar('ds:DocumentID',doc.document_id);
 if(form){scalar('ds:GovernmentFormNumber',form.number);list('dc:source',Object.values(form.official_sources||{}));scalar('ds:CompletionMode',form.completion_mode);}
 function structure(value,prefix){return Object.entries(value).map(([key,v])=>{const pieces=key.split(':');if(pieces.length>2||pieces.some(p=>!xmlName.test(p)))throw Error('Invalid structured metadata key.');const name=pieces.length===2?key:prefix+':'+key;if(!Object.hasOwn(namespaces,name.split(':')[0]))throw Error('Unknown metadata namespace.');if(Array.isArray(v))return '<'+name+'><rdf:Bag>'+v.map(x=>{if(Array.isArray(x))throw Error('Nested RDF lists need named structure properties.');return x&&typeof x==='object'?'<rdf:li rdf:parseType="Resource">'+structure(x,prefix)+'</rdf:li>':'<rdf:li>'+xml(x)+'</rdf:li>';}).join('')+'</rdf:Bag></'+name+'>';if(v&&typeof v==='object')return '<'+name+' rdf:parseType="Resource">'+structure(v,prefix)+'</'+name+'>';return '<'+name+'>'+xml(v)+'</'+name+'>';}).join('');}
 for(const item of m.additional_properties||[]){const key=item.prefix+':'+item.property;if(written.has(expanded(key)))throw Error('Additional metadata duplicates a populated standard field: '+key);let body;
  if(item.type==='text')body=xml(item.value);
  else{const value=JSON.parse(item.value);if(item.type==='structure')body=structure(value,item.prefix);else if(item.type==='lang_alt')body='<rdf:Alt>'+Object.entries(value).map(([l,v])=>{if(!/^(?:x-default|[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*)$/.test(l))throw Error('Invalid metadata language tag.');return '<rdf:li xml:lang="'+xml(l)+'">'+xml(v)+'</rdf:li>';}).join('')+'</rdf:Alt>';else{const tag=item.type==='seq'?'Seq':'Bag';body='<rdf:'+tag+'>'+value.map(v=>v&&typeof v==='object'?'<rdf:li rdf:parseType="Resource">'+structure(v,item.prefix)+'</rdf:li>':'<rdf:li>'+xml(v)+'</rdf:li>').join('')+'</rdf:'+tag+'>';}}
  parts.push('<'+key+(item.type==='structure'?' rdf:parseType="Resource"':'')+'>'+body+'</'+key+'>');
 }
 return '<?xpacket begin="\uFEFF" id="W5M0MpCehiHzreSzNTczkc9d"?>\n<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Document Studio"><rdf:RDF xmlns:rdf="'+NS.rdf+'"><rdf:Description rdf:about="" '+Object.entries(namespaces).filter(([k])=>k!=='rdf').map(([key,value])=>'xmlns:'+key+'="'+xml(value)+'"').join(' ')+'>'+parts.join('\n')+'</rdf:Description></rdf:RDF></x:xmpmeta>\n<?xpacket end="w"?>';
}
