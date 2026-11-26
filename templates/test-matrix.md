# Authorisation test matrix

Adapt every row to this application's real resources. Delete rows the product does not have. Add rows for every sensitive operation found in the API inventory.

Do not assume an administrator may read all private information. Where admin access is allowed, write the policy, not a blanket Allow.

Actors are synthetic. Status for each cell after execution: Allow, Deny, or Policy, then PASS, FAIL, or NOT TESTED.

| Operation | Guest | Owner | Other user | Other tenant | Admin | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| Read private profile | Deny | Allow | Deny | Deny | Policy | NOT TESTED |
| Update private profile | Deny | Allow | Deny | Deny | Policy | NOT TESTED |
| Read invoice | Deny | Allow | Deny | Deny | Policy | NOT TESTED |
| Read private message | Deny | Participant | Deny | Deny | Policy | NOT TESTED |
| Download private file | Deny | Allow | Deny | Deny | Policy | NOT TESTED |
| Change account role | Deny | Deny | Deny | Deny | Restricted | NOT TESTED |
| Export all users | Deny | Deny | Deny | Deny | Restricted | NOT TESTED |
| Redeem own coupon | Deny | Eligible | Deny | Deny | Policy | NOT TESTED |

## Coverage gaps

List sensitive operations that are not in the table yet.

## Notes

Unpredictable identifiers, hidden navigation, and frontend checks are not evidence for an Allow or Deny cell. Evidence is a server or database decision observed with a low-privilege identity.
