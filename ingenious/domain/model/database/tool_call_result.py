from pydantic import BaseModel

from ingenious.domain.model.chat import Action, KnowledgeBaseLink, Product


class ToolCallResult(BaseModel):
    results: str


class ProductToolCallResult(ToolCallResult):
    products: list[Product]


class KnowledgeBaseToolCallResult(ToolCallResult):
    knowledge_base_links: list[KnowledgeBaseLink]


class ActionToolCallResult(ToolCallResult):
    actions: list[Action]
