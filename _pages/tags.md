---
layout: default
title: Tags
---

<article>

{% comment %} Collect all documents from all collections {% endcomment %}
{% assign all_documents = site.documents %}

{% comment %} Build a hash of tags to documents {% endcomment %}
{% assign all_tags = "" | split: "" %}
{% for doc in all_documents %}
  {% if doc.tags %}
    {% assign all_tags = all_tags | concat: doc.tags %}
  {% endif %}
{% endfor %}
{% assign unique_tags = all_tags | uniq | sort %}

{% comment %} Build tag groups {% endcomment %}
{% assign tag_groups = "" | split: "" %}
{% for tag_name in unique_tags %}
  {% assign tagged_docs = "" | split: "" %}
  {% for doc in all_documents %}
    {% if doc.tags contains tag_name %}
      {% assign tagged_docs = tagged_docs | push: doc %}
    {% endif %}
  {% endfor %}
  {% assign tag_group = tag_name | append: "|" | append: tagged_docs.size %}
  {% assign tag_groups = tag_groups | push: tag_group %}
{% endfor %}

<div>
  <ul class="flexbox mb3">
    {% for tag_name in unique_tags %}
      {% assign tag_count = 0 %}
      {% for doc in all_documents %}
        {% if doc.tags contains tag_name %}
          {% assign tag_count = tag_count | plus: 1 %}
        {% endif %}
      {% endfor %}

      <a href="#{{ tag_name | downcase }}" class="tag"><li>#{{ tag_name }} ({{ tag_count }})</li></a>
    {% endfor %}
  </ul>
</div>

{% for tag_name in unique_tags %}
  {% assign tagged_docs = "" | split: "" %}
  {% assign tag_count = 0 %}
  {% for doc in all_documents %}
    {% if doc.tags contains tag_name %}
      {% assign tagged_docs = tagged_docs | push: doc %}
      {% assign tag_count = tag_count | plus: 1 %}
    {% endif %}
  {% endfor %}

<a href="#{{ tag_name | downcase }}" class="list-cat-link border-top full-width">
  <span id="{{ tag_name | downcase }}" class="list-cat aligned">#{{ tag_name }} ({{ tag_count }})</span>
</a>

<div class="list-cat-container">
{% for doc in tagged_docs %}
  <div class="list-item truncate">
      <a class="list-link truncate" href="{{ doc.url }}">{% if doc.collection == 'reviews' %}Notes on <i>{% endif %}
      {{ doc.title | markdownify | remove: '<p>' | remove: '</p>' }}
      {% if doc.collection == 'reviews' %}</i>{% endif %}
      </a>
  </div>
{% endfor %}

</div>

{% endfor %}
</article>
