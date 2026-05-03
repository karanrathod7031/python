"""Tests for intent detection."""

import pytest

from app.core.intent import IntentCategory, IntentDetector


@pytest.fixture
def detector():
    return IntentDetector()


class TestIntentDetector:
    def test_open_app(self, detector):
        intent = detector.detect("open chrome")
        assert intent.category == IntentCategory.SYSTEM_CONTROL
        assert intent.action == "open_app"
        assert intent.confidence >= 0.8

    def test_close_app(self, detector):
        intent = detector.detect("close spotify")
        assert intent.category == IntentCategory.SYSTEM_CONTROL
        assert intent.action == "close_app"

    def test_shutdown_requires_confirmation(self, detector):
        intent = detector.detect("shutdown the computer")
        assert intent.category == IntentCategory.SYSTEM_CONTROL
        assert intent.requires_confirmation is True

    def test_restart_requires_confirmation(self, detector):
        intent = detector.detect("restart my system")
        assert intent.category == IntentCategory.SYSTEM_CONTROL
        assert intent.requires_confirmation is True

    def test_volume_control(self, detector):
        intent = detector.detect("volume up")
        assert intent.category == IntentCategory.VOLUME_BRIGHTNESS

    def test_file_create(self, detector):
        intent = detector.detect("create file test.txt")
        assert intent.category == IntentCategory.FILE_OPERATION
        assert intent.action == "create"

    def test_file_delete(self, detector):
        intent = detector.detect("delete file old.txt")
        assert intent.category == IntentCategory.FILE_OPERATION
        assert intent.requires_confirmation is True

    def test_web_search(self, detector):
        intent = detector.detect("google python tutorials")
        assert intent.category == IntentCategory.WEB_AUTOMATION
        assert intent.action == "search"

    def test_open_url(self, detector):
        intent = detector.detect("open https://github.com")
        assert intent.category == IntentCategory.WEB_AUTOMATION

    def test_reminder(self, detector):
        intent = detector.detect("remind me to study DSA at 8")
        assert intent.category == IntentCategory.REMINDER
        assert "reminder_text" in intent.entities

    def test_todo(self, detector):
        intent = detector.detect("add a to do buy groceries")
        assert intent.category == IntentCategory.TODO

    def test_alarm(self, detector):
        intent = detector.detect("set an alarm for 7 am")
        assert intent.category == IntentCategory.ALARM

    def test_email(self, detector):
        intent = detector.detect("send an email to john")
        assert intent.category == IntentCategory.EMAIL

    def test_monitoring(self, detector):
        intent = detector.detect("cpu usage")
        assert intent.category == IntentCategory.MONITORING

    def test_question(self, detector):
        intent = detector.detect("what is machine learning?")
        assert intent.category == IntentCategory.QUESTION

    def test_scheduling(self, detector):
        intent = detector.detect("every day at 7 open YouTube")
        assert intent.category == IntentCategory.AUTOMATION

    def test_translation(self, detector):
        intent = detector.detect("translate hello to Hindi")
        assert intent.category == IntentCategory.TRANSLATION

    def test_unknown_defaults_to_conversation(self, detector):
        intent = detector.detect("xyzabc random text")
        assert intent.category == IntentCategory.CONVERSATION
        assert intent.confidence < 0.8

    def test_lock_screen(self, detector):
        intent = detector.detect("lock the screen")
        assert intent.category == IntentCategory.SYSTEM_CONTROL
        assert intent.action == "lock_screen"
