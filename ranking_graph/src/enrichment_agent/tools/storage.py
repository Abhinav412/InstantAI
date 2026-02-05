"""Storage Tool."""

from typing import Any, Dict, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from enrichment_agent.db import save_crawled_data


class StorageInput(BaseModel):
    """Input Schema."""

    session_id: str = Field(description="The ID of the current research session.")
    url: str = Field(description="The source URL of the content.")
    content: str = Field(description="The extracted content (markdown preferred).")
    metadata: Dict[str, Any] = Field(
        description="Any relevant metadata (title, date, etc).", default={}
    )


class MongoWriter(BaseTool):
    """Mongo Writer Tool."""

    name: str = "save_research_data"
    description: str = "Saves valuable research findings to the database. Call this whenever you find relevant information."
    args_schema: Type[BaseModel] = StorageInput

    def _run(
        self, session_id: str, url: str, content: str, metadata: Dict[str, Any] = {}
    ) -> str:
        try:
            save_crawled_data(session_id, url, content, metadata)
            return "Successfully saved to database."
        except Exception as e:
            return f"Error saving to database: {str(e)}"
