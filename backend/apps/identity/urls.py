from django.urls import path
from .views import (
    OtpRequestView,
    OtpVerifyView,
    RefreshTokenView,
    PasskeyRegisterOptionsView,
    PasskeyRegisterVerifyView,
    PasskeyLoginOptionsView,
    PasskeyLoginVerifyView,
    DeviceListCreateView,
    DeviceDetailView,
    GoogleAuthView,
    GoogleOAuthStartView,
    GoogleOAuthCallbackView,
)

urlpatterns = [
    path("otp/request", OtpRequestView.as_view(), name="auth_otp_request"),
    path("otp/request/", OtpRequestView.as_view(), name="auth_otp_request_slash"),
    path("otp/verify", OtpVerifyView.as_view(), name="auth_otp_verify"),
    path("otp/verify/", OtpVerifyView.as_view(), name="auth_otp_verify_slash"),
    path("google", GoogleAuthView.as_view(), name="auth_google"),
    path("google/", GoogleAuthView.as_view(), name="auth_google_slash"),
    path("google/oauth/start", GoogleOAuthStartView.as_view(), name="auth_google_oauth_start"),
    path("google/oauth/start/", GoogleOAuthStartView.as_view(), name="auth_google_oauth_start_slash"),
    path("google/callback", GoogleOAuthCallbackView.as_view(), name="auth_google_callback"),
    path("google/callback/", GoogleOAuthCallbackView.as_view(), name="auth_google_callback_slash"),

    path("refresh", RefreshTokenView.as_view(), name="auth_refresh"),
    path("passkeys/register/options", PasskeyRegisterOptionsView.as_view(), name="auth_passkeys_register_options"),
    path("passkeys/register/verify", PasskeyRegisterVerifyView.as_view(), name="auth_passkeys_register_verify"),
    path("passkeys/login/options", PasskeyLoginOptionsView.as_view(), name="auth_passkeys_login_options"),
    path("passkeys/login/verify", PasskeyLoginVerifyView.as_view(), name="auth_passkeys_login_verify"),
    path("devices", DeviceListCreateView.as_view(), name="auth_devices"),
    path("devices/<uuid:device_id>", DeviceDetailView.as_view(), name="auth_device_detail"),
]
