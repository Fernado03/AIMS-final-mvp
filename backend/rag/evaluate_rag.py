import json
from backend.rag.architecture.rag_service import RAGService
from backend.services.llm_service import (
    generate_assessment_from_notes,
    generate_plan_from_soap_notes,
    generate_summary_from_soap_note
)
from backend import config

def evaluate_rag_impact(patient_cases):
    """
    Evaluate the impact of RAG on clinical note generation by comparing
    outputs with and without RAG context.
    """
    rag_service = RAGService(
        corpus_path="backend/rag/corpus/clinical_practical_guide/"
    )
    
    for case in patient_cases:
        print(f"\n=== Evaluating Patient Case: {case['patient_id']} ===")
        
        # 1. Generate non-RAG outputs
        print("\n[Non-RAG Outputs]")
        non_rag_assessment = generate_assessment_from_notes(case['subjective_text'], case['objective_text'])
        non_rag_plan = generate_plan_from_soap_notes(case['subjective_text'], case['objective_text'], non_rag_assessment)
        non_rag_summary = generate_summary_from_soap_note(case['subjective_text'], case['objective_text'], non_rag_assessment, non_rag_plan)
        
        # 2. Retrieve relevant documents
        query_text = f"Subjective: {case['subjective_text']}\nObjective: {case['objective_text']}"
        try:
            retrieved_docs = rag_service.retrieve_relevant_documents(query_text) or []
            if not isinstance(retrieved_docs, list):
                print("\n[WARNING] Retrieved documents is not a list, using empty list instead")
                retrieved_docs = []
                
            print("\n[Retrieved Documents]")
            if retrieved_docs:
                for i, doc in enumerate(retrieved_docs, 1):
                    print(f"Document {i}:")
                    print(json.dumps(doc, indent=2))
            else:
                print("No documents retrieved")
        except (RuntimeError, ValueError) as e:
            print(f"\n[ERROR] Failed to retrieve documents: {str(e)}")
            retrieved_docs = []
            
        # 3. Generate RAG-augmented outputs
        print("\n[RAG-Augmented Outputs]")
        rag_assessment = generate_assessment_from_notes(case['subjective_text'], case['objective_text'])
        rag_plan = generate_plan_from_soap_notes(case['subjective_text'], case['objective_text'], rag_assessment)
        rag_summary = generate_summary_from_soap_note(case['subjective_text'], case['objective_text'], rag_assessment, rag_plan)
        
        # 4. Print side-by-side comparison
        print("\n[Comparison]")
        print("\nAssessment:")
        print(f"Non-RAG: {non_rag_assessment}")
        print(f"RAG: {rag_assessment}")
        
        print("\nPlan:")
        print(f"Non-RAG: {non_rag_plan}")
        print(f"RAG: {rag_plan}")
        
        print("\nSummary:")
        print(f"Non-RAG: {non_rag_summary}")
        print(f"RAG: {rag_summary}")

if __name__ == "__main__":
    # Example usage with test cases
    test_cases = [
        {
            "patient_id": "24680",
            "subjective_text": "Patient is a 45-year-old female presenting for a wellness check. Expresses concern about her weight and difficulty losing it. Reports a sedentary lifestyle due to a desk job and limited time for exercise. Diet consists of frequent fast food and sugary drinks. Complains of occasional knee pain and shortness of breath on exertion. Family history of type 2 diabetes and hypertension. Denies smoking, occasional alcohol.",
            "objective_text": "Height: 165 cm, Weight: 95 kg. BMI: 34.9 kg/m^2. Waist circumference: 105 cm. BP: 135/85 mmHg. Heart rate: 78 bpm. Random blood sugar: 115 mg/dL. Physical exam otherwise unremarkable. Appears well-nourished but with central adiposity."
        }
    ]
    evaluate_rag_impact(test_cases)