def test_introducing_byfrost_a_source_code_path_visualizer():
    article_url = 'https://itnext.io/introducing-byfrost-a-source-code-path-visualizer-2d64002d1f9a'
    from aloud.main import process

    speakable: bytes = process(article_url, only_speakable=True)
    audio = process(speakable.decode(), only_audio=True)
