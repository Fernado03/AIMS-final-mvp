# services/llm_service.py

import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
import traceback
import numpy as np
from backend.config import VERTEX_AI_PROJECT_ID, VERTEX_AI_LOCATION, VERTEX_AI_MODEL_NAME
from backend.rag.knowledge_base_service import KnowledgeBaseService
from backend.rag.prompt_service import get_assessment_prompt, get_plan_prompt, get_summary_prompt

gemini_model = None
kb_service = KnowledgeBaseService()

try:
    vertexai.init(project=VERTEX_AI_PROJECT_ID, location=VERTEX_AI_LOCATION)
    gemini_model = GenerativeModel(VERTEX_AI_MODEL_NAME)
    print(f"Vertex AI initialized and Gemini model '{gemini_model._model_name}' loaded successfully in project '{VERTEX_AI_PROJECT_ID}' location '{VERTEX_AI_LOCATION}'.")
except Exception as e:
    print(f"⚠️ Error initializing Vertex AI or Gemini model: {e}\n{traceback.format_exc()}")
    gemini_model = None

def generate_assessment_from_notes(subjective_text, objective_text):
    if not gemini_model:
        print("⚠️ Gemini model not available. Skipping assessment generation.")
        return None

    # Get relevant clinical guidelines context
    query_text = f"Subjective: {subjective_text}\nObjective: {objective_text}"
    rag_context = kb_service.get_clinical_guidelines_context(query_text)

    prompt = get_assessment_prompt(subjective_text, objective_text, rag_context)
    try:
        print(f"🧠 Generating assessment for S: '{subjective_text[:100]}...', O: '{objective_text[:100]}...'")
        response = gemini_model.generate_content(prompt)
        if response and response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            generated_text = response.candidates[0].content.parts[0].text.strip()
            print(f"✅ Gemini generated assessment: {generated_text[:200]}...")
            if "Diagnosis / Impression:" in generated_text or "Differential Diagnosis (DDx):" in generated_text:
                return generated_text
            else:
                print(f"⚠️ Gemini response did not seem to contain a valid assessment structure: {generated_text[:200]}...")
                return None
        else:
            print(f"⚠️ Gemini response was empty or malformed: {response}")
            return None
    except Exception as e:
        print(f"🚨 Error calling Gemini API or processing response: {e}\n{traceback.format_exc()}")
        return None

def generate_plan_from_soap_notes(subjective_text, objective_text, assessment_text):
    if not gemini_model:
        print("⚠️ Gemini model not available for plan generation.")
        return None

    # Get relevant clinical guidelines context
    query_text = f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}"
    rag_context = kb_service.get_clinical_guidelines_context(query_text)

    full_prompt = get_plan_prompt(subjective_text, objective_text, assessment_text, rag_context)
    try:
        print(f"🤖 Sending prompt to Gemini for PLAN generation (Note ID context)...")
        response = gemini_model.generate_content(full_prompt)
        generated_plan = ""
        if response.candidates and response.candidates[0].content.parts:
            generated_plan = response.candidates[0].content.parts[0].text.strip()

        if "PLAN" not in generated_plan.upper() and not any(kw in generated_plan.upper() for kw in ["DIAGNOSTICS", "MEDICATIONS", "THERAPY", "REFERRALS", "EDUCATION", "FOLLOW-UP"]):
            print(f"⚠️ Gemini response might not be a valid plan: {generated_plan[:200]}...")

        print(f"✅ Gemini generated plan (Note ID context): {generated_plan[:200]}...")
        return generated_plan
    except Exception as e:
        print(f"Error calling Gemini API for plan generation: {e}\n{traceback.format_exc()}")
        return None

def generate_summary_from_soap_note(subjective_text, objective_text, assessment_text, plan_text):
    if not gemini_model:
        print("Gemini model not available for summary generation.")
        return None

    # Get relevant clinical guidelines context
    query_text = f"Subjective: {subjective_text}\nObjective: {objective_text}\nAssessment: {assessment_text}\nPlan: {plan_text}"
    rag_context = kb_service.get_clinical_guidelines_context(query_text)

    prompt = get_summary_prompt(subjective_text, objective_text, assessment_text, plan_text, rag_context)
    try:
        print(f"🤖 Sending prompt to Gemini for SUMMARY generation...")
        response = gemini_model.generate_content(prompt)
        generated_summary = ""
        if response.candidates and response.candidates[0].content.parts:
            generated_summary = response.candidates[0].content.parts[0].text.strip()

        print(f"✅ Gemini generated summary: {generated_summary[:200]}...")
        return generated_summary
    except Exception as e:
        print(f"Error calling Gemini API for summary generation: {e}\n{traceback.format_exc()}")
        return None