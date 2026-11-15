# Source note: the donations API

- **System:** the donations intake service. Every delivery of food to a branch is weighed and recorded on arrival.
- **Owner:** Talal Al-Wabil, donations systems engineer.
- **Access:** `GET /v1/donations?page=<n>&per_page=<up to 200>`. The answer has `page`, `per_page`, `total` (the number of distinct donations), `next` (the address of the next page, or null) and `data`. Records are served oldest first. A busy service answers 503: wait and ask again.
- **What one record is:** one delivery: `donation_id`, `received_at` (with its UTC offset), `branch_id`, `donor_type`, `category`, `weight`, `unit`, `est_value_sar`.
- **Coverage:** 1 January to 28 September 2026, read on 2026-10-04. The service is live: records keep arriving while you page.
- **Basis for use:** internal operational data; donor names are not served by this API. Approval DS-2026-041.
- **Classification:** Restricted.
- **Known limits:**
  - `donor_type` is null when an individual donor asked to stay anonymous.
  - Some retailers report weight in pounds; `unit` says which.
  - `est_value_sar` is an estimate made by the receiving clerk.
