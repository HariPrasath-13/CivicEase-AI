"""
Script to create realistic sample government documents (PDF, DOCX, TXT) for CivicEase AI evaluation.
"""
from pathlib import Path

SAMPLE_DIR = Path(__file__).parent
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)

# Sample 1: Old Age Pension Scheme Directive (Complex, Legalese, Missing Fee/Time)
PENSION_TEXT = """GOVERNMENT OF TAMIL NADU
SOCIAL WELFARE AND WOMEN EMPOWERMENT DEPARTMENT
G.O. (Ms) No. 142 / SW-2026

SUBJECT: Guidelines and Revised Directives pertaining to the Sanction of Financial Assistance under the Integrated Old Age Pension Scheme (OAPS) — Regarding.

1. PREAMBLE & JURISDICTION:
Whereas the Government has deemed it expedient to revise and streamline the administrative instructions for disbursement of monthly financial grants to indigent senior citizens, the competent authority hereby notifies the consolidated operational regulations hereinafter set forth.

2. ELIGIBILITY CRITERIA:
The applicant shall be a permanent resident and bona fide domicile of the State having attained the age of 60 years or above on the date of submission. The total annual household income of the applicant from all pecuniary sources whatsoever shall not exceed Rs. 1,00,000/- (Rupees One Lakh only). Notwithstanding anything contained in previous circulars, persons possessing non-encumbered agricultural land exceeding 2.5 acres shall stand debarred from seeking financial sanction under this scheme.

3. REQUISITE ATTACHMENTS & DOCUMENTATION:
Every applicant shall furnish the requisite documentary proofs to substantiate their claim, inter alia:
(a) Copy of Aadhaar Card duly self-attested.
(b) Domicile / Residence Certificate issued by the Revenue Authority.
(c) Age Proof Certificate from a Competent Medical Officer or recognized Birth Register.
(d) Non-encumbrance certificate pertaining to immovable family property, if applicable.

4. APPLICATION PROCEDURE & SUBMISSION:
The applicant shall furnish the application in the prescribed proforma complete in all respects to the concerned authority within the prescribed period. Incomplete applications or submissions lacking appropriate documents shall be summarily rejected without assigning any reason thereof. Scrutiny of the aforementioned records shall be undertaken by the designated scrutiny committee prior to formal empanelment.

5. GENERAL CONDITIONS:
The sanction of monthly pension shall remain subject to budgetary allocations and at the absolute discretion of the sanctioning committee. Any false undertaking or misrepresentation shall invite immediate forfeiture of all benefits and penal proceedings under the relevant statute."""

# Write TXT version
with open(SAMPLE_DIR / "TamilNadu_OldAge_Pension_Scheme.txt", "w", encoding="utf-8") as f:
    f.write(PENSION_TEXT)

# Sample 2: Healthcare Subsidy (Disability Assistance)
HEALTHCARE_TEXT = """DIRECTORATE FOR EMPOWERMENT OF PERSONS WITH DISABILITIES
NOTIFICATION NO. HC-89/2026

OPERATIONAL GUIDELINES FOR FINANCIAL ASSISTANCE TOWARDS ASSISTIVE MEDICAL DEVICES

1. OBJECTIVE:
This notification pertains to the grant of financial subsidies for the procurement of specialized assistive aids and orthopedic appliances for persons with permanent physical benchmark disabilities.

2. ELIGIBILITY AND ADMISSIBILITY:
Any citizen having a certified benchmark disability of not less than 40% as verified by an authorized Medical Board shall be eligible to seek assistance. The applicant must furnish a valid Unique Disability ID (UDID) card and proof of local residence.

3. SUBMISSION OF CLAIMS:
All claims must be remitted through the prescribed application format. The requisite quotation from an empanelled medical manufacturer along with the doctor's prescription must be attached. The completed dossier shall be forwarded to the competent authority for necessary administrative sanction.

4. FEE AND FINANCIAL DISBURSEMENT:
There is no application fee payable by eligible applicants for this assistance scheme. The sanctioned subsidy amount shall be credited directly to the verified bank account of the beneficiary upon receipt of formal approval.

5. GRIEVANCES AND APPEALS:
Any grievance arising out of non-sanction may be represented before the District Welfare Committee within 30 days of receipt of order."""

with open(SAMPLE_DIR / "Disability_Healthcare_Subsidy_Directive.txt", "w", encoding="utf-8") as f:
    f.write(HEALTHCARE_TEXT)

# Sample 3: Ration Card Address Revision
RATION_CARD_TEXT = """CIVIL SUPPLIES AND CONSUMER PROTECTION DEPARTMENT
PUBLIC DISTRIBUTION SYSTEM — CITIZEN CHARTER & GUIDELINES

SUBJECT: Standard Operating Procedure for Addition of Family Members and Address Modification in Smart Family Ration Cards.

1. OVERVIEW:
Citizens desiring to modify their residential address or append new family members in their existing Smart Family Card may submit an application as outlined herein.

2. REQUIRED DOCUMENTS:
Applicants must attach copies of:
- Existing Smart Ration Card copy
- Aadhaar Card of the member to be added
- Birth Certificate in case of child addition / Marriage Certificate for spouse addition
- Proof of new residence (Electricity Bill / Property Tax Receipt / Gas Connection Receipt)

3. HOW TO APPLY:
Step 1: Visit the official Tamil Nadu Public Distribution portal at https://www.tnpds.gov.in or visit your local e-Seva Centre.
Step 2: Select 'Smart Card Services' -> 'Change of Address' or 'Add Member'.
Step 3: Upload clear scanned copies of the supporting documents.
Step 4: Note down the generated reference number for tracking.

4. PROCESSING TIMELINE AND FEES:
Processing time: 15 working days from the date of submission.
Application Fee: Free of cost (No fee is levied by the Department).

5. HELPLINE & CITIZEN SUPPORT:
Toll-Free Helpline: 1967 / 1800-425-5901
Email: support@tnpds.gov.in
Office: Taluk Supply Office / Assistant Commissioner Office (Civil Supplies)"""

with open(SAMPLE_DIR / "Ration_Card_Revision_Guidelines.txt", "w", encoding="utf-8") as f:
    f.write(RATION_CARD_TEXT)

print("Sample documents generated successfully!")
