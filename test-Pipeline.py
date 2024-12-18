import pandas as pd
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import openai
from fuzzywuzzy import fuzz

# 환경 변수 로드
load_dotenv()

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_username = os.getenv("NEO4J_USERNAME")
neo4j_password = os.getenv("NEO4J_PASSWORD")
openai_api_key = os.getenv("OPENAI_API_KEY")

# OpenAI API 초기화
openai.api_key = openai_api_key

# Neo4j 연결 클래스
class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.run(query, parameters=parameters)
            return [record for record in result]

graph = Neo4jConnection(neo4j_uri, neo4j_username, neo4j_password)

# CSV 데이터 로드 함수
def load_data(filename):
    data = pd.read_csv(filename, encoding='utf-8', header=2)  # header=2로 첫 번째 행을 열 이름으로 인식
    print(data.columns)  # 로드된 열 이름 출력
    if '질문지' not in data.columns:
        raise ValueError("CSV 파일에 '질문지' 열이 없습니다. 열 이름을 확인해 주세요.")
    return data


# 유사도 비교를 통한 정확도 계산 및 점수 저장 함수
def calculate_accuracy(df, threshold=70):
    scores = []
    is_correct = []
    for question, expected, answer in zip(df['질문지'], df['질문에 따른 예상 정답'], df['LLM 질문 답변 (Neo4j Graph Database)']):
        if pd.isna(expected) or expected.strip() == "":
            print(f"Question: {question}\nExpected: {expected}\nAnswer: {answer}\nScore: N/A (Expected answer missing)\n")
            scores.append(None)
            is_correct.append(False)
            continue
        if pd.isna(answer) or answer.strip() == "":
            print(f"Question: {question}\nExpected: {expected}\nAnswer: {answer}\nScore: N/A (LLM answer missing)\n")
            scores.append(None)
            is_correct.append(False)
            continue
        # fuzz.token_sort_ratio 사용
        score = fuzz.token_sort_ratio(expected, answer)
        print(f"Question: {question}\nExpected: {expected}\nAnswer: {answer}\nScore: {score}\n")
        scores.append(score)
        is_correct.append(score >= threshold)
    df['Score'] = scores
    df['is_correct'] = is_correct
    return df['is_correct'].mean()




def generate_answers(df):
    responses = []
    for question in df['질문지']:
        try:
            if pd.isna(question) or question.strip() == "":
                responses.append("No question provided")
                print(f"Question: {question}\nAnswer: No question provided\nScore: 0\n")
                continue

            response = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
            messages=[
             {"role": "system", "content": "You are an assistant who provides answers based on university academic announcements."},
             {"role": "user", "content": f"Answer concisely and accurately: {question}"}
              ],
         max_tokens=200
)

            answer = response['choices'][0]['message']['content'].strip()
            responses.append(answer)
            print(f"Question: {question}\nAnswer: {answer}\nScore: N/A\n")
        except openai.error.OpenAIError as e:
            error_message = f"Error generating response: {str(e)}"
            print(error_message)
            responses.append(error_message)
    return responses



# 메인 함수
def main():
    # 데이터 로드
    df = load_data('/Users/hanhyuk/Downloads/캡스톤 디자인 2/24-2 VSCode/24-2 Total-Project/예상 질문 60개 + 성능 평가 지표 - 성능 평가 지표.csv')
    
    # LLM 답변 생성
    df['LLM 질문 답변 (Neo4j Graph Database)'] = generate_answers(df)
    
    # 정확도 계산
    accuracy = calculate_accuracy(df)
    
    # 결과 저장
    df.to_csv('total.csv', index=False)
    print(f"Accuracy: {accuracy}")

if __name__ == "__main__":
    main()
