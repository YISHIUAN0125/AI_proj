import pymupdf as fitz
import pandas as pd
import os

def remove(text):
    return text[3:] if len(text) > 3 else text

folder_path = 'PDFs'
files = [f for f in os.listdir(folder_path) if f.endswith('.pdf')]
for file in  files:
    pdf_path = os.path.join(folder_path, file)
    doc = fitz.open(pdf_path)
    rows = []
    current_line = "" 
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.split('\n')
        for line in lines:
        # 逐行保存讀取到的文字
            if line.strip().startswith(('K', 'S')) and line.strip()[1].isdigit():
                if current_line:
                    rows.append(current_line.strip())
                current_line = line.strip()
            else:
                #判斷為換行
                current_line += " " + line.strip()

        # 處理可能剩下的最後一行
        if current_line:
            rows.append(current_line.strip())
            current_line = ""

    # 清理合併之後的行
    cleaned_rows = []
    for row in rows:
        # 清除雜亂文字
        cleaned_row = row.split(' ')[0] + ' ' + ' '.join(row.split(' ')[1:]).replace(' ', '')
        cleaned_rows.append(cleaned_row)
    df = pd.DataFrame(cleaned_rows, columns=["Text"])
    #尋找K跟S開頭
    knowledge_df = df[df['Text'].str.match(r'^K\d+')]
    skills_df = df[df['Text'].str.match(r'^S\d+')]

    knowledge_df['Text'] = knowledge_df['Text'].apply(remove)
    skills_df['Text'] = skills_df['Text'].apply(remove)
    #刪除空索引
    knowledge_df = knowledge_df.dropna().drop_duplicates().reset_index(drop=True)
    skills_df = skills_df.dropna().drop_duplicates().reset_index(drop=True)

    output_filename = pdf_path.replace(".pdf", "_output.txt")
    with open(output_filename, "w", encoding="utf-8") as output_file:

        output_file.write("職能內涵 (K=knowledge 知識):\n")
        for content in knowledge_df['Text']:
            output_file.write(f" {content}\n")

        output_file.write("\n職能內涵 (S=skills 技能):\n")
        for content in skills_df['Text']:
            output_file.write(f" {content}\n")
    print(f"職能內涵內容已儲存至 {output_filename}")