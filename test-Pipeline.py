import pandas as pd
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# CSV 데이터 로드 함수
def load_data(filename):
    try:
        data = pd.read_csv(filename, encoding='utf-8')
        if '질문지' not in data.columns:
            raise ValueError("CSV 파일에 '질문지' 열이 없습니다. 열 이름을 확인해 주세요.")
        return data
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# 간단한 답변 생성 함수
def get_answer(question: str) -> str:
    result = "답변: " + question
    return result

# 기본 함수 기반으로 답변 생성
def generate_answers(df):
    responses = []
    for question in df['질문지']:
        if pd.isna(question) or question.strip() == "":
            responses.append("답변: 질문이 제공되지 않았습니다.")  # 빈 질문 처리
            continue
        responses.append(get_answer(question))  # 항상 get_answer 사용
    return responses

# 메인 함수
def main():
    file_path = os.path.join(os.getcwd(), '예상_질문_60개.csv')
    output_path = os.path.join(os.getcwd(), 'total.csv')

    # 데이터 로드
    df = load_data(file_path)
    if df.empty:
        print("Data loading failed.")
        return

    # 항상 get_answer 기반으로 답변 생성
    df['질문에 대한 답변'] = generate_answers(df)

    # 결과 저장
    df.to_csv(output_path, index=False)
    print("Answers generated and saved.")

if __name__ == "__main__":
    main()
