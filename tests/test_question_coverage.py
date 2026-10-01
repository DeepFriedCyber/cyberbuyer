from buyerjourney.question_coverage import *
def c(i,v):return ComponentCoverage(RequestedComponent(i,i,True),CoverageVerdict(v))
def test_all_supported():assert aggregate_coverage([c("a","SUPPORTED"),c("b","SUPPORTED")])=="SUPPORTED"
def test_some_supported():assert aggregate_coverage([c("a","SUPPORTED"),c("b","UNSUPPORTED")])=="PARTIAL"
def test_none_supported():assert aggregate_coverage([c("a","UNSUPPORTED")])=="UNSUPPORTED"
