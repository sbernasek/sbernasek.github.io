---
layout: page
title: Hi. I'm Seb!
use-site-title: true
---

![Cover Photo](/img/cover.jpg){: .center-block :}

<!--
<p class="aligncenter">
  <img src="/img/cover.jpg" width="300px">
</p>
-->

My mission is to answer difficult questions by understanding and predicting the behavior of complex systems, both human-engineered and those found in the natural world. Which emerging energy technologies are most likely to perform at scale? Which athletes can we expect to enjoy successful careers? How do cells make reliable decisions? How do proteins coordinate consistent formation of the fruit fly eyeball? These questions and others like them aren't just fun to explore; they have the capacity to inform major decisions such as which R&D endeavors merit additional funding or which cancer mechanisms are ripe for therapeutic intervention. 

My expertise blends engineering insight with the computational and mathematical skills of a data scientist to seek answers. I build quantitative models subject to physical and thermodynamic constraints, then use them to analyze real data and predict real outcomes. I've modeled both steady state and dynamic processes across a broad range of physical scales, from stochastic molecular events within individual cells to industrial scale plant performance. I've scraped web pages to build empirical data sets, and collaborated with others to design controlled experiments in the lab or in the field. My efforts have informed major corporate decisions, generated patented technologies, and advanced basic understanding of fundamental biological processes. 

Moving forward, I'd like to continue developing my skills and deploying them to seek answers to questions that address problems I care about. Fortunately, I care about a lot of things so I shouldn't be bored any time soon. 


<!-- <div class="posts-list">
  {% for post in paginator.posts %}
  <article class="post-preview">
    <a href="{{ post.url | relative_url }}">
	  <h2 class="post-title">{{ post.title }}</h2>

	  {% if post.subtitle %}
	  <h3 class="post-subtitle">
	    {{ post.subtitle }}
	  </h3>
	  {% endif %}
    </a>

    <p class="post-meta">
      Posted on {{ post.date | date: site.date_format }}
    </p>

    <div class="post-entry-container">
      {% if post.image %}
      <div class="post-image">
        <a href="{{ post.url | relative_url }}">
          <img src="{{ post.image | relative_url }}">
        </a>
      </div>
      {% endif %}
      <div class="post-entry">
        {{ post.excerpt | strip_html | xml_escape | truncatewords: site.excerpt_length }}
        {% assign excerpt_word_count = post.excerpt | number_of_words %}
        {% if post.content != post.excerpt or excerpt_word_count > site.excerpt_length %}
          <a href="{{ post.url | relative_url }}" class="post-read-more">[Read&nbsp;More]</a>
        {% endif %}
      </div>
    </div>

    {% if post.tags.size > 0 %}
    <div class="blog-tags">
      Tags:
      {% if site.link-tags %}
      {% for tag in post.tags %}
      <a href="{{ '/tags' | relative_url }}#{{- tag -}}">{{- tag -}}</a>
      {% endfor %}
      {% else %}
        {{ post.tags | join: ", " }}
      {% endif %}
    </div>
    {% endif %}

   </article>
  {% endfor %}
</div>

{% if paginator.total_pages > 1 %}
<ul class="pager main-pager">
  {% if paginator.previous_page %}
  <li class="previous">
    <a href="{{ paginator.previous_page_path | relative_url }}">&larr; Newer Posts</a>
  </li>
  {% endif %}
  {% if paginator.next_page %}
  <li class="next">
    <a href="{{ paginator.next_page_path | relative_url }}">Older Posts &rarr;</a>
  </li>
  {% endif %}
</ul>
{% endif %}
-->
