# Source note: the beneficiary register

- **System:** the registration system of Ghilal Food Bank Network. Each of the 14 branches enters households at its desk; the call centre and the online form write to the same register.
- **Owner:** Widad Al-Ghunaim, registration supervisor. Requests go through her; the data protection officer, Ruqayyah Al-Marzouqi, approves each extract.
- **What one row is:** one registration of one household. A household that registers again at another branch gets a second row with the same `household_id`.
- **Extract:** `registrations_extract.csv.gz`, taken on 2026-10-04 by appending the 14 branch exports. Registrations from 2021-01-03 to 2026-09-28. The register is refreshed every night; the extract is not.
- **Basis for use:** households consent at registration to the use of their data for delivering and planning food support. The analysis team receives the extract under the internal data-sharing procedure of the network, approval DS-2026-041, for the purpose "service coverage analysis, Q3 2026". No onward sharing of identified records.
- **Classification:** Restricted (personal data of beneficiaries, a vulnerable group).
- **Known limits:**
  - `household_size` and `monthly_income_sar` are reported by the household and are not verified at registration.
  - Before 2025-03-01 the paper form of branches B03 and B11 had no field for household size.
  - The online form and the call-centre script offer household sizes 1 to 6 only.
  - Branch exports are not in one text encoding.
  - Households that never registered are not in the register, whatever their need.
- **Audit:** `audit_resurvey.csv`, 600 home visits in September 2026 in which the household size was verified.
