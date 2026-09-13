---
title: "Publications"
permalink: /publications/
author_profile: true
---

{% assign all_pubs = site.publications | sort: 'date' | reverse %}
{% assign current_group = "" %}

{% for post in all_pubs %}
  {% assign y = post.date | date: "%Y" %}
  {% if y < "2017" %}
    {% assign group = "Before 2017" %}
  {% else %}
    {% assign group = y %}
  {% endif %}

  {% if group != current_group %}
    {% assign current_group = group %}

## {{ group }}
  {% endif %}

- **{{ post.title }}**  
  {{ post.citation }}
{% endfor %}