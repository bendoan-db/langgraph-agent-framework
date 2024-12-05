# Databricks notebook source
# MAGIC %pip install -U -q -r requirements.txt

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import mlflow
print(mlflow.__version__)

# COMMAND ----------

import os
from dbruntime.databricks_repl_context import get_context

os.environ["DATABRICKS_TOKEN"] = dbutils.secrets.get(scope="doan-demos", key="agent-token")
os.environ["DATABRICKS_HOST"] = "https://"+get_context().browserHostName
os.environ["DATABRICKS_HTTP_PATH"] = get_context().apiUrl

#pass in your tavily key, either as plain text or as a databricks secret: https://docs.databricks.com/en/security/secrets/index.html
os.environ["TAVILY_API_KEY"] = dbutils.secrets.get(scope="doan-demos", key="tavily")

# COMMAND ----------

print(os.environ["DATABRICKS_HOST"])
print(os.environ["DATABRICKS_HTTP_PATH"])

# COMMAND ----------

# MAGIC %md
# MAGIC # Agent Developement
# MAGIC Modify `01_langgraph_agent` to make changes to your agent. Then run the cells below to test the new agent on a single question or on an evaluation dataset

# COMMAND ----------

import yaml
with open("agent_config.yaml", "r") as file:
    langgraph_config = yaml.safe_load(file)

# COMMAND ----------

# MAGIC %run ./01_langgraph_agent

# COMMAND ----------

from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))

# COMMAND ----------

#test on single question
input_example = {
    "messages": [
        {
            "role": "user",
            "content": "Who currently has the most wins in F1 history?"
        }
    ]
}

response = graph_agent.invoke(input_example)

# COMMAND ----------

response

# COMMAND ----------

# MAGIC %md 
# MAGIC # Log Model to MLflow

# COMMAND ----------

# Log the model to MLflow
import os
import mlflow
from mlflow.models import infer_signature
from databricks.sdk import WorkspaceClient
from mlflow.models import infer_signature
from mlflow.models.resources import (
    DatabricksFunction,
    DatabricksServingEndpoint,
    DatabricksSQLWarehouse,
    DatabricksVectorSearchIndex,
)


model_signature = infer_signature(input_example, response)
w = WorkspaceClient()

config_path = os.path.join(os.getcwd(), "agent_config.yaml")
lc_model_path = os.path.join(os.getcwd(), '01_langgraph_agent')
requirements_path = os.path.join(os.getcwd(), "requirements.txt")

#log langgraph agent
with mlflow.start_run(run_name="tavily-langgraph"):
    logged_agent_info = mlflow.langchain.log_model(
        lc_model=lc_model_path,
        model_config=config_path,
        artifact_path='agent',
        pip_requirements = [f"-r {requirements_path}"],
        resources = [
            DatabricksServingEndpoint(endpoint_name="ASK-BEFORE-USING-doan-gpt-4o")
        ],
        input_example=input_example,
        signature=model_signature
    )
print(logged_agent_info.run_id)

# COMMAND ----------

# MAGIC %md
# MAGIC # Evaluate Agent

# COMMAND ----------

data = [
    {
        "request_id":"1",
        "request": "Who won the last NFL 3 super bowls?",
        "expected_response": "Kansas City Chiefs (twice, in 2024 and 2023) and the Los Angeles Rams in 2022"
    },
    {
        "request_id":"2",
        "request": "What was the top rated anime in 2024 on crunchyroll?",
        "expected_response": "Demon Slayer: Kimetsu no Yaiba"
    },
    {
        "request_id":"3",
        "request": "Who is main protaginist in the anime, Bleach?",
        "expected_response": "Ichigo Kurosaki"
    },
    {
        "request_id":"4",
        "request": "Who has the most wins in F1 history?",
        "expected_response": "Lewis Hamilton"
    }
]

eval_data = spark.createDataFrame(data).toPandas()

# COMMAND ----------


with mlflow.start_run(run_name="tavily-langgraph"):
    # Evaluate the logged model
    eval_results = mlflow.evaluate(
        data=eval_data,
        model=f'runs:/{logged_agent_info.run_id}/agent',
        model_type="databricks-agent",
    )

# COMMAND ----------

# MAGIC %md
# MAGIC # Register and Deploy

# COMMAND ----------

mlflow.set_registry_uri("databricks-uc")

catalog = "doan_demo_catalog"
schema = "multiagent"
model_name = "langgraph_tavily_agent"
UC_MODEL_NAME = f"{catalog}.{schema}.{model_name}"

# register the model to UC
uc_registered_model_info = mlflow.register_model(model_uri=logged_agent_info.model_uri, name=UC_MODEL_NAME)

# COMMAND ----------

from databricks import agents

# Deploy the model to the review app and a model serving endpoint
agents.deploy(UC_MODEL_NAME, uc_registered_model_info.version, environment_vars={"TAVILY_API_KEY": dbutils.secrets.get(scope="doan-demos", key="tavily")})

# COMMAND ----------


