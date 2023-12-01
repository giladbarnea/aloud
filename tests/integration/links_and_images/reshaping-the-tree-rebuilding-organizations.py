def test_reshaping_the_tree_rebuilding_organizations():
    article_url = 'https://www.oneusefulthing.org/p/reshaping-the-tree-rebuilding-organizations'
    from aloud.main import process

    speakable: bytes = process(article_url, only_speakable=True)
    audio = process(speakable.decode(), only_audio=True)
