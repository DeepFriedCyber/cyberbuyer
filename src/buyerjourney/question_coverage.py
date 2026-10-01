from dataclasses import dataclass,field
from enum import Enum
class CoverageVerdict(str,Enum): SUPPORTED="SUPPORTED";UNSUPPORTED="UNSUPPORTED"
@dataclass
class RequestedComponent:
 id:str;question:str;material:bool=True
@dataclass
class ComponentCoverage:
 component:RequestedComponent;verdict:CoverageVerdict;facts:list[dict]=field(default_factory=list);rejected_facts:list[dict]=field(default_factory=list)
def aggregate_coverage(items):
 material=[x for x in items if x.component.material]
 if not material:return "UNSUPPORTED"
 yes=sum(x.verdict==CoverageVerdict.SUPPORTED for x in material)
 if yes==len(material):return "SUPPORTED"
 if yes>0:return "PARTIAL"
 return "UNSUPPORTED"
