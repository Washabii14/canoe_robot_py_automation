*** Settings ***
Documentation    Positive diagnostics suite (mock backend).
Resource         ../../../resources/keywords/diag_keywords.robot
Resource         ../../../resources/keywords/assertion_keywords.robot

*** Test Cases ***
Raw Request Returns Positive Response
    ${result}=    Send Raw UDS Request    22 F1 90
    Assert Diag Positive Response    ${result}    22 F1 90    0x22

Symbolic Request Returns Positive Response
    ${result}=    Send Symbolic UDS Request    Read_VIN    {}
    Assert Diag Positive Response    ${result}    Read_VIN    Read_VIN
