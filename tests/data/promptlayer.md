#  PromptLayer

This page covers how to use PromptLayer within LangChain. It is broken into two parts: installation and setup, and then references to specific PromptLayer
wrappers.

##  Installation and Setup  ​

If you want to work with PromptLayer:

  * Install the promptlayer python library ` pip install promptlayer `
  * Create a PromptLayer account 
  * Create an api token and set it as an environment variable ( ` PROMPTLAYER_API_KEY ` ) 

##  Wrappers  ​

###  LLM  ​

There exists an PromptLayer OpenAI LLM wrapper, which you can access with

    
    
    from langchain.llms import PromptLayerOpenAI  
    

To tag your requests, use the argument ` pl_tags ` when initializing the LLM

    
    
    from langchain.llms import PromptLayerOpenAI  
    llm = PromptLayerOpenAI(pl_tags=["langchain-requests", "chatbot"])  
    

To get the PromptLayer request id, use the argument ` return_pl_id ` when initializing the LLM

    
    
    from langchain.llms import PromptLayerOpenAI  
    llm = PromptLayerOpenAI(return_pl_id=True)  
    

This will add the PromptLayer request ID in the ` generation_info ` field of the ` Generation ` returned when using ` .generate ` or ` .agenerate `

For example:

    
    
    llm_results = llm.generate(["hello world"])  
    for res in llm_results.generations:  
        print("pl request id: ", res[0].generation_info["pl_request_id"])  
    

You can use the PromptLayer request ID to add a prompt, score, or other metadata to your request.  Read more about it here  .

This LLM is identical to the OpenAI LLM, except that

  * all your requests will be logged to your PromptLayer account 
  * you can add ` pl_tags ` when instantiating to tag your requests on PromptLayer 
  * you can add ` return_pl_id ` when instantiating to return a PromptLayer request id to use while tracking requests  . 

PromptLayer also provides native wrappers for  ` PromptLayerChatOpenAI ` and ` PromptLayerOpenAIChat `