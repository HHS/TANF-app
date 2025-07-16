{{- with secret "database/creds/django-dynamic-role" -}}
{
  "ENGINE": "django.db.backends.postgresql",
  "NAME": "tdrs_test",
  "USER": "{{ .Data.username }}",
  "PASSWORD": "{{ .Data.password }}",
  "HOST": "postgres",
  "PORT": "5432"
}
{{- else -}}
{
  "error": "Failed to retrieve database credentials"
}
{{- end -}}
