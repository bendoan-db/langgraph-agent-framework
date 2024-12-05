# Databricks notebook source
# MAGIC %md
# MAGIC # Overview
# MAGIC This archive is a self-contained quickstart for LangGraph Agent on Databricks. The agent has access to Tavily for web search to assist in Q&A.
# MAGIC
# MAGIC # Files
# MAGIC * `agent_config.yaml`: Contains key parameters for the LangGraph, including: 
# MAGIC   * Model params: model endpoint names, temperature, max_tokens, etc.
# MAGIC   * Databricks resource params: catalog, schema
# MAGIC * `01_langgraph_agent` Contains code for the LangGraph agent and Tavily tool
# MAGIC * `02_evaluate_&_deploy`: Tests/runs the code in `01_langgraph_agent`. It contains code that:
# MAGIC   * [Logs the chain to MLflow](https://docs.databricks.com/en/generative-ai/agent-framework/log-agent.html)
# MAGIC   * Implements  [mlflow.evaluate()](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html) to evaluate agent against a benchmark dataset
# MAGIC   * Registers the chain to Unity Catalog
# MAGIC   * Deploys the chain to a [serving endpoint](https://docs.databricks.com/en/generative-ai/agent-framework/deploy-agent.html) and starts a [review UI](https://docs.databricks.com/en/generative-ai/agent-evaluation/human-evaluation.html)
# MAGIC
# MAGIC # Setup
# MAGIC 1. Update `agent_config.yaml` with the Databricks Resources (catalog, schema), model resources (model endpoints, temperature, max tokens, etc.)
# MAGIC 2. Review and customize `01_langgraph_agent` as needed
# MAGIC 3. Test the agent code using `02_evaluate`. Once the code is stabilized, register the model, run evaluation, register and deploy.
# MAGIC
# MAGIC # Requirements
# MAGIC * Permissions to write to schemas in Databricks
# MAGIC * Permissions to deploy model serving endpoints
# MAGIC * Enablement of [AI-assisted features](https://docs.databricks.com/en/notebooks/use-databricks-assistant.html#enable-or-disable-admin-features) on your Databricks workspace
