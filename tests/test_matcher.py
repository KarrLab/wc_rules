from wc_rules import matcher
import unittest

from wc_rules.chem import Molecule, Site, Bond
from wc_rules.pattern import Pattern
from wc_rules.attributes import *
from wc_rules.matcher import Matcher

class A(Molecule):pass
class X(Site):
    ph = BooleanAttribute()
    v = IntegerAttribute()

class TestReteNet(unittest.TestCase):

    maxDiff = None

    def test_rete_construction(self):
        bnd = Bond(id='bnd')
        a1 = A(id='A1').add_sites(X(id='x1',ph=True,v=0).set_bond(bnd))
        a2 = A(id='A2').add_sites(X(id='x2',ph=True,v=1).set_bond(bnd))
        p4 = Pattern('p4').add_node(a1)

        p5 = Pattern('p5').add_node( A(id='a3') )
        m = Matcher()
        for p in [p4,p5]:
            m.add_pattern(p)
        textgen = m.rete_net.draw_as_gml(as_string=True)

        text = '''graph
[
 directed 1
node [id 0 graphics [ hasOutline 0 fill "#FBB4AE" ]  LabelGraphics [text "(0)root" ]  ]
node [id 1 graphics [ hasOutline 0 fill "#DECBE4" ]  LabelGraphics [text "(1)*0.bond--*1.sites" ]  ]
node [id 10 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(10)p4:x2,p4:bnd" ]  ]
node [id 11 graphics [ hasOutline 0 fill "#DECBE4" ]  LabelGraphics [text "(11)*0.molecule--*1.sites" ]  ]
node [id 12 graphics [ hasOutline 0 fill "#E5D8BD" ]  LabelGraphics [text "(12)store" ]  ]
node [id 13 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(13)p4:x1,p4:A1" ]  ]
node [id 14 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(14)p4:A1,p4:x1" ]  ]
node [id 15 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(15)p4:A1,p4:x1" ]  ]
node [id 16 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(16)p4:x2,p4:A2" ]  ]
node [id 17 graphics [ hasOutline 0 fill "#FED9A6" ]  LabelGraphics [text "(17)isinstance(*,Entity)" ]  ]
node [id 18 graphics [ hasOutline 0 fill "#FED9A6" ]  LabelGraphics [text "(18)isinstance(*,Bond)" ]  ]
node [id 19 graphics [ hasOutline 0 fill "#E5D8BD" ]  LabelGraphics [text "(19)store" ]  ]
node [id 2 graphics [ hasOutline 0 fill "#E5D8BD" ]  LabelGraphics [text "(2)store" ]  ]
node [id 20 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(20)p4:bnd" ]  ]
node [id 21 graphics [ hasOutline 0 fill "#FED9A6" ]  LabelGraphics [text "(21)isinstance(*,Molecule)" ]  ]
node [id 22 graphics [ hasOutline 0 fill "#FED9A6" ]  LabelGraphics [text "(22)isinstance(*,A)" ]  ]
node [id 23 graphics [ hasOutline 0 fill "#E5D8BD" ]  LabelGraphics [text "(23)store" ]  ]
node [id 24 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(24)p4:A1" ]  ]
node [id 25 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(25)p4:A2" ]  ]
node [id 26 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(26)p5:a3" ]  ]
node [id 27 graphics [ hasOutline 0 fill "#FED9A6" ]  LabelGraphics [text "(27)isinstance(*,Site)" ]  ]
node [id 28 graphics [ hasOutline 0 fill "#FED9A6" ]  LabelGraphics [text "(28)isinstance(*,X)" ]  ]
node [id 29 graphics [ hasOutline 0 fill "#CCEBC5" ]  LabelGraphics [text "(29)*.ph==True
*.v==0" ]  ]
node [id 3 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(3)p4:x1,p4:bnd" ]  ]
node [id 30 graphics [ hasOutline 0 fill "#E5D8BD" ]  LabelGraphics [text "(30)store" ]  ]
node [id 31 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(31)p4:x1" ]  ]
node [id 32 graphics [ hasOutline 0 fill "#CCEBC5" ]  LabelGraphics [text "(32)*.ph==True
*.v==1" ]  ]
node [id 33 graphics [ hasOutline 0 fill "#E5D8BD" ]  LabelGraphics [text "(33)store" ]  ]
node [id 34 graphics [ hasOutline 0 fill "#B3CDE3" ]  LabelGraphics [text "(34)p4:x2" ]  ]
node [id 4 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(4)p4:A1,p4:bnd,p4:x1" ]  ]
node [id 5 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(5)p4:A1,p4:bnd,p4:x1" ]  ]
node [id 6 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(6)p4:A1,p4:bnd,p4:x1,p4:x2" ]  ]
node [id 7 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(7)p4:A1,p4:bnd,p4:x1,p4:x2" ]  ]
node [id 8 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(8)p4:A1,p4:A2,p4:bnd,p4:x1,p4:x2" ]  ]
node [id 9 graphics [ hasOutline 0 fill "#FFFFCC" ]  LabelGraphics [text "(9)p4:A1,p4:A2,p4:bnd,p4:x1,p4:x2" ]  ]
edge [ source 0 target 1 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 0 target 11 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 0 target 17 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 1 target 2 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 10 target 6 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 11 target 12 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 12 target 13 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 12 target 16 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 13 target 14 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 14 target 15 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 15 target 4 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 16 target 8 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 17 target 18 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 17 target 21 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 17 target 27 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 18 target 19 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 19 target 20 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 2 target 10 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 2 target 3 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 20 target 5 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 21 target 22 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 22 target 23 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 23 target 24 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 23 target 25 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 23 target 26 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 24 target 14 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 25 target 9 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 27 target 28 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 28 target 29 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 28 target 32 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 29 target 30 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 3 target 4 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 30 target 31 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 31 target 15 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 32 target 33 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 33 target 34 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 34 target 7 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 4 target 5 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 5 target 6 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 6 target 7 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 7 target 8 graphics [ fill "#999999" targetArrow "standard" ]  ]
edge [ source 8 target 9 graphics [ fill "#999999" targetArrow "standard" ]  ]
]
'''

        textgen_split = [x.strip() for x in textgen.split('\n')]
        text_split = [x.strip() for x in text.split('\n')]
        self.assertEqual(len(textgen_split),len(text_split))

        for line1,line2 in zip(textgen_split,text_split):
            self.assertEqual(line1,line2)
        return
