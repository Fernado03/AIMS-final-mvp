import traceback
from openai import OpenAI
from backend.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from backend.rag.rag_service import get_clinical_guidelines_context

llm_client = None
try:
    llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL, timeout=120)
    print(f"✅ LLM initialized: {LLM_MODEL} @ {LLM_BASE_URL}")
except Exception as e:
    print(f"⚠️ Error initializing LLM: {e}\n{traceback.format_exc()}")


def _cite_block(cites):
    if not cites:
        return ""
    return "\n\nSources:\n" + "\n".join(f"- {c}" for c in cites)


def _cite(text, cites):
    extra = _cite_block(cites)
    return (text.rstrip() + extra) if text and extra else text


def _assessment_prompt(s, o, rag):
    return (
        "You are an AI medical assistant. Your task is to generate the ASSESSMENT section of a medical SOAP note.\n"
        f"{rag}\n"
        "Use the provided Subjective and Objective information to create a concise and clinically relevant Assessment.\n"
        "The Assessment section must follow this format exactly: \n"
        "ASSESSMENT\n\n"
        "Diagnosis / Impression:\n"
        "- {Summarize the patient's condition(s) as concluded from the subjective and objective data}\n"
        "- Include both primary and secondary diagnoses using bullet points\n"
        "- Keep each diagnosis concise (1-2 lines maximum)\n\n"
        "Differential Diagnosis (DDx):\n"
        "1. If no definitive diagnosis, list possible diagnoses in order of likelihood\n"
        "2. Include brief rationale for each (1 sentence)\n"
        "3. Limit to 3-5 most likely diagnoses\n"
        "SUBJECTIVE:\n"
        f"{s}\n"
        "OBJECTIVE:\n"
        f"{o}\n"
        "Generate only the Assessment section. Do not include any additional headings or text before 'Diagnosis / Impression:'."
    )


def _plan_prompt(s, o, a, rag):
    return (
        "You are an AI medical assistant. Based on the provided Subjective, Objective, and Assessment sections of a SOAP note, generate the PLAN section.\n"
        f"{rag}\n"
        "The Plan section must include the following items in order: Diagnostics / Tests Ordered; Medications / Therapy; Referrals / Consults; Patient Education and Counseling; Follow-Up Instructions.\n"
        "Use this exact format: \n"
        "PLAN\n\n"
        "Diagnostics / Tests Ordered:\n"
        "1. [List each test on a new numbered line]\n"
        "2. Include brief rationale for each test (1 sentence)\n"
        "3. Group related tests together\n\n"
        "Medications / Therapy:\n"
        "- [List each medication/therapy on a new bullet point]\n"
        "- Include: name, dose, frequency, duration\n"
        "- Highlight any changes to existing medications\n\n"
        "Referrals / Consults:\n"
        "- [List each referral on a new bullet point]\n"
        "- Include: specialty, urgency, reason\n\n"
        "Patient Education and Counseling:\n"
        "- [List key education points as bullet points]\n"
        "- Keep each point concise (1 sentence)\n"
        "- Focus on actionable items\n\n"
        "Follow-Up Instructions:\n"
        "1. Specify exact timing for follow-up\n"
        "2. Include clear return instructions if symptoms worsen\n"
        "3. Provide contact method for questions\n"
        "SUBJECTIVE:\n"
        f"{s}\n"
        "OBJECTIVE:\n"
        f"{o}\n"
        "ASSESSMENT:\n"
        f"{a}\n"
        "Generate only the Plan section. Do not include any other headings or notes."
    )


def _summary_prompt(s, o, a, p, rag):
    return (
        "You are an AI medical assistant. Based on the complete SOAP note below (Subjective, Objective, Assessment, and Plan), generate a structured clinical summary.\n"
        f"{rag}\n"
        "Use this exact format with bullet points for clarity:\n"
        "SUMMARY\n\n"
        "Key Findings:\n"
        "- [List 2-3 most important subjective/objective findings]\n\n"
        "Clinical Assessment:\n"
        "- [State primary diagnosis or working diagnosis]\n"
        "- [Note any critical differentials if applicable]\n\n"
        "Management Plan:\n"
        "- [Highlight 2-3 most important plan items]\n"
        "- [Note any urgent actions needed]\n"
        "SUBJECTIVE:\n"
        f"{s}\n"
        "OBJECTIVE:\n"
        f"{o}\n"
        "ASSESSMENT:\n"
        f"{a}\n"
        "PLAN:\n"
        f"{p}\n"
        "Generate only the clinical summary. Do not repeat headings or templates."
    )


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


def _stream_with_cites(prompt, cites, label):
    if not llm_client:
        yield "Error: LLM not available."
        return
    try:
        print(f"🧠 STREAMING {label}...")
        yield from _stream(prompt)
        extra = _cite_block(cites)
        if extra:
            yield extra
    except Exception as e:
        print(f"🚨 Error streaming {label}: {e}")
        yield f"Error generating {label}: {str(e)}"


def stream_assessment_from_notes(subjective_text, objective_text):
    rag, cites = get_clinical_guidelines_context(f"Subjective: {subjective_text}\nObjective: {objective_text}")
    yield from _stream_with_cites(_assessment_prompt(subjective_text, objective_text, rag), cites, "assessment")


def stream_plan_from_soap_notes(subjective_text, objective_text, assessment_text):
    rag, cites = get_clinical_guidelines_context(
        f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}"
    )
    yield from _stream_with_cites(_plan_prompt(subjective_text, objective_text, assessment_text, rag), cites, "plan")


def generate_summary_from_soap_note(subjective_text, objective_text, assessment_text, plan_text):
    if not llm_client:
        print("LLM not available for summary generation.")
        return None
    rag, cites = get_clinical_guidelines_context(
        f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}\nPlan: {plan_text}"
    )
    try:
        print("🤖 Sending prompt to LLM for SUMMARY generation...")
        text = _complete(_summary_prompt(subjective_text, objective_text, assessment_text, plan_text, rag))
        print(f"✅ LLM generated summary: {text[:200]}...")
        return _cite(text, cites)
    except Exception as e:
        print(f"Error calling LLM for summary generation: {e}\n{traceback.format_exc()}")
        return None
