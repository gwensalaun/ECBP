
Efficient Comparison of BPMN Processes
==============================

This tool automatically compares two BPMN processes from a semantic point of view. In order to compute this comparison efficiently, it works by detecting the syntactic differences between the two processes, and then compares the semantic models (Labelled Transition Systems) of both processes only for these differences. This procedure thus avoids the comparison of the entire semantic models, which may be very costly. The semantic comparison is achieved using existing behavioural equivalences and bisimulations.


Required Software
=======================================

* [CADP](https://cadp.inria.fr/)
* [Maude](https://maude.cs.illinois.edu/wiki/The_Maude_System)
* [Python3](https://www.python.org/)


Usage
=======================================

Move to the main directory, and use the following command:

$ python3 compare.py ex1.bpmn ex2.bpmn box|full

where

- ex1.bpmn and ex2.bpmn are BPMN processes in BPMN2 XML
- box or full are options, box implements the matching algorithm whereas full implies the generation and comparison of the entire semantic models


Contributors
=====================================

* [Francisco Durán](http://www.lcc.uma.es/~duran/)
* [Gwen Salaün](http://convecs.inria.fr/people/Gwen.Salaun/)


License
=============================
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE.md)
