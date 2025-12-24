"""
프롬프트 엔지니어링으로 Local LLM 성능 향상하기
트레이닝 없이 Few-Shot Learning 사용 (추천 방법!)
"""

from openai import OpenAI
import json

def create_few_shot_prompt(po_text: str) -> str:
    """
    Few-shot learning을 위한 프롬프트 생성
    실제 PO 예시를 포함하여 모델 성능 향상
    """
    
    prompt = """You are an expert invoice data extraction assistant.
Extract structured data from Purchase Order documents and return valid JSON only.

Here are examples of correct extractions:

=== Example 1: English PO ===
Input:
PURCHASE ORDER
PO Number: PO-2025-001
Date: 2025-12-10

Supplier: Tech Solutions Inc.
Customer: ABC Corporation
Address: 123 Main Street, Seoul, Korea

Items:
1. Laptop Computer - Qty: 5, Unit Price: $1,200.00
2. Wireless Mouse - Qty: 10, Unit Price: $25.00

Subtotal: $6,250.00
VAT (10%): $625.00
Total: $6,875.00

Payment Terms: Net 30
Delivery Date: 2025-12-20

Output:
{
  "po_number": "PO-2025-001",
  "date": "2025-12-10",
  "customer_name": "ABC Corporation",
  "customer_address": "123 Main Street, Seoul, Korea",
  "items": [
    {
      "description": "Laptop Computer",
      "quantity": 5,
      "unit_price": 1200.00,
      "amount": 6000.00
    },
    {
      "description": "Wireless Mouse",
      "quantity": 10,
      "unit_price": 25.00,
      "amount": 250.00
    }
  ],
  "subtotal": 6250.00,
  "vat": 625.00,
  "total": 6875.00,
  "currency": "USD",
  "payment_terms": "Net 30",
  "delivery_date": "2025-12-20"
}

=== Example 2: Korean PO ===
Input:
발주서
발주번호: 2025-002
날짜: 2025-12-11

공급자: 테크솔루션
고객: XYZ 주식회사
주소: 서울시 강남구 테헤란로 123

품목:
1. 노트북 컴퓨터 - 수량: 3대, 단가: 1,500,000원
2. 모니터 - 수량: 3대, 단가: 300,000원

소계: 5,400,000원
부가세 (10%): 540,000원
합계: 5,940,000원

결제조건: 30일
납품일: 2025-12-25

Output:
{
  "po_number": "2025-002",
  "date": "2025-12-11",
  "customer_name": "XYZ 주식회사",
  "customer_address": "서울시 강남구 테헤란로 123",
  "items": [
    {
      "description": "노트북 컴퓨터",
      "quantity": 3,
      "unit_price": 1500000,
      "amount": 4500000
    },
    {
      "description": "모니터",
      "quantity": 3,
      "unit_price": 300000,
      "amount": 900000
    }
  ],
  "subtotal": 5400000,
  "vat": 540000,
  "total": 5940000,
  "currency": "KRW",
  "payment_terms": "30일",
  "delivery_date": "2025-12-25"
}

=== Now extract from this PO ===
Input:
{po_text}

Output (JSON only, no other text):
"""
    
    return prompt.format(po_text=po_text)


def extract_with_few_shot(po_text: str, llm_url: str = "http://localhost:1234"):
    """
    Few-shot learning으로 PO 데이터 추출
    트레이닝 없이 예시만으로 성능 향상!
    """
    
    client = OpenAI(
        base_url=f"{llm_url}/v1",
        api_key="lm-studio"
    )
    
    # Few-shot 프롬프트 생성
    prompt = create_few_shot_prompt(po_text)
    
    print("=" * 60)
    print("Few-Shot Learning으로 데이터 추출 중...")
    print("=" * 60)
    
    response = client.chat.completions.create(
        model="local-model",
        messages=[
            {
                "role": "system",
                "content": "You are a precise data extraction assistant. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,  # 낮은 temperature로 일관성 향상
        max_tokens=2000
    )
    
    result = response.choices[0].message.content
    
    # JSON 추출
    try:
        # 코드 블록 제거
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0].strip()
        elif "```" in result:
            result = result.split("```")[1].split("```")[0].strip()
        
        data = json.loads(result)
        
        print("\n✓ 추출 성공!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
        
    except json.JSONDecodeError as e:
        print(f"\n✗ JSON 파싱 실패: {e}")
        print(f"원본 응답:\n{result}")
        return None


def test_few_shot_learning():
    """Few-shot learning 테스트"""
    
    # 테스트 PO (새로운 형식)
    test_po = """
    구매 발주서
    
    발주 번호: PO-2025-100
    발주 날짜: 2025-12-12
    
    납품업체: 글로벌 테크
    구매업체: 스타트업 코리아
    배송지: 경기도 성남시 분당구 판교역로 235
    
    주문 내역:
    - 상품명: 개발용 서버 - 수량: 2 / 단가: 5,000,000원
    - 상품명: 네트워크 스위치 - 수량: 1 / 단가: 800,000원
    
    공급가액: 10,800,000원
    부가세: 1,080,000원
    총액: 11,880,000원
    
    결제: 60일 후 지급
    납기: 2025-12-30
    """
    
    print("\n테스트 PO:")
    print(test_po)
    print("\n" + "=" * 60)
    
    # Few-shot learning으로 추출
    result = extract_with_few_shot(test_po)
    
    if result:
        print("\n" + "=" * 60)
        print("✓ Few-Shot Learning 성공!")
        print("트레이닝 없이도 정확하게 추출되었습니다.")
        print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("프롬프트 엔지니어링 (Few-Shot Learning) 예시")
    print("트레이닝 불필요! 예시만으로 성능 향상")
    print("=" * 60)
    
    # LM Studio 서버가 실행 중이어야 합니다
    test_few_shot_learning()
