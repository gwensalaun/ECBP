#
#
# Name:   bpmn.py - describing BPMN processes in Python
# Authors: Gwen and Paco
#
################################################################################

#!/usr/bin/python3

##
# A Node is an identifier
class Node:

    def __init__(self, ident):
        self.id=ident

    def getIdent(self):
        return self.id

    def print(self):
        print(self.id)

    def isGateway(self):
        return False


##
# A start node
class Start(Node):

    def __init__(self, ident):
        self.id=ident
        self.name=ident

    def getClass(self):
        return "Start"

    def print(self):
        print("start", self.id)

    def isGateway(self):
        return False

##
# An end node
class End(Node):

    def __init__(self, ident):
        self.id=ident
        self.name=ident

    def getClass(self):
        return "End"

    def print(self):
        print("end", self.id)

    def isGateway(self):
        return False



##
# An activity
class Activity(Node):

    def __init__(self, ident, name):
        self.ident=ident
        self.name=name

    def getIdent(self):
        return self.ident

    def getName(self):
        return self.name

    def print(self):
        print("activity", self.ident, self.name)

    def getClass(self):
        return "Activity"

    def setIdent(self, ident):
        self.ident=ident

    def setName(self, name):
        self.name=name

    def isGateway(self):
        return False

##
# A split node
class Split(Node):

    def __init__(self, ident, type):
        self.id=ident
        self.name=type  # this can be: exclusive, inclusive, parallel

    def getType(self):
        return self.name

    def print(self):
        print("split", self.name, self.id)

    def getClass(self):
        return "Split"

    def isGateway(self):
        return True

##
# A join node
class Join(Node):

    def __init__(self, ident, type):
        self.id=ident
        self.name=type  # this can be: exclusive, inclusive, parallel

    def getType(self):
        return self.name

    def print(self):
        print("join", self.name, self.id)

    def getClass(self):
        return "Join"

    def isGateway(self):
        return True

##
# A flow
class Flow:

    def __init__(self, ident, source, target):
        self.id=ident
        self.source=source  # source node (ident)
        self.target=target  # target node (ident)

    def getIdent(self):
        return self.id

    def getSource(self):
        return self.source

    def getTarget(self):
        return self.target

    def setTarget(self, node):
        self.target=node

    def print(self):
        print("flow", self.id,":", self.source, "->", self.target)

##
# A BPMN graph is defined by a set of nodes and a set of flows.
class BPMNGraph:
    def __init__(self, name, nodes, flows):
        self.name=name
        self.nodes = nodes
        self.flows = flows

    def addNode(self, node):
        # if not node.getIdent() in [n.getIdent() for n in self._nodes]:
        self.nodes.add(node)

    def addFlow(self, flow):
        #print("ADD FLOW")
        #flow.print()
        self.flows.add(flow)

    def getNodes(self):
        return self.nodes

    def getFlows(self):
        return self.flows

    def getName(self):
        return self.name

    def getNode(self, ident):
        for n in self.nodes:
            if (n.getIdent()==ident):
                return n

    def getNodePrefix(self, ident):
        for n in self.nodes:
            if (n.getIdent().startswith(ident)):
                return n

    def removeNode(self, ident):
        nds=set()
        for n in self.nodes:
            if (n.getIdent()!=ident):
                nds.add(n)
        self.nodes=nds

    def getFlow(self, ident):
        for f in self.flows:
            if (f.getIdent()==ident):
                return f

    def removeFlow(self, ident):
        fls=set()
        for f in self.flows:
            if (f.getIdent()!=ident):
                fls.add(f)
        self.flows=fls

    # returns the flows outgoing of a given node
    def getOutgoingFlows(self, ident):
        fls=set()
        for f in self.flows:
            if (f.getSource()==ident):
                fls.add(f)
        return fls

    # returns the flows incoming to a given node
    def getIncomingFlows(self, ident):
        fls=set()
        for f in self.flows:
            if (f.getTarget()==ident):
                fls.add(f)
        return fls

    # returns the flows incoming to a given node, but only if the source node is a task
    def getIncomingFlowsActivityOnly(self, ident):
        fls=set()
        for f in self.flows:
            if (f.getTarget()==ident):
                if (f.getSource()=="Activity"):
                    fls.add(f)
        return fls

    def getActivity(self, name):
        for n in self.nodes:
            if (n.getClass()=="Activity") and (n.getName()==name):
                return n

    # returns the start node of the process
    def getStartNode(self):
        for n in self.nodes:
            if (n.getClass()=="Start"):
                return n

    # returns the end nodes of the process
    def getEndNodes(self):
        res=set()
        for n in self.nodes:
            if (n.getClass()=="End"):
                res.add(n)
        return res

    # returns all the tasks of the process
    def getTasks(self):
        res=set()
        for n in self.nodes:
            if (n.getClass()=="Activity"):
                res.add(n)
        return res

    # returns all the splits of the process
    def getSplits(self):
        res=set()
        for n in self.nodes:
            if (n.getClass()=="Split"):
                res.add(n)
        return res

    # returns all the joins of the process
    def getJoins(self):
        res=set()
        for n in self.nodes:
            if (n.getClass()=="Join"):
                res.add(n)
        return res

    # returns all parallel gateways of the process
    def getParallelGateways(self):
        res=set()
        for n in self.nodes:
            if ((n.getClass()=="Split") or (n.getClass()=="Join")) and (n.getType()=="parallel"):
                res.add(n)
        return res

    # returns all exclusive gateways of the process
    def getExclusiveGateways(self):
        res=set()
        for n in self.nodes:
            if ((n.getClass()=="Split") or (n.getClass()=="Join")) and (n.getType()=="exclusive"):
                res.add(n)
        return res

    # computes the alphabet of the process
    def computeAlphabet(self):
        tasks=self.getTasks()
        alpha=set()
        for t in tasks:
            alpha.add(t.getIdent())
        return alpha

    # Prints a BPMN graph
    def print(self):
        print("START OF THE PROCESS PRETTY PRINT")
        print(self.name)
        for n in self.nodes:
            n.print()
        for f in self.flows:
            f.print()
        print("END OF THE PROCESS PRETTY PRINT")

##
# A class defining instances of BPMN processes
class Examples:

    def proc1(self):

        # nodes
        s = Start("s")
        a1 = Activity("a1","A1")
        a2 = Activity("a2","A2")
        e = End("e")
        g1 = Split("g1", "exclusive")
        g2 = Join("g2", "exclusive")

        # flows
        f1 = Flow("f1", "s", "g1")
        f2 = Flow("f2", "g1", "a1")
        f3 = Flow("f3", "g1", "a2")
        f4 = Flow("f4", "a1", "g2")
        f5 = Flow("f5", "a2", "g2")
        f6 = Flow("f6", "g2", "e")

        # BPMN graph
        proc = BPMNGraph("p1", {s, a1, a2, e, g1, g2}, {f1, f2, f3, f4, f5, f6})
        return (proc)



if __name__ == '__main__':

    ex=Examples()
    p1=ex.proc1()
    p1.print()
