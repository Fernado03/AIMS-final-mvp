# services/llm_service.py

import traceback
from openai import OpenAI
from backend.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from backend.rag.knowledge_base_service import KnowledgeBaseService
from backend.rag.prompt_service import get_assessment_prompt, get_plan_prompt, get_summary_prompt

llm_client = None
kb_service = KnowledgeBaseService()

try:
    llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=120)
    print(f"✅ LLM initialized: {LLM_MODEL} @ {LLM_BASE_URL}")
except Exception as e:
    print(f"⚠️ Error initializing LLM: {e}\n{traceback.format_exc()}")
    llm_client = None


def _complete(prompt):
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return (response.choices[0].message.content or "").strip()


def _stream(prompt):
    response = llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    for chunk in response:
        delta = chunk.choices[0].delta.content if chunk.choices else None
        if delta:
            yield delta


def _cite(text, cites):
    if not text or not cites:
        return text
    return text.rstrip() + "\n\nSources:\n" + "\n".join(f"- {c}" for c in cites)


def _cite_block(cites):
    if not cites:
        return ""
    return "\n\nSources:\n" + "\n".join(f"- {c}" for c in cites)

def generate_assessment_from_notes(subjective_text, objective_text):
    if not llm_client:
        print("⚠️ LLM not available. Skipping assessment generation.")
        return None

    rag_context, cites = kb_service.get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}")
    prompt = get_assessment_prompt(subjective_text, objective_text, rag_context)
    try:
        print(f"🧠 Generating assessment for S: '{subjective_text[:100]}...', O: '{objective_text[:100]}...'")
        generated_text = _complete(prompt)
        print(f"✅ LLM generated assessment: {generated_text[:200]}...")
        if "Diagnosis / Impression:" in generated_text or "Differential Diagnosis (DDx):" in generated_text:
            return _cite(generated_text, cites)
        print(f"⚠️ LLM response did not seem to contain a valid assessment structure: {generated_text[:200]}...")
        return None
    except Exception as e:
        print(f"🚨 Error calling LLM or processing response: {e}\n{traceback.format_exc()}")
        return None


def generate_plan_from_soap_notes(subjective_text, objective_text, assessment_text):
    if not llm_client:
        print("⚠️ LLM not available for plan generation.")
        return None

    rag_context, cites = kb_service.get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}")
    full_prompt = get_plan_prompt(subjective_text, objective_text, assessment_text, rag_context)
    try:
        print("🤖 Sending prompt to LLM for PLAN generation...")
        generated_plan = _complete(full_prompt)
        if "PLAN" not in generated_plan.upper() and not any(
            kw in generated_plan.upper()
            for kw in ["DIAGNOSTICS", "MEDICATIONS", "THERAPY", "REFERRALS", "EDUCATION", "FOLLOW-UP"]
        ):
            print(f"⚠️ LLM response might not be a valid plan: {generated_plan[:200]}...")
        print(f"✅ LLM generated plan: {generated_plan[:200]}...")
        return _cite(generated_plan, cites)
    except Exception as e:
        print(f"Error calling LLM for plan generation: {e}\n{traceback.format_exc()}")
        return None


def generate_summary_from_soap_note(subjective_text, objective_text, assessment_text, plan_text):
    if not llm_client:
        print("LLM not available for summary generation.")
        return None

    rag_context, cites = kb_service.get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}\nPlan: {plan_text}")
    prompt = get_summary_prompt(subjective_text, objective_text, assessment_text, plan_text, rag_context)
    try:
        print("🤖 Sending prompt to LLM for SUMMARY generation...")
        generated_summary = _complete(prompt)
        print(f"✅ LLM generated summary: {generated_summary[:200]}...")
        return _cite(generated_summary, cites)
    except Exception as e:
        print(f"Error calling LLM for summary generation: {e}\n{traceback.format_exc()}")
        return None


def stream_assessment_from_notes(subjective_text, objective_text):
    if not llm_client:
        yield "Error: LLM not available."
        return

    rag_context, cites = kb_service.get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}")
    prompt = get_assessment_prompt(subjective_text, objective_text, rag_context)
    try:
        print("🧠 STREAMING assessment...")
        yield from _stream(prompt)
        extra = _cite_block(cites)
        if extra:
            yield extra
    except Exception as e:
        print(f"🚨 Error streaming assessment: {e}")
        yield f"Error generating assessment: {str(e)}"


def stream_plan_from_soap_notes(subjective_text, objective_text, assessment_text):
    if not llm_client:
        yield "Error: LLM not available."
        return

    rag_context, cites = kb_service.get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}")
    full_prompt = get_plan_prompt(subjective_text, objective_text, assessment_text, rag_context)
    try:
        print("🤖 STREAMING plan...")
        yield from _stream(full_prompt)
        extra = _cite_block(cites)
        if extra:
            yield extra
    except Exception as e:
        print(f"🚨 Error streaming plan: {e}")
        yield f"Error generating plan: {str(e)}"


def stream_summary_from_soap_note(subjective_text, objective_text, assessment_text, plan_text):
    if not llm_client:
        yield "Error: LLM not available."
        return

    rag_context, cites = kb_service.get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}\nPlan: {plan_text}")
    prompt = get_summary_prompt(subjective_text, objective_text, assessment_text, plan_text, rag_context)
    try:
        print("🤖 STREAMING summary...")
        yield from _stream(prompt)
        extra = _cite_block(cites)
        if extra:
            yield extra
    except Exception as e:
        print(f"🚨 Error streaming summary: {e}")
        yield f"Error generating summary: {str(e)}"
