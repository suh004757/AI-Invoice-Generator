"""
LM Studio 연결 예시
LM Studio에서 서버를 시작한 후 이 스크립트를 실행하세요.
"""
from openai import OpenAI
import json

def test_lm_studio_connection():
    """LM Studio 연결 테스트"""
    
    # LM Studio 클라이언트 생성
    client = OpenAI(
        base_url="http://localhost:1234/v1",  # LM Studio 기본 주소
        api_key="lm-studio"  # 로컬이라 실제 키 불필요
    )
    
    print("LM Studio 연결 테스트 중...\n")
    
    try:
        # 1. 사용 가능한 모델 확인
        models = client.models.list()
        print("=== 사용 가능한 모델 ===")
        for model in models.data:
            print(f"  - {model.id}")
        print()
        
        # 2. 간단한 테스트 요청
        print("=== 테스트 요청 ===")
        response = client.chat.completions.create(
            model="local-model",  # 또는 위에서 확인한 모델 ID
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in Korean!"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"응답: {response.choices[0].message.content}\n")
        
        # 3. PO 데이터 추출 테스트
        print("=== PO 데이터 추출 테스트 ===")
        
        sample_po = """
        PURCHASE ORDER
        
        PO Number: PO-2025-001
        Date: 2025-12-11
        
        Supplier: ABC Corporation
        Customer: XYZ Company
        Address: 123 Main St, Seoul, Korea
        
        Items:
        1. Product A - Qty: 10, Unit Price: $100
        2. Product B - Qty: 5, Unit Price: $200
        
        Subtotal: $2,000
        VAT (10%): $200
        Total: $2,200
        
        Payment Terms: Net 30
        Delivery Date: 2025-12-20
        """
        
        extraction_prompt = f"""
Extract invoice data from the following Purchase Order and return as JSON.

Required JSON format:
{{
    "po_number": "string",
    "customer_name": "string",
    "customer_address": "string",
    "items": [
        {{
            "description": "string",
            "quantity": number,
            "unit_price": number,
            "amount": number
        }}
    ],
    "subtotal": number,
    "vat": number,
    "total": number,
    "currency": "string",
    "delivery_date": "string",
    "payment_terms": "string"
}}

Purchase Order:
{sample_po}

Return ONLY valid JSON, no other text.
"""
        
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "You are a data extraction assistant. Extract structured data from documents and return valid JSON only."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,  # 낮은 temperature로 일관성 향상
            max_tokens=1000
        )
        
        extracted_text = response.choices[0].message.content
        print(f"추출된 데이터:\n{extracted_text}\n")
        
        # JSON 파싱 시도
        try:
            # JSON 블록 추출 (```json ... ``` 형식일 경우)
            if "```json" in extracted_text:
                json_str = extracted_text.split("```json")[1].split("```")[0].strip()
            elif "```" in extracted_text:
                json_str = extracted_text.split("```")[1].split("```")[0].strip()
            else:
                json_str = extracted_text.strip()
            
            data = json.loads(json_str)
            print("=== 파싱된 JSON ===")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("\n✓ LM Studio 연결 및 데이터 추출 성공!")
            
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 실패: {e}")
            print("LLM이 JSON 형식으로 응답하지 않았습니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n확인 사항:")
        print("1. LM Studio가 실행 중인가?")
        print("2. Server 탭에서 'Start Server' 버튼을 눌렀는가?")
        print("3. 모델이 로드되어 있는가?")
        print("4. 서버 주소가 http://localhost:1234 인가?")

if __name__ == "__main__":
    test_lm_studio_connection()
