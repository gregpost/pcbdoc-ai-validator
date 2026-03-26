# pcbdoc_filter.py
# Фильтр PCB: удаление LAYER, механических и геометрических полей

import sys,re

class FieldFilter:
    def __init__(self):
        self.drop_prefix=(
            "INDEXFORSAVE","PATTERN","NAMEON","COMMENTON","GROUPNUM","COUNT",
            "UNIONINDEX","CHANNELOFFSET","SOURCEUNIQUEID","SOURCEHIERARCHICALPATH",
            "SOURCEFOOTPRINTLIBRARY","SOURCECOMPONENTLIBRARY",
            "FOOTPRINTDESCRIPTION","SOURCECOMPLIBIDENTIFIERKIND","SOURCECOMPLIBRARYIDENTIFIER",
            "VAULTGUID","ITEMGUID","ITEMREVISIONGUID","POLYGONTYPE","POUROVER","REMOVEDEAD",
            "HATCHSTYLE","USEOCTAGONS","SA","SHELVED","RESTORELAYER","REMOVEISLANDSBYAREA",
            "REMOVENECKS","AREATHRESHOLD","POUROVERSTYLE","POURINDEX","IGNOREVIOLATIONS",
            "SOLDERMASKEXPANSIONMODE","PASTEMASKEXPANSIONMODE",
            "OVERRIDEWITHV6_6SHAPES","FONT","MIRROR","USETTFONTS","BOLD","ITALIC",
            "INVERTED","FONTNAME","WIDESTRING","USEINVERTEDRECTANGLE","TTFINVERTEDTEXTJUSTIFY",
            "TEXTKIND","BARCODEKIND","BARCODERENDERMODE","BARCODEINVERTED","BARCODEFONTNAME",
            "BARCODESHOWTEXT","ADVANCESNAPPING","STARTANGLE","ENDANGLE","SWAPID_PAD","SWAPID_GATE",
            "SWAPPEDPADNAME", "CCSV", "CPLV", "CCWV", "CENV", "CAGV" "CPEV", "CSEV", "CPCV",
            "CPRV", "CEN", "GATEID", "UNIQUEID",
            "SELECTION","LOCKED","USERROUTED","POLYGONOUTLINE","JUMPERSVISIBLE",
            "HOLECOUNT","BODYPROJECTION","BODYOPACITY3D",
            "PADMODE","DRILLTYPE","HOLETYPE","PADJUMPERID","DAISYCHAIN"
        )
        self.drop_indexed_regex=re.compile(
            r"(PAD[XY]OFFSET\d+|.*_MRWIDTH.*|.*SHAPE.*|.*ROTATION.*|.*Y\d+|.*X\d+|.*COLOR.*|.*MODEL.*|.*COUNT.*|.*BODY.*|.*LAYER.*|.*3D.*|.*KIND.*|.*CHECKSUM.*|.*TEXTURE.*|.*CONTOUR.*|.*POLY.*|EA\d+|LOOKAT.*|ZOOMMULT|VIEWSIZE.*|GR0_.*|EGMULT|NEAROBJECTSET|FAROBJECTSET|DRILLSYMBOL.*|HASHKEY.*|HASHVALUE.*|FN#.*|TEARDROPPARAM_.*|SURFACEMICROSTRIP_.*|SYMMETRICSTRIPLINE_.*|BOARDINSIGHTVIEWCONFIGURATIONNAME)$"
        )
        self.drop_value_mil=re.compile(r".*=[0-9.+-]+mil$")

    def is_drop(self,key:str,value:str="")->bool:
        return key.startswith(self.drop_prefix) \
            or self.drop_indexed_regex.match(key) \
            or self.drop_value_mil.match(f"{key}={value}")

class PcbDocParser:
    def __init__(self,filter_:FieldFilter): self.filter=filter_
    def parse_line(self,line:str)->str:
        parts=line.strip().split("|")
        return "|".join([p for p in parts if "=" in p and not self.filter.is_drop(*p.split("=",1))])
    def process(self,src:str)->str:
        return "\n".join([self.parse_line(l) for l in src.splitlines() if self.parse_line(l)])

if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage: python pcbdoc_filter.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file=sys.argv[1]
    output_file=sys.argv[2]
    
    with open(input_file,"r",encoding="cp1251",errors="replace") as f:
        data=f.read()
    
    parser=PcbDocParser(FieldFilter())
    
    with open(output_file,"w",encoding="utf-8") as f:
        f.write(parser.process(data))
    
    print(f"Filtered PCB data saved to: {output_file}")