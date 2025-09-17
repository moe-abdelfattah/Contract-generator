# app.py
import os
from flask import Flask, jsonify, render_template
import google.generativeai as genai

# Initialize the Flask application
app = Flask(__name__)

# --- IMPORTANT: Set up your API Key ---
# Before running, set your API key in your terminal or deployment service:
# export GOOGLE_API_KEY='your_google_api_key_here'
try:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-pro')
except KeyError:
    print("🔴 Critical Error: GOOGLE_API_KEY environment variable not set.")
    model = None

# --- Your New, Detailed Saudi Arabian Contract Prompt ---
THE_SECRET_PROMPT = """
ROLE
You are an advanced legal AI specialized in Saudi Arabian contracts. Act as a Dynamic Contract Generator.
OBJECTIVE
Produce one fully synthetic, unique, Arabic contract (>= 5 pages equivalent) as a professionally formatted Markdown document (no code fences), with all variables auto-populated and full annex content generated inside the same document.
AUDIENCE & SCOPE
Audience: Legal/ops teams in KSA.
Scope: Official Saudi styles/terminology, drawing from the template corpus below.

CRITICAL CONSTRAINTS (Must follow exactly)
No placeholders: Every variable (party names, addresses, roles, project name, financials, dual dates Hijri & Gregorian with day of week, signatures) must be unique and fully populated. No brackets like [ ... ] may remain.
Length & depth: Content must clearly exceed a typical 5-page equivalent. Enforce with:
Scope of Work ≥ 600 words, split into 4–6 phases, each with 5–10 specific activities.
Fully generated Annexes A–D with real content (not descriptions).
Professional Markdown only:
Use # / ## / ### headings.
Use standard Markdown tables for all tabular data.
No JSON, no metadata, no commentary, no analysis—document text only.
Internal consistency:
Sums, percentages, and totals must reconcile (e.g., payment schedule = total contract value).
Dates must be coherent; the day of week must match the Gregorian date you generate.
Terminology must match the chosen base template (government vs commercial).
Language: Entire document in Arabic (RTL), including headings, tables, and labels.
KNOWLEDGE BASE (Choose exactly one base per generation)
Use one of the following as the structural/terminology base:
SA_GOV_CONSULTING_01 — Official Government (Consulting Services)
Terms: “الجهة الحكومية”، “المتعاقد”، “نظام المنافسات والمشتريات الحكومية”
Format: وثيقة أساسية + شروط مفصلة
Clauses to reflect: المحتوى المحلي، حقوق الملكية الفكرية، تعارض المصالح، السرية وحماية المعلومات
Mechanism: تعاقد مباشر لخدمات محددة
SA_GOV_GENERAL_SERVICES_02 — Official Government (General Services)
Personnel, materials, equipment clauses; two-part format
SA_GOV_MILITARY_SUPPLY_03 — Official Government (Military Supply)
Export licenses, GAMI industrial participation, military-grade packaging/docs
Acceptance flow: FAT → SAT → UAT (sequential preconditions)
PVT_COMMERCIAL_SUPPLY_04 — Private B2B (Goods Supply)
Simple linear structure (price/payment, delivery, warranty)
SA_GOV_CONSTRUCTION_GENERAL_11 — Official Government (General Construction)
Site handover, preliminary/final acceptance, defects liability, insurances (CAR/PI)
Central role of “المهندس”
SA_GOV_OM_12 — Official Government (Operation & Maintenance)
KPIs, SLAs, preventive maintenance schedule; payments tied to KPIs
SA_FRAMEWORK_SUPPLY_07 — Official Government (Framework Agreement)
Term length, ceiling value, no procurement on signature; purchases via later POs
SA_GOV_ENG_SUPERVISION_13 — Official Government (Engineering Supervision)
Consultant authority/responsibility; professional liability
GENERATION PLAN (Deterministic steps)
Select Base & Scenario
Randomly choose a baseTemplateId from the list above.
Write a one-sentence scenario describing what this contract is about (Arabic).
Parties (Create unique, Saudi-plausible details)
For two parties: full legal names, legal form, CR or identifier (synthetic), full addresses, city, and authorized representative (name + title).
Keep style coherent with base template (e.g., “الجهة الحكومية/المتعاقد” or “المشتري/البائع”).
Project Details
Generate a unique projectName.
Write a 2–3 sentence background for the preamble (الديباجة).
Financials
Generate contractValueNumeric (SAR), plus plausible percentages for guarantees, advances, retention, penalties (late delivery, SLA breach, KPI miss, etc. per template).
Dual Calendar Date & Place
Generate a future Gregorian date and the matching Hijri date and day of week (e.g., “يوم الأربعاء”).
Choose a Saudi city for signing location.
Document Structure (Sections)
Government bases: 12–18 main sections. Commercial bases: 8–12.
Titles should reflect the template’s key clauses and add unique, scenario-specific sections.
Reorder secondary sections for structural uniqueness.
Write Content
Preamble (الديباجة): party details + city + day of week + dual dates (Hijri/Gregorian).
Scope of Work (نطاق العمل): ≥600 words; 4–6 phases, each with 5–10 concrete activities; include a ‘المخرجات الرئيسية’ subsection listing 5–8 distinct deliverables tied to phases.
Specifications (المواصفات): create detailed specs and tables.
If personnel are relevant, include a table with columns: المسمى الوظيفي | المؤهل | الشهادات | الخبرة | المسؤوليات (4–6 roles).
Include all template-relevant clauses (e.g., IP, confidentiality, SLAs/KPIs, acceptance stages, insurances, site handover, conflict of interest, local content, etc.).
Signatures: populate names/titles; include space/lines as text.
Annexes (Generate content, not descriptions)
الملحق (أ) — نطاق العمل والمواصفات الفنية
Reiterate SoW and add 3–5 specific technical requirements/standards.
الملحق (ب) — الجدول الزمني التفصيلي
A Markdown table with Phase | Milestone | Deliverable | Estimated Completion (Hijri/Gregorian) | Responsibilities
Include 10–15 unique milestones.
الملحق (ج) — جدول الغرامات والجزاءات
Markdown table with Violation Type | Description | Penalty Calculation | Max Penalty
Include 5–7 violations, aligned to the chosen base (e.g., KPI misses, late delivery, QA failure, safety breach).
الملحق (د) — جدول الأسعار والدفعات
Markdown table: line items that map to SoW phases/deliverables; total must equal contractValueNumeric; show payment triggers (acceptance, KPI achievement, timeline gates).
Optional 1–2 extra annexes (random): e.g., خطة إدارة المخاطر، خطة ضمان الجودة، مصفوفة أصحاب المصلحة—write substantial content.

STRUCTURE & FORMATTING RULES
Use Arabic headings with Markdown:
 # عنوان العقد → top title; ## for main sections; ### for subsections.
Use only standard Markdown tables (no HTML).
Use numbered lists/bullets where it enhances clarity.
Keep RTL punctuation natural; avoid mixing English unless required for clarity in tables (prefer Arabic labels).
CONSISTENCY & VALIDATION RULES
Payment schedule sums to exact contract value.
Percentages/retentions/penaltalities are consistent across sections and annexes.
Acceptance stages (if applicable) appear in both body and timeline annex.
SLAs/KPIs (if applicable) appear in body and are enforced by penalties annex.
The day of week matches the Gregorian date you used.
Preamble details (city, parties, dates) match signatures and annex headers.
No leftover placeholders, brackets, or English scaffolding text.


OUTPUT SPEC (Strict)
Final output = the contract document only (Arabic).
Do not include analysis, notes, JSON, or code fences.
End with a closing statement that includes the Hijri and Gregorian dates again.
QUALITY BAR (Implicit heuristics)
Use realistic figures for KSA procurement contexts.
Use template-appropriate terminology (e.g., “نظام المنافسات والمشتريات الحكومية” for gov contracts).
Avoid repetition; vary phrasing and order of secondary sections each run.
SELF-CHECKLIST (Run before you output)
No [placeholder] or English scaffolding remains.
SoW ≥ 600 words with 4–6 phases; each phase has 5–10 concrete activities.
‘المخرجات الرئيسية’ lists 5–8 deliverables tied to phases.
All required tables are present and properly formatted in Markdown.
Annexes A–D fully written (not mere descriptions); 10–15 milestones in Annex B; 5–7 violations in Annex C; Annex D totals = contract value.
Dual date + matching day of week + city appear in preamble, and dates re-appear in closing.
Payment triggers and penalties align with body clauses (SLA/KPI/acceptance).
Names, roles, addresses, reps, signatures fully populated and realistic for KSA.
Government vs commercial tone and clauses match the chosen base template.
Final output is Arabic Markdown only, no JSON, no explanations.
"""

# This function serves the main webpage (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# This is the API endpoint that the button click calls
@app.route('/generate-contract', methods=['POST'])
def generate_contract_api():
    if model is None:
        return jsonify({'error': 'Server is not configured with an API key.'}), 500
    
    try:
        # Call the Gemini API with your secret prompt
        response = model.generate_content(THE_SECRET_PROMPT)
        contract_text = response.text
        return jsonify({'contract_text': contract_text})
    except Exception as e:
        print(f"An error occurred during API call: {e}")
        return jsonify({'error': 'Failed to generate contract due to an internal error.'}), 500

if __name__ == '__main__':
    app.run(debug=True)
