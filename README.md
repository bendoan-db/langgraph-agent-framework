# Overview
This archive is a self-contained quickstart for LangGraph Agent on Databricks. The agent has access to Tavily for web search to assist in Q&A.

# Files
* `agent_config.yaml`: Contains key parameters for the LangGraph, including: 
  * Model params: model endpoint names, temperature, max_tokens, etc.
  * Databricks resource params: catalog, schema
* `01_langgraph_agent` Contains code for the LangGraph agent and Tavily tool
* `02_evaluate_&_deploy`: Tests/runs the code in `01_langgraph_agent`. It contains code that:
  * [Logs the chain to MLflow](https://docs.databricks.com/en/generative-ai/agent-framework/log-agent.html)
  * Implements  [mlflow.evaluate()](https://docs.databricks.com/en/generative-ai/agent-evaluation/index.html) to evaluate agent against a benchmark dataset
  * Registers the chain to Unity Catalog
  * Deploys the chain to a [serving endpoint](https://docs.databricks.com/en/generative-ai/agent-framework/deploy-agent.html) and starts a [review UI](https://docs.databricks.com/en/generative-ai/agent-evaluation/human-evaluation.html)

# Setup
1. Update `agent_config.yaml` with the Databricks Resources (catalog, schema), model resources (model endpoints, temperature, max tokens, etc.)
2. Review and customize `01_langgraph_agent` as needed
3. Test the agent code using `02_evaluate`. Once the code is stabilized, register the model, run evaluation, register and deploy.

# Requirements
* Permissions to write to schemas in Databricks
* Permissions to deploy model serving endpoints
* Enablement of [AI-assisted features](https://docs.databricks.com/en/notebooks/use-databricks-assistant.html#enable-or-disable-admin-features) on your Databricks workspace