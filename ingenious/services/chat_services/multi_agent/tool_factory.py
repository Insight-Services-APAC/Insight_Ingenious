# tool_factory.py
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
import ingenious.config.config as config


class ToolFunctions:
    @staticmethod
    def aisearch(search: str, index_name: str) -> str:
        _config = config.get_config()
        credential = AzureKeyCredential(_config.azure_search_services[0].key)
        client = SearchClient(
                endpoint=_config.azure_search_services[0].endpoint,
                index_name=index_name,
                credential=credential,
            )
        results = client.search(search_text=search, top=5,
                                query_type = "semantic", #semantic, full or simple
                                query_answer = "extractive",
                                query_caption="extractive",
                                vector_queries = None) #vector_queries can input the query as a vector
        text_results = ""
        title = ""
        for result in results:
            captions = result['@search.captions']
            for caption in captions:
                text_results = text_results + "; " + caption.text
                if 'title' in result:
                    title = result['title']
                else:
                    title = ""
        return text_results

    def update_memory(context: str) -> None:
        _config = config.get_config()
        memory_path = _config.chat_history.memory_path
        with open(f"{memory_path}/context.md", "w") as memory_file:
            memory_file.write(context)


