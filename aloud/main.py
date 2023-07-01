from pathlib import Path
import elevenlabs as xi
from langchain.document_loaders import WebBaseLoader


def main():
    xi.set_api_key(Path("~/.elevenlabs-token").expanduser().read_text().strip())
    url = "https://www.deconstructconf.com/blog/how-to-prepare-a-talk"
    loader = WebBaseLoader(url)
    data = loader.load()
    print(data)
    # audio = xi.generate(text="Hi! My name is Bella, nice to meet you!", voice="Bella", model="eleven_monolingual_v1")

    # xi.play(audio)


if __name__ == "__main__":
    main()
