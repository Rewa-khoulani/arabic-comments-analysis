from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import re
from utils import dedup, chunk, remove_non_arabic

class InstagramSummarizer:
    def __init__(self):
        self.MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"
        self.model = None
        self.tokenizer = None
        self.load_model()

    def load_model(self):
        print("Loading Summarizer Model...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME, trust_remote_code=True)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_NAME,
            device_map="auto",
            dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            trust_remote_code=True,
        )

    def build_prompt(self, comments_text: str) -> str:
        return f"""أنت محلل عربي متخصص في تلخيص تعليقات إنستغرام.
قواعد صارمة:
- لا تختلق معلومات غير موجودة في التعليقات.
- لا تكتب أسلوب أخبار (لا تقول: تداولت/انتشر/في منشور).
- اكتب جملة واحدة إلى ثلاث جمل كحد أقصى.
- اكتب باللغة العربية فقط. يُمنع استخدام أي أحرف أو كلمات غير عربية (مثل الإنجليزية أو الصينية)، وأي خروج عن العربية يُعد خطأ.
- ركّز على الأنماط الأكثر تكراراً فقط، ولا تضخّم التعليقات الفردية أو النادرة.
- اذكر الأسئلة/الطلبات فقط إذا كانت موجودة فعلاً وبشكل متكرر.
- إذا وُجدت إساءة أو تهجّم أو سخرية جارحة، اذكر ذلك بشكل عام دون اقتباس.
- عند وجود مدح استخدم: مدح/إشادة/تشجيع/حماس، ولا تستخدم كلمة "احترام" إلا إذا وردت صراحة.
- لا تذكر "تشجيع" أو "مشاركة" إلا إذا وُجدت عبارات صريحة مثل: شارك، تابع، لايك، انشر.
- اكتب الملخص فقط بدون عناوين أو نقاط.

أمثلة:

مثال 1:
التعليقات:
- الصورة رهيبة 😍
- وين المكان؟
- الإضاءة خرافية
- متى كان التصوير؟
الملخص: إعجاب واضح بالصورة والإضاءة، مع استفسارات متكررة عن موقع المكان ووقت التصوير.

مثال 2:
التعليقات:
- السعر مبالغ فيه
- المنتج ممتاز بس غالي
- في خصم؟
- وين نشتريه؟
الملخص: تفاعل مختلط بين مدح الجودة والاعتراض على السعر، مع أسئلة عن الخصومات وطريقة الشراء.

مثال 3:
التعليقات:
- الكلام مو دقيق
- وين المصدر؟
- هذا تضليل
- اعطونا دليل
الملخص: انتقادات وتشكيك بصحة المعلومات، مع طلب واضح لمصدر أو دليل موثوق.

مثال 4:
التعليقات:
- هل صحيح الصيام المتقطع غير صحي للمرأة على المدى الطويل؟
- طيب ما قصرتي ربي يسعدك، لكن اللي بعرفه الصيام المتقطع ما يساعد على بناء العضل صحيح؟
- حبيبتي كيف صيام متقطع بين الوجبات؟ ممكن توضيح
- أحلا شرح 👏🏻✨
- هل صحيح الصيام المتقطع غير صحي للمرأة على المدى الطويل؟
الملخص: تفاعل إيجابي مع الشرح ترافق مع تساؤلات متكررة حول تأثير الصيام المتقطع على صحة المرأة وبناء العضلات، مع طلبات توضيح حول آلية تطبيقه بين الوجبات.

مثال 5 (سخرية/تنمّر + مدح):
التعليقات:
- هاد شو عم يعمل أصلاً؟
- حرفياً أزنخ محتوى
- كل الناس عم تتمسخر
- وحش 🔥
- ملك 👏
الملخص: تفاعل مختلط يجمع بين سخرية وانتقادات لاذعة تجاه الشخص ومحتواه مقابل مدح وحماس من بعض المتابعين. لا توجد أسئلة متكررة.

الآن لخص التعليقات التالية:
{comments_text}

الملخص:"""

    def generate_summary_onepass(self, comments_block: str, max_new_tokens=140) -> str:
        user_prompt = self.build_prompt(comments_block)
        messages = [
            {"role": "system", "content": "أنت مساعد عربي يلتزم بالتعليمات حرفياً ويخرج ملخصاً فقط دون أي نص إضافي."},
            {"role": "user", "content": user_prompt},
        ]
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        with torch.no_grad():
            out_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=0.0,
                repetition_penalty=1.15,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )
        out = self.tokenizer.decode(out_ids[0], skip_special_tokens=True)
        if "الملخص:" in out:
            out = out.split("الملخص:")[-1].strip()
        out = re.sub(r"\s+", " ", out).strip()
        out = remove_non_arabic(out)
        parts = re.split(r"(?<=[.!؟])\s+", out)
        return " ".join(parts[:4]).strip()

    def summarize(self, comments_list):
        if not comments_list:
            return "📭 لا توجد تعليقات لتلخيصها."
        
        comments = [c for c in comments_list if isinstance(c, str) and c.strip()]
        comments = dedup(comments)
        
        partial = []
        for part in chunk(comments, 30):
            block = "\n".join([f"- {c}" for c in part])
            partial.append(self.generate_summary_onepass(block, max_new_tokens=120))
        
        if not partial:
             return "📭 لا توجد تعليقات كافية"

        if len(partial) == 1:
            return partial[0]
        else:
            merged = "\n".join([f"- {p}" for p in partial])
            return self.generate_summary_onepass(merged, max_new_tokens=140)