# Source note: the branch logs

- **System:** each branch keeps its own handout log: a spreadsheet at most branches, a donated point-of-sale program at B05 and B13.
- **Owner:** Hazem Al-Sulaim, branch operations lead. Branch supervisors upload a file every week.
- **What one row is:** one handout to one household on one day: parcels, total weight, who collected.
- **Extract:** 14 files `B01.csv.gz` to `B14.csv.gz`, 1 January to 30 September 2026, assembled on 2026-10-03.
- **Basis for use:** operational records of the network, used for planning under the same approval as the register, DS-2026-041.
- **Classification:** Restricted (household ids and the name of the person who collected).
- **Known limits:**
  - The date layout, the weight unit and the text encoding differ by branch and are not stated in the files.
  - `household_id` is typed by hand at some desks.
  - A week can be uploaded twice; a week can be missing. Nothing in a file says so.
  - The scale of B09 was away for repair from 4 to 17 May 2026.
