# rag/prompt_service.py

def get_assessment_prompt(subjective_text: str, objective_text: str, rag_context: str) -> str:
    """Generate the assessment prompt with clinical context."""
    assessment_template = (
        """
        ASSESSMENT

        Diagnosis / Impression:
        - {Summarize the patient's condition(s) as concluded from the subjective and objective data}
        - Include both primary and secondary diagnoses using bullet points
        - Keep each diagnosis concise (1-2 lines maximum)

        Differential Diagnosis (DDx):
        1. If no definitive diagnosis, list possible diagnoses in order of likelihood
        2. Include brief rationale for each (1 sentence)
        3. Limit to 3-5 most likely diagnoses
        """
    )

    return (
        "You are an AI medical assistant. Your task is to generate the ASSESSMENT section of a medical SOAP note.\n"
        f"{rag_context}\n"
        "Use the provided Subjective and Objective information to create a concise and clinically relevant Assessment.\n"
        "The Assessment section must follow this format exactly: \n"
        f"{assessment_template}\n"
        "SUBJECTIVE:\n"
        f"{subjective_text}\n"
        "OBJECTIVE:\n"
        f"{objective_text}\n"
        "Generate only the Assessment section. Do not include any additional headings or text before 'Diagnosis / Impression:'."
    )


def get_plan_prompt(subjective_text: str, objective_text: str, assessment_text: str, rag_context: str) -> str:
    """Generate the plan prompt with clinical context."""
    plan_template = (
        """
        PLAN

        Diagnostics / Tests Ordered:
        1. [List each test on a new numbered line]
        2. Include brief rationale for each test (1 sentence)
        3. Group related tests together

        Medications / Therapy:
        - [List each medication/therapy on a new bullet point]
        - Include: name, dose, frequency, duration
        - Highlight any changes to existing medications

        Referrals / Consults:
        - [List each referral on a new bullet point]
        - Include: specialty, urgency, reason

        Patient Education and Counseling:
        - [List key education points as bullet points]
        - Keep each point concise (1 sentence)
        - Focus on actionable items

        Follow-Up Instructions:
        1. Specify exact timing for follow-up
        2. Include clear return instructions if symptoms worsen
        3. Provide contact method for questions
        """
    )

    return (
        "You are an AI medical assistant. Based on the provided Subjective, Objective, and Assessment sections of a SOAP note, generate the PLAN section.\n"
        f"{rag_context}\n"
        "The Plan section must include the following items in order: Diagnostics / Tests Ordered; Medications / Therapy; Referrals / Consults; Patient Education and Counseling; Follow-Up Instructions.\n"
        "Use this exact format: \n"
        f"{plan_template}\n"
        "SUBJECTIVE:\n"
        f"{subjective_text}\n"
        "OBJECTIVE:\n"
        f"{objective_text}\n"
        "ASSESSMENT:\n"
        f"{assessment_text}\n"
        "Generate only the Plan section. Do not include any other headings or notes."
    )


def get_summary_prompt(subjective_text: str, objective_text: str, assessment_text: str, plan_text: str, rag_context: str) -> str:
    """Generate the summary prompt with clinical context."""
    summary_template = (
        """
        SUMMARY
        
        Key Findings:
        - [List 2-3 most important subjective/objective findings]
        
        Clinical Assessment:
        - [State primary diagnosis or working diagnosis]
        - [Note any critical differentials if applicable]
        
        Management Plan:
        - [Highlight 2-3 most important plan items]
        - [Note any urgent actions needed]
        """
    )
    
    return (
        "You are an AI medical assistant. Based on the complete SOAP note below (Subjective, Objective, Assessment, and Plan), generate a structured clinical summary.\n"
        f"{rag_context}\n"
        "Use this exact format with bullet points for clarity:\n"
        f"{summary_template}\n"
        "SUBJECTIVE:\n"
        f"{subjective_text}\n"
        "OBJECTIVE:\n"
        f"{objective_text}\n"
        "ASSESSMENT:\n"
        f"{assessment_text}\n"
        "PLAN:\n"
        f"{plan_text}\n"
        "Generate only the clinical summary. Do not repeat headings or templates."
    )
