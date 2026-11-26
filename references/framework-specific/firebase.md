# Firebase

The rule expectations live in [database-security.md](../database-security.md).

- `allow read, write: if true` in a production rules file is a finding. Test mode left in place is a finding.
- Rules check `request.auth.uid` against the owner field on the document being read or written.
- Custom claims are set only by privileged server code. A client cannot write its own `admin` claim.
- Cloud Functions that import the Admin SDK authorise the caller before they use that SDK.
- Storage rules distinguish public marketing assets from private uploads.
- `firebase-adminsdk` credentials and private keys are not in the client or the repository.

Use the emulator tests the repository already has. Do not add the emulator unless the user approves that dependency.
