def test_interconnects_q_star():
    article_url = "https://www.interconnects.ai/p/q-star"
    from aloud.main import process

    speakable: bytes = process(article_url, only_speakable=True)
    audio = process(speakable.decode(), only_audio=True)
