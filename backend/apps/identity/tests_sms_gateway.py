"""Unit tests for Android SMS Gateway OTP Provider."""
import unittest
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase, override_settings
from apps.identity.services.otp import (
    AndroidSmsGatewayOtpProvider,
    get_otp_provider,
    OtpService,
)


class AndroidSmsGatewayOtpProviderTestCase(SimpleTestCase):
    """Test suite for capcom6/android-sms-gateway provider integration."""

    @override_settings(
        SMS_GATEWAY_USER="test_user",
        SMS_GATEWAY_PASSWORD="test_password",
        SMS_GATEWAY_URL="https://api.sms-gate.app/3rdparty/v1/messages",
        SMS_GATEWAY_SIM_NUMBER=1,
    )
    @patch("requests.post")
    def test_send_otp_success_cloud_mode(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"id": "msg-123456", "state": "Pending"}
        mock_resp.content = b'{"id": "msg-123456"}'
        mock_post.return_value = mock_resp

        provider = AndroidSmsGatewayOtpProvider()
        result = provider.send_otp(phone="+919876543210", code="482910", language="en")

        self.assertTrue(result)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args

        # Verify target endpoint
        self.assertEqual(args[0], "https://api.sms-gate.app/3rdparty/v1/messages")

        # Verify Basic Auth
        self.assertEqual(kwargs["auth"], ("test_user", "test_password"))

        # Verify JSON payload
        payload = kwargs["json"]
        self.assertEqual(payload["phoneNumbers"], ["+919876543210"])
        self.assertIn("482910", payload["textMessage"]["text"])
        self.assertEqual(payload["simNumber"], 1)

    @override_settings(
        SMS_GATEWAY_USER="admin",
        SMS_GATEWAY_PASSWORD="secretpassword",
        SMS_GATEWAY_URL="http://192.168.1.50:8080",
        SMS_GATEWAY_SIM_NUMBER=2,
    )
    @patch("requests.post")
    def test_send_otp_local_mode_url_normalization(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"status": "ok"}
        mock_resp.content = b'{"status": "ok"}'
        mock_post.return_value = mock_resp

        provider = AndroidSmsGatewayOtpProvider()
        result = provider.send_otp(phone="+919876543210", code="112233", language="hi")

        self.assertTrue(result)
        args, kwargs = mock_post.call_args

        # Local mode URL normalization appends /message
        self.assertEqual(args[0], "http://192.168.1.50:8080/message")
        self.assertEqual(kwargs["json"]["simNumber"], 2)
        self.assertIn("112233", kwargs["json"]["textMessage"]["text"])

    @override_settings(
        SMS_GATEWAY_USER="",
        SMS_GATEWAY_PASSWORD="",
    )
    def test_send_otp_fallback_when_unconfigured(self):
        """When credentials are blank, provider gracefully logs simulation and returns True."""
        provider = AndroidSmsGatewayOtpProvider()
        result = provider.send_otp(phone="+919876543210", code="654321", language="en")
        self.assertTrue(result)

    @override_settings(
        OTP_PROVIDER="android_gateway",
        SMS_GATEWAY_USER="user",
        SMS_GATEWAY_PASSWORD="pass",
    )
    def test_get_otp_provider_factory_explicit(self):
        provider = get_otp_provider()
        self.assertIsInstance(provider, AndroidSmsGatewayOtpProvider)

    @override_settings(
        OTP_PROVIDER="",
        SMS_GATEWAY_USER="user",
        SMS_GATEWAY_PASSWORD="pass",
    )
    def test_get_otp_provider_factory_credential_fallback(self):
        provider = get_otp_provider()
        self.assertIsInstance(provider, AndroidSmsGatewayOtpProvider)

