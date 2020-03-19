---
layout: page
title: Software
---

{% accordion software-accordion %}

  {% collapse Fly-QMA %}
  A python package for automated mosaic analysis of Drosophila imaginal discs. Facilitates high-throughput segmentation, bleedthrough correction, and annotation of raw microscope images in order to accelerate experimental pipelines while improving reproducibility. [[site](https://www.sbernasek.com/flyqma)][[code](https://github.com/sebastianbernasek/flyqma)]

      pip install flyqma

  {% endcollapse %}

  {% collapse FlyEye Analysis %}
  A python platform for analyzing gene expression measurements obtained using FlyEye Silhouette. Supports dynamic analysis, spatial analysis, model fitting, and visualization of the resultant trends. [[site](https://www.sbernasek.com/flyeye)][[code](https://github.com/sebastianbernasek/flyeye)]

      pip install flyeye

  {% endcollapse %}

  {% collapse TF-Binding %}
  A python package for simulating the statistical mechanics of cooperative binding events between transcription factors and their target promoters. A recursive, cython-based implementation enables large-scale and highly parallelized enumeration of all possible microstates that would otherwise be computationally intractable. [[code](https://github.com/sebastianbernasek/binding)]
  {% endcollapse %}

  {% collapse Gene SSA %}
  A python framework for exact stochastic simulation of Markov processes, with a particular emphasis on gene regulatory networks. Leverages a cython backend to simulate large networks faster and more efficiently than all other open source tools I've come across. [[code](https://github.com/sebastianbernasek/genessa)]
  {% endcollapse %}

{% endaccordion %}
