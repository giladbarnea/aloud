import json

from aloud.console import console
from aloud.convert.to_markdown import prompts
from aloud.oai import oai
from aloud.text import remove_lines_after, remove_lines_until
from aloud.thread_pool_executor import ThreadPoolExecutor


def find_real_article_boundaries(markdown: str) -> tuple[str, str, str]:
    with ThreadPoolExecutor(max_workers=3) as executor:
        first_real_article_line_future = executor.submit(find_first_real_article_line, markdown)
        first_post_title_line_future = executor.submit(find_first_post_title_line, markdown)
        last_real_article_line_future = executor.submit(find_last_real_article_line, markdown)
    first_real_article_line = first_real_article_line_future.result()
    first_post_title_line = first_post_title_line_future.result()
    last_real_article_line = last_real_article_line_future.result()
    return first_real_article_line, first_post_title_line, last_real_article_line


def find_first_real_article_line(markdown: str) -> str:
    template = prompts.get('find_first_real_article_line')
    prompt_value = template.format_prompt(markdown=markdown)
    chat_completion = oai.chat.call(
        prompt_value,
        timeout=10,
    )
    first_real_article_line = chat_completion.content.splitlines()[0]
    console.log('find_first_real_article_line: %r', first_real_article_line)
    return first_real_article_line


def find_first_post_title_line(markdown: str) -> str:
    template = prompts.get('find_first_post_title_line')
    prompt_value = template.format_prompt(markdown=markdown)
    chat_completion = oai.chat.call(
        prompt_value,
        timeout=10,
    )
    last_real_article_line = chat_completion.content.splitlines()[0]
    console.log('find_first_post_title_line: %r', last_real_article_line)
    return last_real_article_line


def find_last_real_article_line(markdown: str) -> str:
    # prompt = textwrap.dedent(
    #     """
    #         You are given a markdown representation of an article from the internet, generated automatically by a tool. This means that the markdown is not perfect.
    #         Often, at the bottom of the article, the article's real actual content would end, and after that, things that used to be the website's comment section, social media links, navigation elements and buttons would appear. Those elements are called "junk elements".
    #         What line concludes the real article, excluding the "junk elements"?
    #         """,
    # ).strip()
    # chat_completion = oai.chat.call(
    #     messages=[{'role': 'system', 'content': prompt}, {'role': 'user', 'content': markdown}],
    #     tool_choice='required',
    #     tools=[
    #         {
    #             'type': 'function',
    #             'function': {
    #                 'name': 'find_last_real_article_line',
    #                 'description': 'Extract the last real article line from the markdown.',
    #                 'parameters': {
    #                     'type': 'object',
    #                     'properties': {
    #                         'line': {
    #                             'type': 'string',
    #                             'description': 'The real article line.',
    #                         },
    #                     },
    #                     'required': ['line'],
    #                 },
    #             },
    #         },
    #     ],
    #     timeout=10,
    # )
    template = prompts.get('find_last_real_article_line')
    prompt_value = template.format_prompt(markdown=markdown)
    chat_completion = oai.chat.call(
        prompt_value,
        timeout=10,
    )
    last_real_article_line = json.loads(chat_completion.tool_calls[0].function.arguments)['line']
    # content = chat_completion.content
    # last_real_article_line = content.splitlines()[0]
    console.log('find_last_real_article_line: %r', last_real_article_line)
    return last_real_article_line


def trim_junk_sections(
    raw_markdown: str,
    first_real_article_line: str,
    first_post_title_line: str,
    last_real_article_line: str,
) -> str:
    clean_markdown = remove_lines_until(raw_markdown, first_real_article_line)
    clean_markdown = remove_lines_until(clean_markdown, first_post_title_line)
    clean_markdown = remove_lines_after(clean_markdown, last_real_article_line)
    clean_markdown = clean_markdown.strip()
    return clean_markdown
