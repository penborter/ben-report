---
layout: default
title: Tags
---

<article>

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

<a href="#{{ t | downcase }}" class="list-cat-link border-top full-width">
  <span id="{{ t | downcase }}" class="list-cat aligned">#{{ t }} ({{ posts.size }})</span>
</a>

<div class="list-cat-container">
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
