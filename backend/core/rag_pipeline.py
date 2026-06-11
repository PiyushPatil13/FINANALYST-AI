from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from backend.core.vectorstore import VectorStoreManager
from backend.core.llm_config import get_gemini_llm


# ── PROMPTS ─────────────────────────────────────────────────────

CONTEXT_PROMPT = ChatPromptTemplate.from_messages([
   ("system", """
    Given the chat history and latest question:

    1. Rewrite the question as a standalone question.
    2. Replace all references like 'that', 'those', 'it', 'them'.
    3. Include important entities, metrics, and topics from prior conversation.
    4. Preserve the user's intent.
    5. Expand the query with relevant context when needed for document retrieval.

    Return ONLY the rewritten question.
    """),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert financial analyst.
    You have access to one or more financial documents.
    Use ONLY the context below to answer the question.
    If information comes from multiple documents, clearly
    indicate which document each fact comes from.
    Be concise and use numbers where available.
    If not in context say: 'This information is not available.'

    Context:
    {context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# ── RAG PIPELINE ────────────────────────────────────────────────

class RAGPipeline:
    def __init__(self):
        self.store = VectorStoreManager()
        self.llm = get_gemini_llm()
        self.chain = None
        self._rag_chain = None
        self.chat_store = {}

    def get_session_history(self, session_id: str):
        if session_id not in self.chat_store:
            self.chat_store[session_id] = InMemoryChatMessageHistory()
        return self.chat_store[session_id]

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def build_chain(self):
        if self.store.is_empty():
            raise ValueError("Vectorstore is empty. Please upload a PDF first.")

        retriever = self.store.as_retriever(k=10)

        # ← Bug 1 fixed: CONTEXT_PROMPT not contextualized_chain
        contextualize_chain = CONTEXT_PROMPT | self.llm | StrOutputParser()

        def contextualized_retriever(input_dict):
            chat_history = input_dict.get("chat_history", [])
            question = input_dict["input"]

            if chat_history:
                standalone_question = contextualize_chain.invoke({
                    "input": question,
                    "chat_history": chat_history
                })
            else:
                standalone_question = question

            docs = retriever.invoke(standalone_question)
            return docs

        def rag_chain(input_dict):
            # ← Bug 5 fixed: contextualized_retriever not contextualized_chain
            docs = contextualized_retriever(input_dict)
            context = self._format_docs(docs)

            response = QA_PROMPT | self.llm | StrOutputParser()
            answer = response.invoke({
                "input": input_dict["input"],
                "chat_history": input_dict.get("chat_history", []),
                "context": context
            })

            return {"answer": answer, "docs": docs}

        self.chain = RunnableWithMessageHistory(
            RunnableLambda(lambda x: rag_chain(x)["answer"]),
            self.get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history"
        )

        self._rag_chain = rag_chain
        print("[RAG] Chain built successfully.")

    # ← Bug 3 fixed: ask() is now at class level, not inside build_chain()
    def ask(self, question: str, session_id: str = "default") -> dict:
        if self.chain is None:
            self.build_chain()

        history = self.get_session_history(session_id)

        result = self._rag_chain({
            "input": question,
            "chat_history": history.messages
        })

        history.add_message(HumanMessage(content=question))
        history.add_message(AIMessage(content=result["answer"]))

        sources = []
        for doc in result["docs"]:
            page = doc.metadata.get("page", "?")
            sources.append(f"pg.{page + 1}")
        sources = list(dict.fromkeys(sources))

        return {
            "answer": result["answer"],
            "sources": sources
        }

    def reset(self):
        self.chain = None
        self._rag_chain = None
        self.chat_store = {}
        self.store.clear()
        print("[RAG] Pipeline reset.")