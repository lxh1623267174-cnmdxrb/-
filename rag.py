from langchain_classic import text_splitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter,MarkdownHeaderTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
import os
import tiktoken

# markdown_path = r"C:\Users\laixiaohan\PycharmProjects\PythonProject\奖学金评定_无表格.md"
# headers_to_split_on = [
#     ("##","page_header"),
#     ("###","section_header")
# ]
# with open(markdown_path, "r", encoding="utf-8") as f:
#     markdown = f.read()
# markdown_splitter = MarkdownHeaderTextSplitter(
#     headers_to_split_on = headers_to_split_on,
#     strip_headers= False
#     )
#
# header_splits = markdown_splitter.split_text(markdown)
#
# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200,
#     separators=["\n\n","\n","。"," ",""]
# )
#
# final_docs = text_splitter.split_documents(header_splits)
#
# embeddings = DashScopeEmbeddings(
#     model="qwen3.7-text-embedding",
#     dashscope_api_key =  os.getenv("QW_API_KEY")
#
# )
#
# vectorstore = Chroma(
#     persist_directory="./.chroma_db",
#     embedding_function =embeddings,
#
# )
# batch_size = 16
# for i in range(0, len(final_docs), batch_size):
#     batch = final_docs[i:i+batch_size]
#     vectorstore.add_documents(batch)
#
# print("已完成")

# data = vectorstore.get()
# docs = data["documents"]
# ids = data["ids"]
# for i in docs:
#     print(i)
#     print()
# print(len(docs))

# data = vectorstore.get()
# docs = data["documents"]
# ids = data["ids"]
# seen = {}
# same_ids = []
# for i, doc in enumerate(docs):
#     if doc in seen:
#         same_ids.append(ids[i])
#     else:
#         seen[doc] = i
# print(len(same_ids))

# import shutil
#
# shutil.rmtree("./.chroma_db")
#
# print("旧数据库删除完成")