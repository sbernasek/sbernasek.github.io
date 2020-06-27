---
layout: page
use-site-title: false
title: Software
bigimg:
 - "/img/site/triangulation.jpg" : "Triangulating R8 cells in the early fly eye"
---


The software projects detailed below were originally developed to support my own research endeavours. I've since packaged them for public distribution in order to ensure that my results remain reproducible and to facilitate new avenues for future research. I don't actively promote any of these, but if you have any questions or there are any additional features you'd like to see, please don't hesitate to contact me via github!


## FlyQMA

A python framework for automated mosaic analysis of Drosophila imaginal discs. Facilitates high-throughput segmentation, bleedthrough correction, and annotation of raw microscope images in order to accelerate experimental pipelines while increasing reproducibility.

<p class="aligncenter">
  <img src="/img/software/flyqma_pipeline.png" width="650px">
</p>

See the [Fly-QMA page](https://www.sbernasek.com/flyqma) for more info.

**Use cases:**\\
&#8226; Comparing Pnt-GFP expression between yan clones ([Figure 4](https://doi.org/10.1101/430744))


<br>
## FlyEye Analysis

A python platform for analyzing gene expression measurements obtained using FlyEye Silhouette. The main purpose of this package is to infer aggregate dynamic behavior by assigning a developmental age to each segmented nucleus using the approach described in our upcoming [paper](https://doi.org/10.1101/430744). The package also provides various spatial analysis, model fitting, and visualization methods useful for analyzing Silhouette data.

<p class="aligncenter">
  <img src="/img/software/flyeye.png" width="650px">
</p>

See the [FlyEye Analysis page](https://www.sbernasek.com/flyeye) for more info.

**Use cases:**\\
&#8226; Measuring Pnt-to-Yan ratio dynamics during retinal patterning ([Several figures](https://doi.org/10.1101/430744))\\
&#8226; Measuring the effect of miR-7 on Yan expression dynamics ([Figure 5](https://doi.org/10.1016/j.cell.2019.06.023))


<br>
## TF Binding

A python package for simulating the statistical mechanics of cooperative binding events between transcription factors and their target promoters. A recursive, cython-based implementation enables large-scale and highly parallelized enumeration of all possible microstates that would otherwise be computationally intractable. 

<p class="aligncenter">
  <img src="/img/software/tfbinding.png" width="650px">
</p>

Check out the [repo](https://github.com/sebastianbernasek/binding) for more info.

**Use cases:**\\
&#8226; Exploring Pnt/Yan competition for shared ETS binding sites ([Figure 3](https://doi.org/10.1101/430744))


<br>
## Gene SSA

A python framework for exact stochastic simulation of Markov processes, with a particular emphasis on gene regulatory networks. Leverages a cython backend to simulate large networks faster and more efficiently than all other open source tools I've come across. 

<p class="aligncenter">
  <img src="/img/software/genessa.png" width="650px">
</p>

Check out the [repo](https://github.com/sebastianbernasek/genessa) for more info.

**Use cases:**\\
&#8226; Surveying the influence of metabolism on GRN perturbation sensitivity ([Figure 4](https://doi.org/10.1016/j.cell.2019.06.023))\\
&#8226; Predicting Yan expression dynamics under miR-7 ablation ([Figure 5](https://doi.org/10.1016/j.cell.2019.06.023))

