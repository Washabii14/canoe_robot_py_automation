*** Settings ***
Documentation    Negative diagnostics suite (mock backend).
Resource         ../../../resources/keywords/diag_keywords.robot
Resource         ../../../resources/keywords/assertion_keywords.robot

*** Test Cases ***
Unknown Raw Request Returns Negative Response
    ${result}=    Send Raw UDS Request    22 FF FF
    Assert Diag Negative NRC    ${result}    22 FF FF    0x31
