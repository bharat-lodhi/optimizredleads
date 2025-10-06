# OptimizedLeads Starter

This is a starter Django project for OptimizedLeads with:
- custom user model (no Django admin)
- manual HTML forms (no forms.py)
- Central Admin, Sub Admin, Subscriber dashboards
- Leads app with export helpers (CSV/Excel/PDF)

## Quick start

1. Create & activate virtualenv (Windows):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Make migrations and migrate:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Run server:
   ```
   python manage.py runserver
   ```

## Notes
- Change SECRET_KEY in optimizedleads/settings.py for production.
- This starter uses a simple CustomUser model (not tied to Django auth backend).
"# Optimizredleads" 
