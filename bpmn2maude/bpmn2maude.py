#
# Name: bpmn2maude.py - Generates a Maude file given a BPMN process
#
# Authors: Gwen and Paco
#
###############################################################################

import xml.etree.ElementTree as ET
from bpmn import *
import sys
import re
import os

class BPMNtoMAUDE:

    def __init__(self, filename):
        self.filename=filename

    def getRoot(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()
        return root

    def getTree(self):
        tree = ET.parse(self.filename)
        return tree

    def printString(self):
        xml_str = ET.tostring(self.getRoot(), encoding='unicode')
        print(xml_str)

    def countIncomingFlows(self, ident, flows):
        nbincf=0
        for f in flows:
            if (f.getTarget()==ident):
                nbincf=nbincf+1
        return nbincf

    def generateBPMNObject(self):
        name=""
        nodes=set()
        flows=set()

        tree=self.getTree()

        # we first compute flows, because we need them for identifying
        # split vs merge gateways
        for n in tree.iter():
            tag=n.tag
            newtag= re.sub('{[^}]+}', '', tag)

            if (newtag=="sequenceFlow"):
                flows.add(Flow(n.attrib['id'], n.attrib['sourceRef'], n.attrib['targetRef']))

        # in a second step, we compute nodes
        for n in tree.iter():
            tag=n.tag
            newtag= re.sub('{[^}]+}', '', tag)

            if (newtag=="startEvent"):
                nodes.add(Start(n.attrib['id']))

            if (newtag=="endEvent"):
                nodes.add(End(n.attrib['id']))

            if (newtag=="task") or (newtag=="userTask") or (newtag=="manualTask") or (newtag=="serviceTask") or (newtag=="scriptTask"):
                nodes.add(Activity(n.attrib['id'], n.attrib['name']))

            if (newtag=="exclusiveGateway"):
                nbincf=self.countIncomingFlows(n.attrib['id'], flows)
                if (nbincf>1):
                    nodes.add(Join(n.attrib['id'], "exclusive"))
                else:
                    nodes.add(Split(n.attrib['id'], "exclusive"))

            if (newtag=="inclusiveGateway"):
                nbincf=self.countIncomingFlows(n.attrib['id'], flows)
                if (nbincf>1):
                    nodes.add(Join(n.attrib['id'], "inclusive"))
                else:
                    nodes.add(Split(n.attrib['id'], "inclusive"))

            if (newtag=="parallelGateway"):
                nbincf=self.countIncomingFlows(n.attrib['id'], flows)
                if (nbincf>1):
                    nodes.add(Join(n.attrib['id'], "parallel"))
                else:
                    nodes.add(Split(n.attrib['id'], "parallel"))

        return BPMNGraph(name, nodes, flows)

    def dumpSetInFile(self, f, flows):
        res=""
        nbf=len(flows)
        res=res+"("
        for flow in flows:
            res=res+"\""+flow.getIdent()+"\""
            nbf=nbf-1
            if (nbf>0):
                res=res+","
        res=res+")"
        return res

    def generateMaudeCode(self, proc):
        ftmp=os.path.splitext(self.filename)
        pident=ftmp[0]
        fmaude=pident+".maude"
        f = open(fmaude, 'w')
        f.write("--- this file was automatically generated by the bpmn2maude converter\n\n")
        f.write("sload ../comparison/bpmn-process.maude\n\n")
        f.write("omod "+pident+" is\n")
        f.write("    inc BPMN-PROCESS .\n\n")
        f.write("    op "+pident+" : -> Object .\n")
        f.write("    eq "+pident+" = < \""+pident+"\" : Process | \n")
        f.write("          nodes : ( \n")

        nbnodes=len(proc.getNodes())

        for n in proc.getNodes():

            # CAUTION: not a nice translation (not using OO concepts) but
            # required because nodes and flows are separated in the Python BPMN classes.

            outf=proc.getOutgoingFlows(n.getIdent())
            incf=proc.getIncomingFlows(n.getIdent())

            f.write("                ")
            if (n.getClass()=="Start"):
                f.write("start(\""+n.getIdent()+"\", \""+list(outf).pop().getIdent()+"\")")

            if (n.getClass()=="End"):
                f.write("end(\""+n.getIdent()+"\", \""+list(incf).pop().getIdent()+"\")")

            if (n.getClass()=="Activity"):
                f.write("task(\""+n.getIdent()+"\", \""+n.getName()+"\", \""+list(incf).pop().getIdent()+"\", \""+list(outf).pop().getIdent()+"\")")

            if (n.getClass()=="Split"):
                f.write("split(\""+n.getIdent()+"\", "+n.getType()+", \""+list(incf).pop().getIdent()+"\", "+self.dumpSetInFile(f,outf)+")")

            if (n.getClass()=="Join"):
                f.write("merge(\""+n.getIdent()+"\", "+n.getType()+", "+self.dumpSetInFile(f,incf)+", \""+list(outf).pop().getIdent()+"\")")

            nbnodes=nbnodes-1
            if (nbnodes>0):
                f.write(",\n")

        f.write("\n                  ) > . \n")
        f.write("endom")
        f.close()

if __name__ == '__main__':

    # script format -> python3 bpmn2maude.py x.pif OR python3 bpmn2maude.py all
    #  the second option translates all bpmn files in the current directory

    firstarg=sys.argv[1]
    if (firstarg=="all"):
        os.system('ls *.bpmn >& tmp.txt')
        # call('ls *.bpmn >& tmp.txt', shell=True)
        ff = open('tmp.txt', 'r')
        res=ff.readlines()
        for f in res:
            f2=f.rstrip('\n')
            print(f2)
            r=BPMNtoMAUDE(f2)
            proc=r.generateBPMNObject()
            r.generateMaudeCode(proc)
        os.system('rm tmp.txt')
        os.system('mv *.bpmn BPMN')
        os.system('mv *.maude MAUDE')

    else:
        print(firstarg)
        r=BPMNtoMAUDE(firstarg)
        proc=r.generateBPMNObject()
        r.generateMaudeCode(proc)
