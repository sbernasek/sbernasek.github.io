---
layout: page
title: Research Projects
---

My primary field is computational biology; I synthesize concepts from chemical engineering and computer science to study how cells make decisions. As a graduate student, I was particularly focused on exploring the chemical mechanisms that guide cells to adopt the appropriate roles and functions during the formation of complex organs.

Despite the subject matter, my role is akin to that of a modern data scientist. I combine computer vision, mathematical modeling, statistics, and dynamical systems theory to develop new analytical methods and derive meaning from experimental data. Common themes include:

- Development & validation of toy models
- Process dynamics & stochasticity
- Time series analysis
- Analysis of heterogeneous behavior
- Quantitative microscopy

Check out the sections below for an introduction to some of my past projects, and please don't hesitate to contact me with any ideas, suggestions, or questions!


### Redundancy in gene regulatory networks

During the development of complex organisms, gene regulatory networks integrate external signals to ensure the timely execution of downstream events. These networks exhibit extensive functional redundancy, enabling cells to partially compensate for deleterious mutations. I sought to elucidate evolutionary forces shaping these topologies by identifying additional benefits that redundant regulatory mechanisms confer upon heterogeneous populations of organisms. My collaborators and I coupled model-based predictions with experimental validation in model organisms in an effort to generate and test new hypotheses. We showed that redundant regulatory mechanisms enable faster rates of growth and development by safeguarding against excessive protein expression when metabolic rates are high.

The [study](https://doi.org/10.1016/j.cell.2019.06.023) was published in *Cell*.


### Automated analysis of mosaic tissues

Biologists use mosaic tissues to compare the behavior of genetically distinct cells within an otherwise equivalent context. The ensuing analysis is often limited to qualitative insight. However, it is becoming clear that quantitative models are needed to unravel the complexities of many biological systems. I developed a computational framework that automates the quantification of mosaic analysis for *Drosophila* imaginal discs, a common setting for studies of developmental processes. The software extracts quantitative measurements from confocal images of mosaic tissues, rectifies any cross-talk between fluorescent reporters, and identifies clonally-related subpopulations of cells. Together, these functions allow users to rigorously ascribe changes in gene expression to the presence or absence of particular genes.

The [manuscript](https://doi.org/10.1101/775783) is scheduled for publication in Spring 2020.


### Cellular decisions in the developing eye

Transcription factors coordinate the timing and execution of cell differentiation by tuning the expression of target genes. Some transcription factors promote differentiation, while others impede it. Competing transcription factors are often co-expressed *in vivo*, and it remains unclear how cells reliably integrate their antagonistic inputs. I developed and deployed computer vision techniques to infer the expression dynamics of competing transcription factors from confocal microscope images of the developing fruit fly eye. Combined with an experimental pipeline developed by my experimental collaborators, my approach facilitates quantitative modeling and characterization of transcription factor activity both before, during, and after differentiation.

Check out a [preprint](https://doi.org/10.1101/430744) of our manuscript.
