from langchain.document_loaders import WebBaseLoader, BSHTMLLoader
import requests


def test_loads_fine():
    url = "https://github.blog/2023-02-06-the-technology-behind-githubs-new-code-search/"
    loader = WebBaseLoader(url)
    doc = loader.load()[0]
    assert "The technology behind GitHub’s new code search | The GitHub Blog" in doc.page_content


def test_foo(tmp_path):
    url = "https://github.blog/2023-02-06-the-technology-behind-githubs-new-code-search/"
    req = requests.get(url)
    html_path = tmp_path / "foo.html"
    with html_path.open("w") as f:
        f.write(req.text)
    loader = BSHTMLLoader(str(html_path))
    doc = loader.load()[0]
    print()
