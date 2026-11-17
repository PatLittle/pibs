"""Read actual exported PDF metadata and text with an independent PDF implementation."""
import logging
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
import pdfplumber
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1
from pdfminer.utils import decode_text
logging.disable(logging.CRITICAL)
NS={'dc':'http://purl.org/dc/elements/1.1/','rdf':'http://www.w3.org/1999/02/22-rdf-syntax-ns#','iptc':'http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/','ext':'http://iptc.org/std/Iptc4xmpExt/2008-02-29/','example':'https://example.invalid/ns/','mm':'http://ns.adobe.com/xap/1.0/mm/','ds':'https://patlittle.github.io/pibs/document-studio/ns/1.0/'}
instances=[]
for mode in ['en','fr','bil']:
    path=Path(sys.argv[1])/(mode+'.pdf')
    with path.open('rb') as f:
        pdf=PDFDocument(PDFParser(f));stream=resolve1(pdf.catalog['Metadata'])
        assert str(stream.attrs['Type'])=="/'Metadata'"
        root=ET.fromstring(stream.get_data())
        assert root.find('.//dc:creator/rdf:Seq/rdf:li',NS).text=='Fictional Author'
        assert root.find('.//iptc:CreatorContactInfo/iptc:CiEmailWork',NS).text=='author@example.invalid'
        assert root.find('.//iptc:CountryCode',NS).text=='CAN'
        assert root.find('.//ext:OrganisationInImageName/rdf:Bag/rdf:li',NS).text=='Fictional institution'
        assert root.find('.//example:Provenance/example:source',NS).text=='Example & <source>'
        assert root.find('.//example:Label/rdf:Alt/rdf:li',NS).text=='Example'
        assert root.find('.//example:Provenance/example:nested/example:contributors/rdf:Bag/rdf:li/example:name',NS).text=='Fictional'
        assert [li.text for li in root.findall('.//dc:language/rdf:Bag/rdf:li',NS)]==(['en','fr'] if mode=='bil' else [mode])
        assert root.find('.//ds:DocumentStatus',NS).text=='review_ready'
        assert decode_text(resolve1(pdf.info[0])['Author'])=='Fictional Author'
        instances.append(root.find('.//mm:InstanceID',NS).text)
    with pdfplumber.open(path) as pdf:
        text='\n'.join(p.extract_text() or '' for p in pdf.pages)
        assert ('English-only title' in text)==(mode!='fr'),mode
        assert ('Titre exclusivement français' in text)==(mode!='en'),mode
        assert ('Deputy head' in text)==(mode!='fr'),mode
        assert ('Administrateur général' in text)==(mode!='en'),mode
        for name in ['Morgan Example','Alex Example','Sam Example']:assert name in (pdf.pages[-1].extract_text() or ''),mode
assert len(set(instances))==3
print('Verified EN/FR/BIL text, Unicode, full chart, PDF Info, XMP and IPTC Core/Extension metadata.')
