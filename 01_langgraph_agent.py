# Databricks notebook source
# MAGIC %md
# MAGIC # Agent Code
# MAGIC Modify this code and then run `02_evaluate_&_deploy` to test

# COMMAND ----------

import yaml
import mlflow
langgraph_config = mlflow.models.ModelConfig(development_config="agent_config.yaml")

# COMMAND ----------

#initialize openai model config
open_ai_model_name = langgraph_config.get("open_ai_config")["model_name"]
open_ai_model_parameters = langgraph_config.get("open_ai_config")["llm_parameters"]

# COMMAND ----------

import os

# Set up Openi AI model
from dotenv import load_dotenv
from langchain_databricks import ChatDatabricks
llm = ChatDatabricks(endpoint=open_ai_model_name, temperature=open_ai_model_parameters["temperature"])

# COMMAND ----------

from typing import Annotated

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict, Dict, Union
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from mlflow.langchain.output_parsers import ChatCompletionsOutputParser


class State(TypedDict):
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)


tool = TavilySearchResults(max_results=2)
tools = [tool]
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatbot")
graph_builder.set_entry_point("chatbot")
graph = graph_builder.compile()

# COMMAND ----------

def get_final_message(response):
  try:
    final_response = response["messages"][-1].content
    return final_response
  except:
    try:
      final_response = response["chatbot"]["messages"][-1].content #handle streaming responses
      return final_response
    except Exception as e:
      return f"Error parsing output: {e} \n\n Full output:" + str(response)

# COMMAND ----------

import mlflow
graph_agent = graph | RunnableLambda(get_final_message) | StrOutputParser()
mlflow.models.set_model(graph_agent)
