import json
import anthropic
from pydantic import ValidationError
from app.domain.generation.schema import GenerationResult
from app.models.relational import GenerationStatus

class GenerationResponse:
    def __init__(self, status: GenerationStatus, result: GenerationResult = None, raw_response: str = None, error_detail: str = None):
        self.status = status
        self.result = result
        self.raw_response = raw_response
        self.error_detail = error_detail

class LLMGenerator:
    def __init__(self, client: anthropic.Client, model: str = "claude-3-haiku-20240307", prompt_version: str = "v1.0"):
        self.client = client
        self.model = model
        self.prompt_version = prompt_version
        
    def generate_test_cases(self, text_context: str) -> GenerationResponse:
        system_prompt = "You are a QA engineer. Generate 3-5 test cases based on the provided text. Return ONLY raw JSON matching the required schema. Do not output markdown code blocks."
        prompt = f"Text:\n{text_context}\n\nReturn a JSON object with a 'test_cases' list containing 3-5 test cases."
        
        return self._execute_with_retry(system_prompt, prompt)
        
    def _execute_with_retry(self, system_prompt: str, prompt: str, retry_count: int = 1) -> GenerationResponse:
        messages = [{"role": "user", "content": prompt}]
        
        for attempt in range(retry_count + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    system=system_prompt,
                    messages=messages,
                    temperature=0.0
                )
                raw_text = response.content[0].text
                
            except Exception as e:
                # Provider error (network, timeout, auth, etc.)
                return GenerationResponse(
                    status=GenerationStatus.provider_error,
                    error_detail=str(e)
                )
                
            try:
                # Extract JSON from potential markdown blocks if the LLM hallucinated them
                clean_text = raw_text.strip()
                if clean_text.startswith("```json"):
                    clean_text = clean_text[7:]
                if clean_text.startswith("```"):
                    clean_text = clean_text[3:]
                if clean_text.endswith("```"):
                    clean_text = clean_text[:-3]
                clean_text = clean_text.strip()

                parsed_json = json.loads(clean_text)
                result = GenerationResult(**parsed_json)
                
                return GenerationResponse(
                    status=GenerationStatus.success,
                    result=result,
                    raw_response=raw_text
                )
            except (json.JSONDecodeError, ValidationError) as e:
                error_detail = str(e)
                if attempt < retry_count:
                    # Append error for retry
                    messages.append({"role": "assistant", "content": raw_text})
                    messages.append({"role": "user", "content": f"Your previous response failed validation: {error_detail}\nPlease fix it and return ONLY valid JSON matching the exact schema."})
                else:
                    return GenerationResponse(
                        status=GenerationStatus.validation_failed,
                        raw_response=raw_text,
                        error_detail=error_detail
                    )
