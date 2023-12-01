# The Q* hypothesis: Tree-of-thoughts reasoning, process reward models, and supercharging synthetic data

### Emergency special: The information we need to understand what Q* is was right in front of us, but the memes are more fun than reality.

Nathan Lambert

Nov 24, 2023

#### The Q* hypothesis: Tree-of-thoughts reasoning, process reward models, and supercharging synthetic data

_Programming note: this counts as next week’s post. I pulled it forward for timeliness, as RLAIF and process reward
models were on my hit list anyway. We’ll see if there are more_ _emergency posts._

* * *

On Wednesday, right when we were all ready to sign off for Thanksgiving, Reuters reported on OpenAI one last time ,
revealing just the name and high-level evaluations of a new OpenAI method, Q*, touted with vague powerful capabilities:

> After being contacted by Reuters, OpenAI, which declined to comment, acknowledged in an internal message to staffers a
project called Q*…
>
> Some at OpenAI believe Q* (pronounced Q-Star) could be a breakthrough in the startup's search for what's known as
artificial general intelligence (AGI), one of the people told Reuters. OpenAI defines AGI as autonomous systems that
surpass humans in most economically valuable tasks.
>
> Given vast computing resources, the new model was able to solve certain mathematical problems, the person said on
condition of anonymity because the individual was not authorized to speak on behalf of the company. Though only
performing math on the level of grade-school students, acing such tests made researchers very optimistic about Q*’s
future success, the source said.

Such extensive speculation has never unfolded from only the name of a method. Though, the name is pretty simple in this
case, and not just another codename from the Dune universe . Q* (Q-Star), if real, clearly links two core themes from
the RL literature: Q-values and A* _, a classic graph search algorithm. Yes, there’s an argument that Q_ could just
refer to the value function of the optimal policy, but this would need to be a fabricated leak for it to be so silly,
and OpenAI has pretty much had everything leaked, so fabricating them seems unlikely. 1

My initial hypothesis, which I clearly labeled as a tin hat theory, was a vague merging of Q-learning and A* search.
What I didn’t answer is, what is being searched over? My initial guess of searching over dialogue turns is almost
certainly wrong due to infrastructure reasons I’ll touch on later.

As I’ve dug into this in more detail, I’ve become convinced that they are doing something powerful by **searching over
language/reasoning steps via tree-of-thoughts reasoning** , but it is much smaller of a leap than people believe. The
reason for the hyperbole is the goal of linking large language model training and usage to the core components of Deep
RL that enabled success like AlphaGo: self-play and look-ahead planning.

* **Self-play** is the idea that an agent can improve its gameplay by playing against slightly different versions of
  itself because it’ll progressively encounter more challenging situations. In the space of LLMs, it is almost certain
  that the largest portion of self-play will look like AI Feedback rather than competitive processes.

* **Look-ahead planning** is the idea of using a model of the world to reason into the future and produce better actions
  or outputs. The two variants are based on Model Predictive Control (MPC), which is often used on continuous states,
  and Monte-Carlo Tree Search (MCTS), which works with discrete actions and states.

To understand how this links together, we need to cover recent results published from OpenAI and others that’ll answer
two questions:

1. How do we construct a representation of language that we can search over?

2. How do we construct a notion of value over compartmentalized and meaningful language chunks (rather than the entire
   completion)?

With answers to these, it should be clear how we could use existing RL methods that are used for RLHF. We use an RL
optimizer to fine-tune the language model and get higher-quality generations with modular rewards (rather than the full
sequence, as is done today).

![Runway 2023-11-23T16\\_55\\_51.562Z Expand Image.jpeg](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F77dd8242-6d53-4f2c-a401-243aa58019e3_1820x1024.jpeg)

DALLE3

### Modular reasoning with LLMs: Tree-of-Thoughts (ToT) prompting

Promoting techniques like “take a deep breath” and “think step by step” are now expanding into advanced methods for
inference with parallel computation and heuristics (some fundamentals of search).

Tree-of-thoughts is really how it sounds. It is a way to prompt a language model to create a tree of reasoning paths
that may or may not converge at a correct answer. A comparison to other ways of problem-solving with LLMs was shown in
the paper:

![Image.png](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F86601708-3c01-43ee-b196-9f227e1eb983_1582x842.png)

The innovations that make this click are the chunking of reasoning steps and prompting a model to create new reasoning
steps. **ToT seems like the first “recursive” prompting technique for improving inference performance** , which sounds
remarkably close to the AI Safety concern of recursively self-improving models (though I am not an expert).

With the reasoning trees, different methods can be applied to score each vertex (the nodes) or to sample the final path.
It can be based on things like minimum length to the most agreed answer, or complex things that require external
feedback, which points us back in the direction of RLHF.

Read the Tree of Thoughts paper here: https://arxiv.org/abs/2305.10601

### Fine-grained reward labels in generation: Process Reward Models (PRM)

The way that most RLHF is done to date has the entire response from a language model get an associated score. To anyone
with an RL background, this is disappointing, because it limits the ability for RL methods to make connections about the
value of each sub-component of text. Futures have been pointed to where this multi-step optimization comes at the level
of multiple dialogue turns, but that is still far-fetched due to the requirement of having humans or some prompt source
in the loop.

This could easily be extended to a self-play style dialogue but is hard to give an LLMs goals that translate to the
self-play dynamics of consistently improving. Most of the things we want to do with LLMs are repetitive tasks without
near-infinite ceilings on performance like the game of Go.

On the other hand, **there is a type of LLM use case that naturally abstracts to contained chunks of text: step-by-step
reasoning** , best exemplified by math problems.

Process Reward Models (PRMs) have been a topic I’ve heard a lot about from RLHF folks off the record for the last 6
months. It turns out there is a lot of literature on these models, but very little on how to use them with RL.

The core idea of a PRM is to assign a score to each step of reasoning, rather than a complete message. An example from
the OpenAI paper Let’s Verify Step by Step is shown below:

![Image.png](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2Fa9eaa85b-db2e-4b79-8879-ee88c13e4b78_1614x1164.png)

And the funny feedback interface they used (which will be replaced by AIs), but is instructive:

![Screenshot 2023-11-23 at 3.48.54 PM.png](https://substackcdn.com/image/fetch/w_1456,c_limit,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F6f4e5bd9-0d69-421b-a841-f09d95ad9004_1454x756.png)

This allows finer-tuned generation with reasoning problems, by sampling over the maximum average reward or other
metrics, instead of just relying on one score (standard RMs are called outcome RMs in this literature). Using Best-of-N
sampling , essentially generating a bunch of times and using the one that scored the highest by the reward model (the
inference time cousin of Rejection Sampling popularized with Llama 2), PRMs outperform standard RMs on reasoning tasks.

To date, most of the resources for PRMs just show how to use them at inference time. The true power will come when this
signal is optimized against training. To create the richest optimization setting, having the ability to generate diverse
reasoning pathways for scoring and learning from is essential. This is where Tree-of-Thoughts comes in. **The prompting
from ToT gives diversity to the generations, which a policy can learn to exploit with access to a PRM** .

For more resources on PRMs, see the following:

* _ Let’s Verify Step by Step _ : a good introduction to PRMs.

* _ Solving math word problems with process- and outcome-based feedback _ : the canonical citation in all PRM and
  reasoning works in 2023.

* _ Scaling Relationship on Learning Mathematical Reasoning with Large Language Models _ : A paper that studies the
  method of rejection sampling for reasoning problems, among other contributions.

* _ Let's reward step by step: Step-Level reward model as the Navigators for Reasoning _

Additionally, there’s one popular openly available math model that is documented as training with PRMs: Wizard-LM-Math .
Second, OpenAI released their fine-grained reward labels from the Verify Step by Step paper for training a PRM earlier
this year.

* * *

🧪🎙️ Tom and I discussed Q* and all of the OpenAI drama on this week’s episode of The Retort , check it out!

* * *

### Putting it together: what Q* could be

Q* seems to be using PRMs to score Tree of Thoughts reasoning data that then is optimized with Offline RL. This wouldn’t
look too different from existing RLHF toolings that use offline algorithms like DPO or ILQL that do not need to generate
from the LLM during training. The ‘trajectory’ seen by the RL algorithm is the sequence of reasoning steps, so we’re
finally doing RLHF in a multi-step fashion rather than contextual bandits!

Given that the rumors I’ve heard already indicated OpenAI was using offline RL for RLHF (which doesn’t say that much),
this doesn’t seem like a big leap to me. The intricacies of this method involve collecting the right prompts, having a
model to generate great reasoning steps, and most importantly: accurately scoring tens of thousands of completions.

**This last step is where the rumored “vast computing resources”: use AI to label every step with a score instead of
humans** . Synthetic data is king, and with trees rather than single-width paths (via chain-of-thought) giving more and
more options later on to arrive at the right answer.

The ton of compute resources tracks with the rumor that I’ve heard one or more of the big tech players (Google,
Anthropic, Cohere, etc) are creating a pretraining-sized dataset from process supervision or RLAIF-like methods, which
would take 10s of thousands of GPU hours easily. The gap to openly available models in this area worries me.

All of this said while the core ideas seem clear to me, implementing this takes levels of model whispering few poses.
Distribution control, massive inference, and RL finickiness are well beyond my knowledge or experience. All of this
information just seems so natural. All the evaluations for ToT and PRMs are on reasoning problems like math, which is
what all the news articles were saying this leaked method was about. Even if it isn’t Q*, it would be a fun experiment.

### Super-scale AI feedback data and the future

As I’ve written about before, AI Feedback and Constitutional AI are underrepresented in public awareness . Synthetic
data represents the shortest path to expanding datasets. In the short term, it’s clear we can create some useful data
with this. What is not clear is the extent to which it can be scaled — ie can it replace internet scale data entirely?
