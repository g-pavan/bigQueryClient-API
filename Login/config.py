# config.py
SECRET_KEY = 'zDb8Q~IrASuHPJMuBRFikEWtpq2I5Axp2bILcdc9'  # Change this to a random secret key
CLIENT_ID = "5168674a-ec68-44c7-9e89-2b518a59e10a"
CLIENT_SECRET = "zDb8Q~IrASuHPJMuBRFikEWtpq2I5Axp2bILcdc9"
REDIRECT_URI = 'http://localhost:5000/get_token'
TENANT_ID = "6de5354b-f23a-492c-b7cb-d04a716bcbc1"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"  # Update with your Azure AD tenant ID
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0/me'