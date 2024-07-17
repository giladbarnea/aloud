from aloud.vision import _generate_image_description


def test_generate_image_description():
    image_url = (
        'https://substack-post-media.s3.amazonaws.com/public/images/98f562a1-ece9-4e31-bafd-363da13fa741_667x571.png'
    )
    image_description = _generate_image_description(image_url)
    assert image_description
