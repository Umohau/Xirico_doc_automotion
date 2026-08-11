import pytest
from unittest.mock import Mock, PropertyMock
from Projeto_xirico.seguranca import OtpMixIn
from Projeto_xirico.exc import ExpiredOtpError, InvalidOtpError, AttemptsExcedError

@pytest.fixture
def otp_mix_in():
    return OtpMixIn()


def test_verificar_otp_sucess(otp_mix_in):
    otp= otp_mix_in.gerar_otp()
    assert otp_mix_in.verificar_otp(otp) is True


def test_verificar_otp_expired(otp_mix_in):
    otp= otp_mix_in.gerar_otp()
    type(otp_mix_in).status_=PropertyMock(return_value='expired')
    with pytest.raises(ExpiredOtpError):
        otp_mix_in.verificar_otp(otp)


def test_otp_mix_in_no_genereted_otp(otp_mix_in):
    otp= "90345623"
    type(otp_mix_in).status_=PropertyMock(return_value= None)

    with pytest.raises(AttributeError):
        otp_mix_in.verificar_otp(otp)


def test_otp_mix_in_incorrect_otp(otp_mix_in):
    otp_mix_in.gerar_otp()
    incorrect_otp='12345678'
    with pytest.raises(InvalidOtpError):
        otp_mix_in.verificar_otp(incorrect_otp)


def test_otp_mix_in_attempts_exceded(otp_mix_in):
    otp_mix_in.gerar_otp()
    incorrect_otp= '12345678'
    with pytest.raises(AttemptsExcedError):
        for i in range (3):
            try:
                otp_mix_in.verificar_otp(incorrect_otp)
            except InvalidOtpError:
                continue