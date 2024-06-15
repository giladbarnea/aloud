from __future__ import annotations

from collections.abc import Sequence
from enum import Enum
from typing import Annotated, Literal

from pydantic import AnyUrl, BaseModel, ConfigDict, Field, RootModel


class SystemMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: Annotated[str, Field(description='The contents of the system message.')]
    role: Annotated[Literal['system'], Field(description='The role of the messages author, in this case `system`.')]
    name: Annotated[
        str | None,
        Field(
            None,
            description='An optional name for the participant. Provides the model information to differentiate between participants of the same role.',
        ),
    ]
    type = property(lambda self: self.role)


class ImageDetail(Enum):
    """
    Specifies the detail level of the image. Learn more in the [Vision guide](/docs/guides/vision/low-or-high-fidelity-image-understanding).
    """

    auto = 'auto'
    low = 'low'
    high = 'high'


class ImageUrl(BaseModel):
    model_config = ConfigDict(frozen=True)
    url: Annotated[AnyUrl, Field(description='Either a URL of the image or the base64 encoded image data.')]
    detail: Annotated[
        ImageDetail,
        Field(
            'auto',
            description='Specifies the detail level of the image. Learn more in the [Vision guide](/docs/guides/vision/low-or-high-fidelity-image-understanding).',
        ),
    ]


class ImageContentPart(BaseModel):
    model_config = ConfigDict(frozen=True)
    type: Annotated[Literal['image_url'], Field(description='The type of the content part.')]
    image_url: ImageUrl


class TextContentPart(BaseModel):
    model_config = ConfigDict(frozen=True)
    type: Annotated[Literal['text'], Field(description='The type of the content part.')]
    text: Annotated[str, Field(description='The text content.')]


class ArrayOfContentParts(RootModel[Sequence[ImageContentPart | TextContentPart]]):
    model_config = ConfigDict(frozen=True)
    root: Annotated[
        Sequence[ImageContentPart | TextContentPart],
        Field(
            description='An array of content parts with a defined type, each can be of type `text` or `image_url` when passing in images. You can pass multiple images by adding multiple `image_url` content parts. Image input is only supported when using the `gpt-4-visual-preview` model.',
            min_length=1,
            title='Array of content parts',
        ),
    ]


class UserMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    content: Annotated[str | ArrayOfContentParts, Field(description='The contents of the user message.\n')]
    role: Annotated[Literal['user'], Field(description='The role of the messages author, in this case `user`.')]
    name: Annotated[
        str | None,
        Field(
            None,
            description='An optional name for the participant. Provides the model information to differentiate between participants of the same role.',
        ),
    ]


class ToolMessage(BaseModel):
    model_config = ConfigDict(frozen=True)
    role: Annotated[Literal['tool'], Field(description='The role of the messages author, in this case `tool`.')]
    content: Annotated[str, Field(description='The contents of the tool message.')]
    tool_call_id: Annotated[str, Field(description='Tool call that this message is responding to.')]


class Chat(BaseModel):
    model_config = ConfigDict(frozen=True)
    messages: Annotated[
        Sequence[SystemMessage | UserMessage | ToolMessage] | None,
        Field(
            None,
            description='A list of messages comprising the conversation so far. [Example Python code](https://cookbook.openai.com/examples/how_to_format_inputs_to_chatgpt_models).',
            min_length=1,
        ),
    ]
