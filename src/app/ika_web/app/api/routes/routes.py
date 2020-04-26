from src.app.ika_web.app.api.resources.login import SignupApi, LoginApi
from src.app.ika_web.app.api.resources.credential import CredentialsApi, CredentialApi
from src.app.ika_web.app.api.resources.reset_password import ForgotPassword, ResetPassword

def initialize_routes(api):
    api.add_resource(CredentialsApi, '/api/v1/credentials')
    api.add_resource(CredentialApi, '/api/v1/credentials/<id>')
    
    api.add_resource(SignupApi, '/api/v1/auth/signup')
    api.add_resource(LoginApi, '/api/v1/auth/login')
    api.add_resource(ForgotPassword, '/api/v1/auth/forgot')
    api.add_resource(ResetPassword, '/api/v1/auth/reset')
