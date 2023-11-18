import textwrap

from openai import OpenAI

ARTICLE_URL = "https://www.kpassa.me/posts/google"


def test_something(get_markdown):
    markdown = get_markdown(ARTICLE_URL)
    oai = OpenAI()
    prompt = textwrap.dedent("""
    You are given a markdown representation of an article from the internet.
    
    Convert it such that it is a 100% textual representation of the article, which can be read out loud by a human to a colleague, and the colleague will understand what the markdown formatting typically tries to convey, namely, the hierarchy of the document (subtitles inside titles inside sections, etc).
    
    Don't modify the actual text of the article. Only deal with the structure.
    
    The article's markdown representation is:
    ```md
    {markdown}
    ```
    """).format(markdown=markdown).strip()
    chat_completion = oai.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model="gpt-4-1106-preview"
    )
    result = chat_completion.choices[0].message.content
    print(result)
