# Django

- `DEBUG` is false in production settings. The production secret key is not the generated default and is not committed.
- CSRF protection stays enabled for cookie-authenticated browser forms.
- Views and DRF permission classes check the object owner. A queryset filtered only in the template is not authorisation.
- Raw SQL uses parameters. Identifiers that must be dynamic come from an allowlist.
- `ALLOWED_HOSTS` is explicit. Open redirects do not use an unvalidated `next` parameter.
- Media uploads follow the file rules in [data-privacy.md](../data-privacy.md).

Mark NOT APPLICABLE when the repository is not a Django project.
