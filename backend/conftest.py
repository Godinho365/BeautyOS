"""Configuração de testes (pytest).

Desabilita o rate limiting durante os testes: a suíte faz muitos logins/requests
e o throttling (ex.: AnonRateThrottle no endpoint de token) causaria 429. O
throttling continua ativo em dev/produção.
"""
import pytest


@pytest.fixture(autouse=True)
def _disable_throttling(settings):
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {"user": None, "anon": None},
    }
