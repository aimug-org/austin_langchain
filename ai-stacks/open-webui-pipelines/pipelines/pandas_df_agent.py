# -*- coding: utf-8 -*-
"""
title: Pandas DataFrame Agent
author: open-webui
date: 2024-05-30
version: 1.0
license: MIT
description: Process CSV/Excel files using pandas agent with natural language queries
requirements: langchain, langchain-experimental, langchain-community, langchain_ollama, pandas, openpyxl
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import tempfile
import base64
import os
import logging
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_ollama import OllamaLLM
from langchain.agents.agent_types import AgentType
from pydantic import BaseModel, Field
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add console handler if not already added
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

class Pipeline(FunctionCallingBlueprint):
    """Pipeline for processing CSV/Excel files using pandas agent with Ollama models"""

    class Valves(FunctionCallingBlueprint.Valves):
        """Pipeline configuration valves"""
        model: str = Field(
            default="llama2",
            description="Ollama model to use"
        )
        temperature: float = Field(
            default=0.0,
            ge=0.0,
            le=1.0,
            description="Controls randomness in responses"
        )
        base_url: str = Field(
            default="http://ollama:11434",
            description="Ollama API base URL"
        )

    class Tools:
        def __init__(self, pipeline) -> None:
            self.pipeline = pipeline

        def analyze_data(self, query: str) -> str:
            """
            Analyze the loaded dataframe using natural language queries.

            :param query: Natural language query about the data
            :return: Analysis result based on the query
            """
            logger.info(f"Analyzing data with query: {query}")

            if not hasattr(self.pipeline, 'df') or self.pipeline.df is None:
                logger.warning("Attempt to analyze data without loaded dataframe")
                return "Please upload a CSV or Excel file first."

            if not hasattr(self.pipeline, 'agent') or self.pipeline.agent is None:
                logger.warning("Attempt to analyze data without initialized agent")
                return "Agent not initialized. Please ensure the LLM is properly configured."

            try:
                # Use the langchain agent for analysis
                logger.debug("Invoking langchain agent for analysis")
                result = self.pipeline.agent.invoke(query)
                return str(result["output"] if isinstance(result, dict) else result)
            except Exception as e:
                logger.error(f"Error during data analysis: {str(e)}", exc_info=True)
                return f"Error analyzing data: {str(e)}"

        def get_data_info(self) -> str:
            """
            Get basic information about the loaded dataframe.

            :return: Information about the loaded dataframe
            """
            logger.info("Retrieving dataframe information")

            if not hasattr(self.pipeline, 'df') or self.pipeline.df is None:
                logger.warning("Attempt to get info without loaded dataframe")
                return "No data loaded. Please upload a CSV or Excel file first."

            try:
                info = {
                    'columns': list(self.pipeline.df.columns),
                    'rows': len(self.pipeline.df),
                    'dtypes': self.pipeline.df.dtypes.to_dict()
                }
                logger.debug(f"DataFrame info retrieved: {info}")
                return (f"DataFrame Info:\n"
                        f"- Rows: {info['rows']}\n"
                        f"- Columns: {', '.join(info['columns'])}\n"
                        f"- Data Types: {', '.join(f'{k}: {v}' for k, v in info['dtypes'].items())}")
            except Exception as e:
                logger.error(f"Error getting data info: {str(e)}", exc_info=True)
                return f"Error getting data info: {str(e)}"

    def __init__(self):
        logger.info("Initializing Pandas DataFrame Agent Pipeline")
        super().__init__()
        self.name = "Pandas DataFrame Agent"
        self.description = "Process CSV/Excel files using pandas agent with natural language queries"
        self.resources = {}
        self.df = None
        self.agent = None
        self.temp_dir = tempfile.mkdtemp()
        logger.debug(f"Created temporary directory: {self.temp_dir}")
        self.valves = self.Valves(
            **{
                **self.valves.model_dump(),
                "pipelines": ["*"],  # Connect to all pipelines
            }
        )
        self.tools = self.Tools(self)
        logger.info("Pipeline initialization completed")

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        """Process incoming messages - handle file uploads"""
        logger.info("Processing inlet message")
        try:
            if "file" in body:
                logger.info("File upload detected, processing file")
                result = await self._process_file(body["file"], body.get("filename", ""))
                messages = body.get("messages", [])
                messages.append({
                    "role": "system",
                    "content": result
                })
                body["messages"] = messages
            return body
        except Exception as e:
            logger.error(f"Error in inlet processing: {str(e)}", exc_info=True)
            messages = body.get("messages", [])
            messages.append({
                "role": "system",
                "content": f"Error processing file: {str(e)}"
            })
            body["messages"] = messages
            return body

    async def _process_file(self, file_bytes: str, filename: str) -> str:
        """Process uploaded CSV or Excel file"""
        logger.info(f"Processing file: {filename}")
        try:
            # Validate file type
            if not any(filename.lower().endswith(ext) for ext in ['.csv', '.xlsx', '.xls']):
                logger.warning(f"Unsupported file type: {filename}")
                return "Unsupported file type. Please upload a CSV or Excel file."

            # Decode file content
            logger.debug("Decoding file content")
            decoded_bytes = base64.b64decode(file_bytes)

            # Save to temporary file
            temp_path = os.path.join(self.temp_dir, filename)
            try:
                logger.debug(f"Saving file to temporary path: {temp_path}")
                with open(temp_path, "wb") as buffer:
                    buffer.write(decoded_bytes)

                # Read file based on extension
                logger.info("Reading file into pandas DataFrame")
                if filename.lower().endswith(('.xlsx', '.xls')):
                    self.df = pd.read_excel(temp_path)
                else:
                    self.df = pd.read_csv(temp_path)

                # Initialize agent
                logger.info("Initializing pandas DataFrame agent")
                self.agent = create_pandas_dataframe_agent(
                    self.resources["llm"],
                    self.df,
                    verbose=True,
                    agent_type=AgentType.OPENAI_FUNCTIONS
                )

                info = {
                    'columns': list(self.df.columns),
                    'rows': len(self.df)
                }
                logger.info(f"File processed successfully: {info}")
                return f"Successfully loaded file with {info['rows']} rows. Available columns: {', '.join(info['columns'])}"
            finally:
                if os.path.exists(temp_path):
                    logger.debug(f"Removing temporary file: {temp_path}")
                    os.remove(temp_path)

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return f"Error processing file: {str(e)}"

    async def on_startup(self):
        """Initialize async resources when pipeline server starts"""
        logger.info("Starting pipeline initialization")
        try:
            logger.info(f"Initializing LLM with model: {self.valves.model}")
            self.resources["llm"] = OllamaLLM(
                model=self.valves.model,
                temperature=self.valves.temperature,
                base_url=self.valves.base_url
            )
            logger.info("Pipeline startup completed successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}", exc_info=True)
            raise Exception(f"Failed to initialize LLM: {str(e)}")

    async def on_shutdown(self):
        """Clean up resources when pipeline server stops"""
        logger.info("Starting pipeline shutdown")
        try:
            self.df = None
            self.agent = None
            if os.path.exists(self.temp_dir):
                logger.debug(f"Removing temporary directory: {self.temp_dir}")
                os.rmdir(self.temp_dir)
            self.resources.clear()
            logger.info("Pipeline shutdown completed successfully")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}", exc_info=True)
            print(f"Error during cleanup: {str(e)}")

    async def on_valves_updated(self):
        """React to valve configuration changes"""
        logger.info("Processing valve configuration update")
        try:
            # Reinitialize LLM with new settings
            logger.info(f"Reinitializing LLM with updated settings - Model: {self.valves.model}")
            self.resources["llm"] = OllamaLLM(
                model=self.valves.model,
                temperature=self.valves.temperature,
                base_url=self.valves.base_url
            )

            # Recreate agent if dataframe exists
            if self.df is not None:
                logger.info("Recreating pandas DataFrame agent with new LLM")
                self.agent = create_pandas_dataframe_agent(
                    self.resources["llm"],
                    self.df,
                    verbose=True,
                    agent_type=AgentType.OPENAI_FUNCTIONS
                )
            logger.info("Valve configuration update completed successfully")
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}", exc_info=True)
            raise Exception(f"Error updating configuration: {str(e)}")


# Make Pipeline class available at module level
__all__ = ["Pipeline"]
