# Test Authoring Guide

This guide explains how to write testcases with clear PASS/FAIL behavior.

## Diagnostics Pattern

```robot
*** Settings ***
Resource    ../../resources/keywords/diag_keywords.robot
Resource    ../../resources/keywords/assertion_keywords.robot

*** Test Cases ***
Read DID Positive
    ${result}=    Send Raw UDS Request    22 F1 95
    Assert Diag Positive Response
    ...    ${result}
    ...    22 F1 95
    ...    0x22
```

Negative NRC case:

```robot
*** Test Cases ***
Read DID Invalid Length
    ${result}=    Wait For Raw UDS NRC Response    22 F1 95 FF    0x13    2.0    0.1
    Assert Diag Negative NRC    ${result}    22 F1 95 FF    0x13
```

## Flashing Pattern

```robot
*** Settings ***
Library     Collections
Resource    ../../resources/keywords/flash_keywords.robot
Resource    ../../resources/keywords/assertion_keywords.robot

*** Test Cases ***
Flash Positive
    ${blocks}=    Create List    AA BB    CC DD
    ${plan}=    Create Dictionary
    ...    security_key=11 22 33 44
    ...    request_download=34 00 44 00 00 00 20
    ...    transfer_blocks=${blocks}
    ...    transfer_exit=37
    ${result}=    Start CAN Flashing    ${plan}
    Assert Flash Success    ${result}    Flash Positive
```

Controlled-abort negative case:

```robot
*** Test Cases ***
Flash Negative Abort
    ${blocks}=    Create List    FE ED FA CE
    ${plan}=    Create Dictionary    transfer_blocks=${blocks}
    ${result}=    Start CAN Flashing    ${plan}
    Assert Flash Controlled Abort    ${result}    Flash Negative Abort    Transfer failed
```

## Logging

Use assertion keywords for explicit failure messages:
- request
- expected vs actual NRC/response
- payload/service/transport
- flashing step/reason/history
