import os


SENTRY_DSN = os.environ.get('SENTRY_DSN', '')


def init_sentry():
    if not SENTRY_DSN:
        return None
    
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        from sentry_sdk.integrations.requests import RequestsIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                FlaskIntegration(),
                RequestsIntegration(),
            ],
            traces_sample_rate=0.1,
            environment=os.getenv('FLASK_ENV', 'development'),
            release=os.getenv('VERSION', '0.1.0'),
        )
        return sentry_sdk
    except ImportError:
        return None
    except Exception:
        return None


def capture_exception(exc_info=None, **kwargs):
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(exc_info)
    except Exception:
        pass


def capture_message(message, level='info', **kwargs):
    try:
        import sentry_sdk
        sentry_sdk.capture_message(message, level=level)
    except Exception:
        pass
