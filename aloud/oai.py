from collections.abc import Mapping
from typing import cast

import httpx
from httpx import Timeout
from openai import DEFAULT_MAX_RETRIES, NOT_GIVEN, NotGiven, Stream
from openai import OpenAI as _OpenAI
from openai.resources import Chat as _ChatResource
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionChunk,
    ChatCompletionMessage,
)

CHAT_COMPLETION_CREATE_DEFAULTS = {
    'temperature': 0,
    'model': 'gpt-4o',
}


class ChatCompletionMessageHybrid(ChatCompletion, ChatCompletionMessage):
    pass


class ChatCompletionChunkHybrid(ChatCompletion, ChatCompletionChunk):
    pass


class ChatResource(_ChatResource):
    def call(self, *args, **kwargs) -> ChatCompletionMessageHybrid:
        if 'stream' in kwargs:
            raise ValueError('stream is not allowed in ChatResource.call')
        completions = self.completions.create(*args, **CHAT_COMPLETION_CREATE_DEFAULTS, **kwargs, stream=False)
        message = completions.choices[0].message
        return ChatCompletionMessageHybrid(
            **{
                **vars(completions),
                **vars(message),
            },
        )

    def stream(self, *args, **kwargs) -> Stream[ChatCompletionChunkHybrid]:
        if 'stream' in kwargs:
            raise ValueError('stream is not allowed in ChatResource.stream')
        completions = self.completions.create(*args, **CHAT_COMPLETION_CREATE_DEFAULTS, **kwargs, stream=True)
        completions = cast(Stream[ChatCompletion], completions)
        for completion in completions:
            message = completion.choices[0].message
            yield ChatCompletionChunkHybrid(
                **{
                    **vars(completion),
                    **vars(message),
                },
            )


class OpenAI(_OpenAI):
    chat: ChatResource

    def __init__(
        self,
        *,
        api_key: str | None = None,
        organization: str | None = None,
        project: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        http_client: httpx.Client | None = None,
        _strict_response_validation: bool = False,
    ) -> None:
        super().__init__(
            api_key=api_key,
            organization=organization,
            project=project,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            default_query=default_query,
            http_client=http_client,
            _strict_response_validation=_strict_response_validation,
        )
        self.chat = ChatResource(self)


oai = OpenAI()
