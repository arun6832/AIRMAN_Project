import os, re, json
import pdfplumber
def extract_text_with_pdfplumber(path): 
    texts=[]
    with pdfplumber.open(path) as pdf:
        for p in pdf.pages:
            texts.append(p.extract_text() or '')
    return '\n'.join(texts)
def search_numeric_limits_by_regex(full_text):
    res={'max_demonstrated_crosswind_kt':None,'max_wind_kt_recommendation':None,'min_visibility_km_recommendation':None,'other_notes':''}
    t=full_text.lower()
    m=re.search(r'(?:crosswind)[^0-9\n]{0,40}([0-9]{1,2})',t)
    if m: res['max_demonstrated_crosswind_kt']=float(m.group(1))
    m2=re.search(r'(?:visibility)[^0-9\n]{0,40}([0-9]{1,3})\s*(km|m)?',t)
    if m2:
        val=float(m2.group(1))
        unit=m2.group(2) or ''
        if unit.startswith('m') and val>10: val=val/1000.0
        res['min_visibility_km_recommendation']=val
    return res
class SimpleRAG:
    def __init__(self): self.docs=[]
    def build_index_from_pdfs(self,pdfs):
        for p in pdfs:
            self.docs.append(extract_text_with_pdfplumber(p))
    def retrieve(self,query,k=6): return [{'score':1.0,'doc':d} for d in self.docs[:k]]
    def extract_limits_from_chunks(self,chunks,aircraft_label,pdf_paths=None):
        combined='\n'.join(chunks)
        if pdf_paths:
            full=''
            for p in pdf_paths:
                if os.path.exists(p):
                    full += extract_text_with_pdfplumber(p)+'\n'
            found=search_numeric_limits_by_regex(full)
            if any(found.values()): return found
        found2=search_numeric_limits_by_regex(combined)
        if any(found2.values()): return found2
        return {'max_demonstrated_crosswind_kt':None,'max_wind_kt_recommendation':None,'min_visibility_km_recommendation':None,'other_notes':'none'}
