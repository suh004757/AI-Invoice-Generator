"""
Local LLM 파인튜닝 예시 (Unsloth 사용)
주의: 이 방법은 고급 사용자용이며, 대부분의 경우 필요하지 않습니다!
프롬프트 엔지니어링으로 충분합니다.
"""

# 필요한 패키지 (GPU 필요):
# pip install unsloth torch transformers datasets

from unsloth import FastLanguageModel
import torch
from datasets import load_dataset

def finetune_for_invoice_extraction():
    """
    PO 데이터 추출을 위한 LLM 파인튜닝
    
    요구사항:
    - NVIDIA GPU (최소 8GB VRAM)
    - 학습 데이터 (training_data.jsonl)
    """
    
    # 1. 베이스 모델 로드
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/llama-3-8b-bnb-4bit",  # 4bit 양자화 모델
        max_seq_length=2048,
        dtype=None,
        load_in_4bit=True,
    )
    
    # 2. LoRA 어댑터 추가 (효율적인 파인튜닝)
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,  # LoRA rank
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing=True,
    )
    
    # 3. 학습 데이터 로드
    dataset = load_dataset("json", data_files="training_data.jsonl", split="train")
    
    # 4. 학습 설정
    from transformers import TrainingArguments
    from trl import SFTTrainer
    
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=2048,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=100,  # 적은 스텝으로 시작
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            output_dir="outputs",
        ),
    )
    
    # 5. 학습 시작
    print("파인튜닝 시작...")
    trainer.train()
    
    # 6. 모델 저장
    model.save_pretrained("invoice_extraction_model")
    tokenizer.save_pretrained("invoice_extraction_model")
    
    print("✓ 파인튜닝 완료!")
    print("모델 저장 위치: invoice_extraction_model/")

if __name__ == "__main__":
    print("=" * 60)
    print("경고: 이 스크립트는 고급 사용자용입니다!")
    print("대부분의 경우 프롬프트 엔지니어링으로 충분합니다.")
    print("=" * 60)
    
    # finetune_for_invoice_extraction()
