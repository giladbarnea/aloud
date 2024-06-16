# `aloud`

## What is `aloud`?
`aloud` converts articles, academic PDFs, code documentation, and other rich content into legible and compelling speech.

It's designed to sound like a colleague professionally reading the text to you, rather than a robot spelling it out
verbatim.

It's in early development, but if it's interesting to you, watch for version 1.0, which will be fully functional.

## Why?

There's just too many articles and papers out there.

I can't read them all, but I can listen to them all while housekeeping, dogwalking and commuting.

## The problem with existing solutions

1. They ignore the structure and graphics of the text. `aloud` effectively communicates code blocks, images, diagrams,
   quotes, heading levels, and all the information that's you would get from LOOKING at the text.
2. The rhetoric and tonality they provide is typically dull and non-engaging. This hurts comprehension and retention so
   much that it's usually a waste of time.

## Communicating structure and graphics

### For a given code block:

```python
def get_weather(city: str) -> float:
    return weather_api.get_temperature(city)
```

`aloud` would say:

```
There's a code block here that defines a function 'get_weather'.
It takes a 'city' argument and returns a 'temperature' float. 
It uses the 'weather_api' module to get the temperature.
```

One could argue that this is more informative than:

```
def get weather parentheses city colon string arrow float:
    ...
```

### For images and diagrams, `aloud` uses a vision LLM to describe the image,

and then reads that out:
      
      There's a flowchart here that shows the high-level flow of getting weather data from the weather API.

### Headings are conveyed by simply saying:

```python
...text concluding the previous section.

New section: {big heading text}; Paragraph title: {smaller heading text}
```

### Quote blocks are declaredliterally before reading a quote, and callouts are preceded by a "Now this is important:", etc.

## Achieving engaging tonality
State-of-the-art voice LLMs, like GPT-4o, are used.

It seems that these are simply too expensive for existing startups to use at scale.

## `aloud` is in pre-alpha. Version 1.0 will be robust and holistic.
