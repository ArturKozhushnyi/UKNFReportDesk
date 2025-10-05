My AI workflow. 

I am using technique called "double prompting". Creating prompts with help of other LLMs. In my case I am using gemini Pro for creating prompts and claude-4.5-sonnet in cursor ai for executing prompts. My methodology is based on device and conquer, I devide big problem into smaller ones and with use of  "double prompting" it give a fruitful results. 

## Guide for **double prompting**

### Coding 

first of all creator of prompts and executor of prompts needs to have as much context as possible. Creator of prompts needs to have context to create very precise prompts, executor needs to have full context to correctly execute things. Mainly I check the created prompt, the correctness of prompt and how it logically connects to the system, checking prompt is much easier than checking full code for errors. After correct and precise prompt rate of error for execution prompts have fallen dramatically. Basically you as a user now talk directly only to prompt creator and executor only receives prompts that are explicit and well describe by prompt creator. 


### Small advice

We forced the models to speak in English because english has more data corpus which means that it has more data to work with in english than in any other language. 


### Testing 

With very precise prompts executor of prompts could generate very precise component tests. Which in turn we used to double check the correctness of generated code. This improved our code qualify and speed of development at the same time 


### Trasfer of context 

in case of cursor ai, it is done automatically to executor of prompts, for gemini Pro we used a lot of different tactics, from copy paste to pasting images of diagrams, I think the fastest way was by using existing functionality of gemini Pro that read github repository. 


### Documentation

We asked executor for very contextful explanation of each newly created feature, these features are in /docs file in our repo. It helped a lot to executor and prompt creator, because they could "refresh" their memories on features that they already created, which in turn helped increase the quality of code and precision of execution. 


### How to create prompt with help of prompt creator? 


To create effectively prompts with prompt creator it is a good practice to sometimes "refresh" memory when working with something, for e.g. when asking for prompt that creates new feature or new column in database, you can paste the definition of database (SQL script) into the chat to refresh memory. You can ask prompt creator to add files that executor should pay attention. Also with more features ask your creator and executor to analyze existing codebase, it yields more precision. 

Examples of such prompts


```
# codebase was attached
analyze the code, after analisys finish assignment


Create a prompt for cursor ai, that will create new migration script with 002 number as prefix. This migration script contains resource id and group, resource id is randomly generated (I will provide uuid for it) for each resource, one resource is for example one endpoint in this case like fetch user. Also in this migration script must be group called administrator, this group must be in resource allow list with all new created resources, create this prompt. The prompt should be runnable multiple times without adding new duplicate records

```


```
# context was previosly provided
Create a prompt that will create new endpoint that adds users to groups, this new endpoint needs to have administration group access.

This endpoint should also add new resource id and add this resource id to administrator group

Create prompt 
```

### Context Limits

When context limit is reach, there is not much we can do about it. Create new chat, but ask to reanalyze codebase before asking prompt creator anything. This works for executor too. 




