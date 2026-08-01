from langchain_community.embeddings import DashScopeEmbeddings
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_core.runnables import RunnablePassthrough,RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
import jieba
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_compressors import DashScopeRerank
from dashscope import TextReRank
import json

# os.environ["LANGSMITH_TRACING"] = "true"
#
# os.environ["LANGSMITH_API_KEY"] = "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"
#
# os.environ["LANGSMITH_PROJECT"] = "langchain_lianxi"
embeddings = DashScopeEmbeddings(
    model="qwen3.7-text-embedding",
    dashscope_api_key =  os.getenv("QW_API_KEY"),
)

vectorstore = Chroma(
    persist_directory="./.chroma_db",
    embedding_function=embeddings
)

vector_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k":7,
        "fetch_k":10
    }
)
bm25_docs = vectorstore.get()["documents"]
bm25_retriever = BM25Retriever.from_texts(
    texts = bm25_docs,preprocess_func=lambda x:jieba.lcut(x)
)

model = ChatOpenAI(
    model="qwen3.7-plus",
    api_key =  os.getenv("QW_API_KEY"),
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
)
def rewrite(query):
    prompt = f"""你是一个搜索引擎优化专家。请将用户的提问先抽取问题最关键的词组，并改写为 5 个近义或同义的检索关键词，以便在知识库中精准匹配。
【改写策略】：
1. 如果问题只有一个条件就直接简写问题，并提取关键词，删去非关键成分(人物代称等)
2. 如果问题有多个条件，那就有几个条件就拆分成几个原始问题，然后再进行关键词改写
3. 改写关键字首先考虑同义或近义词，并且不要出现两个近义词在同一个句子里
4. 改写后的问题不可超过原问题长度，可大胆删减不重要的字

【用户提问】: {query}
【输出要求】: 
必须严格输出为一个 JSON 格式的字符串数组（List），不要包含任何额外的解释或 Markdown 标签。
例如：["改写关键词1", "改写关键词2", "改写关键词3", "改写关键词4", "改写关键词5"]

【输出 JSON】:"""
    try:
        response = model.invoke(prompt)
        content = response.content.strip().replace("'''json","").replace("'''","")
        queries = json.loads(content)
        if "综测" not in query:
            queries.append(query)
        print(queries)
        return queries
    except Exception as e:
        print(e)
        return [query]
template = """你是学校奖学金知识库助手。
回答要求：
1. 优先回答用户真正的问题。
2. 参考资料只是辅助，不要直接复述资料。
3. 如果资料无法回答，请明确说明。
4. 不要把参考资料中的其他主题强行套入用户问题。
5. 如果用户的问题不是关于奖学金或者综测方面的，可以忽略参考资料，专心回答用户问题
【参考资料】
{context}
【用户问题】
{question}
【你的回答】："""
prompt = ChatPromptTemplate.from_template(template)

def format_docs(docs):

    return "\n\n".join(doc.page_content for doc in docs)

def reranked(original_query, top_n=5):
    queries = rewrite(original_query)
    all_docs_dict = {}
    for query in queries:

        vector_docs = vector_retriever.invoke(query)
        bm25_docs = bm25_retriever.invoke(query)

        for doc in bm25_docs + vector_docs:
            all_docs_dict[doc.page_content] = doc

    all_docs_list = list(all_docs_dict.values())
    if not all_docs_list:
        return "未检索到资料"
    try:
        rerank_docs = TextReRank.call(
                model = "gte-rerank-v2",
                api_key = os.getenv("QW_API_KEY"),
                top_n=top_n,
                query = original_query,
                documents=[doc.page_content for doc in all_docs_list]
            )

        results = sorted(rerank_docs.output.results,
                         key=lambda doc: doc.relevance_score,
                         reverse=True)

        docs_list = [all_docs_list[r.index] for r in results[:top_n]]
        for i in docs_list:
            print(i)
        return format_docs(docs_list)
    except Exception as e:
        print(e)
        return format_docs(all_docs_list[:top_n])


rag_chain = (
    {"context":lambda x:reranked(x), "question":RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
if __name__ == "__main__":
    while True:
        user_input = input("用户：")
        if  not user_input :
            break
        else:
            try:
                for chunk in rag_chain.stream(user_input):
                    print(chunk,end="",flush=True)
                print()
            except Exception as e:
                print(e)

