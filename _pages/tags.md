---
layout: default
title: Tags
---

{% include navigation.html %}

<article>
<h1>Tags</h1>

{% assign sorted_tags = site.tags | sort %}

<div>
  <ul class="flexbox mb3">
    {% for tag in sorted_tags %}
      {% assign t = tag | first %}
      {% assign posts = tag | last %}

      <a href="#{{ t | downcase }}" class="tag"><li>#{{ t }} ({{ posts.size }})</li></a>
    {% endfor %}
  </ul>
</div>

{% for tag in sorted_tags %}
  {% assign t = tag | first %}
  {% assign posts = tag | last %}

<a href="#{{ t | downcase }}" class="list-cat-link">
  <span id="{{ t | downcase }}" class="list-cat top-u1">#{{ t }} ({{ posts.size }})</span>
</a>

<div class="list-cat-container border-top top-u2">
{% for post in posts %}
  {% if post.tags contains t %}

  <div class="list-item truncate">
      <a class="list-link truncate" href="{{ post.url }}">{{ post.title | markdownify | remove: '<p>' | remove: '</p>' }}</a>
  </div>
  {% endif %}
{% endfor %}

</div>

{% endfor %}
</article>
