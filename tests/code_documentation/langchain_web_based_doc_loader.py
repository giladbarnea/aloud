from pathlib import Path

from langchain.document_loaders import BSHTMLLoader, WebBaseLoader, tomarkdown

ARTICLE_URL: str = "https://python.langchain.com/docs/modules/data_connection/document_loaders/integrations/web_base"


def test_loads_fine():
    loader = WebBaseLoader(ARTICLE_URL)
    doc = loader.load()[0]
    assert (
        "This covers how to use WebBaseLoader to load all text from HTML webpages into a document format that we can"
        " use downstream. For more custom logic for loading webpages look at some child class examples such as"
        " IMSDbLoader, AZLyricsLoader, and CollegeConfidentialLoader"
        in doc.page_content
    )
    assert "Loading multiple webpages" in doc.page_content
    assert '"https://www.walmart.com/search?q=parrots"' in doc.page_content


def test_converts_to_markdown():
    loader = tomarkdown.ToMarkdownLoader(ARTICLE_URL, api_key=Path("~/.2markdown").expanduser().read_text().strip())
    doc = loader.load()[0]
    print(doc)
