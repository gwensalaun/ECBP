#
# Name:    compare.py - Efficient semantic comparison of two BPMN processes
#
# Authors: Gwen and Paco
# Date:    2023
###############################################################################

import sys
import maude
import os
from subprocess import call

# removes generated files
def clean ():
    call("rm *.o *.maude *.aut bisimulator", shell=True)
    call("mv diag.bcg diag.bcg.tmp", shell=True)
    call("rm *.bcg", shell=True)
    call("mv diag.bcg.tmp diag.bcg", shell=True)


if __name__ == '__main__':

    # CAUTION: replace with your own local path..
    # sys.path.insert(0, '/Users/duran/git/workflowrefactoring/TOOLS/bpmn2maude')
    # sys.path.insert(0, '/Users/salaung/WORK/TOOLS/REFACTORING/workflowrefactoring/TOOLS/bpmn2maude')
    sys.path.insert(0, '../bpmn2maude')

    from bpmn2maude import *

    # script format -> python3 compare.py p1.bpmn p2.bpmn option
    # with option = full | box

    if (len(sys.argv)<4):

        print("Erroneous number of parameters, missing parameters !")
        print("Expected syntax: python3 compare.py ex1.bpmn ex2.bpmn box|full")

    elif (len(sys.argv)>4):

        print("Erroneous number of parameters, too many parameters !")
        print("Expected syntax: python3 compare.py ex1.bpmn ex2.bpmn box|full")

    else:

        f1 = sys.argv[1]
        f2 = sys.argv[2]
        option = sys.argv[3]

        # step 1. transform bpmn to maude

        r1=BPMNtoMAUDE(f1)
        p1=r1.generateBPMNObject()
        r1.generateMaudeCode(p1)
        r2=BPMNtoMAUDE(f2)
        p2=r2.generateBPMNObject()
        r2.generateMaudeCode(p2)

        # step 2. call the maude comparison with the two generated (maude) files
        maude.init()
        maude.setAllowFiles(True)
        tmp=os.path.splitext(f1)
        ident1=tmp[0]
        tmp=os.path.splitext(f2)
        ident2=tmp[0]
        maude.load('../comparison/bpmn-comp.maude')
        maude.load(ident1+'.maude')
        maude.load(ident2+'.maude')
        maude.input('omod EX1 is inc BPMN-COMPARISON . inc '+ident1+' . inc '+ident2+' . endom')
        run = maude.getModule('EX1')

        if (option=="full"):
            # FULL COMPARISON
            print("FULL COMPARISON OF LTSs: ")
            tf1 = run.parseTerm('writeAutFile('+ident1+',"'+ident1+'")')
            tf1.erewrite()
            tf2 = run.parseTerm('writeAutFile('+ident2+',"'+ident2+'")')
            tf2.erewrite()
            call('bcg_io '+ident1+'.aut .bcg', shell=True)
            call('bcg_io '+ident2+'.aut .bcg', shell=True)
            res=call('bcg_open '+ident1+'.bcg bisimulator -branching -diag diag.bcg '+ident2+'.bcg', shell=True)
            clean()

        else:
            # COMPARISON USING BOXES
            print("EFFICIENT COMPARISON USING BOXES: ")
            t = run.parseTerm('compare('+ident1+','+ident2+', "'+ident1+"-"+ident2+'", true)')
            t.erewrite()
            s = run.parseTerm('success')
            if t.equal(s):
                print("TRUE")
            else:

                # step 3. call CADP with the new files generated by maude (loop possibly required)
                res=call('ls -l output_'+ident1+"-"+ident2+'*.aut | wc -l > tmp.txt', shell=True)
                f = open('tmp.txt', 'r')
                res=f.read()
                if (int(res)>2):
                    nbcouples=int(res)//2
                    for i in range(nbcouples):
                        call('bcg_io output_'+ident1+"-"+ident2+'_'+str(i)+'_0.aut .bcg', shell=True)
                        call('bcg_io output_'+ident1+"-"+ident2+'_'+str(i)+'_1.aut .bcg', shell=True)
                        res=call('bcg_open output_'+ident1+"-"+ident2+'_'+str(i)+'_0.bcg bisimulator -branching -diag diag.bcg output_'+ident1+"-"+ident2+'_'+str(i)+'_1.bcg', shell=True)

                else:
                    call('bcg_io output_'+ident1+"-"+ident2+'_0_0.aut .bcg', shell=True)
                    call('bcg_io output_'+ident1+"-"+ident2+'_0_1.aut .bcg', shell=True)
                    res=call('bcg_open output_'+ident1+"-"+ident2+'_0_0.bcg bisimulator -branching -diag diag.bcg output_'+ident1+"-"+ident2+'_0_1.bcg', shell=True)

                clean()
