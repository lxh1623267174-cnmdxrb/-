import fitz
import pdfplumber
pdf_path = r"D:\Documents\Desktop\9.18★ 《海洋信息工程学院学生专业奖学金评定和综合素质量化测评办法》的通知_20250918173325.pdf"



def clean_cell(cell):
    """清洗单元格里的多余换行和空格"""
    if not cell:
        return ""
    # 将单元格内部的换行符替换为空格，并压缩连续空格
    return " ".join(cell.split())


def table_to_markdown(table):
    """将 pdfplumber 提取的二维表格矩阵转为标准的 Markdown 表格文本"""
    if not table:
        return ""

    cleaned_table = []
    for row in table:
        cleaned_row = [clean_cell(cell) for cell in row]
        # 过滤掉完全为空的整行
        if any(cleaned_row):
            cleaned_table.append(cleaned_row)

    if not cleaned_table:
        return ""

    md_lines = []
    # 提取第一行为表头
    header = cleaned_table[0]
    md_lines.append("| " + " | ".join(header) + " |")
    md_lines.append("| " + " | ".join(["---"] * len(header)) + " |")

    # 处理后面的每一行数据
    for row in cleaned_table[1:]:
        # 防止列数对不齐（填充空列）
        if len(row) < len(header):
            row += [""] * (len(header) - len(row))
        elif len(row) > len(header):
            row = row[: len(header)]
        md_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(md_lines)


def process_pdf(pdf_path):
    full_document = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            print(f"正在处理第 {page_num} 页...")

            # 1. 提取当前页的正文文本
            page_text = page.extract_text() or ""

            # 2. 提取当前页的所有表格，并转为 Markdown 格式
            tables = page.extract_tables()
            md_tables = []
            for t in tables:
                md_t = table_to_markdown(t)
                if md_t:
                    md_tables.append(md_t)

            # 3. 按页拼装
            page_content = f"## 第 {page_num} 页\n\n"
            if page_text.strip():
                page_content += f"### 正文内容\n{page_text.strip()}\n\n"

            if md_tables:
                page_content += "### 结构化表格\n" + "\n\n".join(md_tables) + "\n\n"

            full_document.append(page_content)

    return "\n".join(full_document)


if __name__ == "__main__":
    # 执行提取
    markdown_result = process_pdf(pdf_path)

    # 1. 打印预览前 1000 个字符
    print("\n" + "=" * 20 + " 提取预览 " + "=" * 20)
    print(markdown_result[:1000])

    # 2. 保存为 .md 文件（用于下一步的 RAG 结构化切分）
    output_md_path = "奖学金评定办法_提取结果.md"
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(markdown_result)

    print(f"\n✅ 处理完成！已成功将正文与表格提取并存入：{output_md_path}")
# def extract_text(pdf_path):
#     docs = fitz.open(pdf_path)
#     all_docs = []
#     for page_num,doc in enumerate(docs):
#         text = doc.get_text()
#         all_docs.append(
#             {
#                 "page": page_num + 1,
#                 "text": text
#             }
#         )
#     return all_docs
# all_docs_list = extract_text(pdf_path)

# for doc in all_docs_list[:3]:
#     print("页码",doc["page"])
#     print(doc["text"])
# #     print()
# def extract_tables(pdf_path):
#     tables = []
#     with pdfplumber.open(pdf_path) as pdf:
#         for page_num,page in enumerate(pdf.pages):
#             page_tables = page.extract_tables()
#             for table in page_tables:
#                 tables.append(
#                     {
#                         "page": page_num + 1,
#                         "table": table
#                     }
#                 )
#     return tables
#
# def clean_tables(text):
#     if text is None:
#         return ""
#     elif "\n" in text :
#         text = text.replace("\n", "")
#         return text.strip()
#     else:
#         return text
#
# if __name__ == "__main__":
#     tables = extract_tables(pdf_path)
#     new_tables = []
#     for table in tables:
#         for row in table["table"]:
#             for col in row:
#                 i = clean_tables(col)
#                 new_tables.append(i)
#     print(new_tables)