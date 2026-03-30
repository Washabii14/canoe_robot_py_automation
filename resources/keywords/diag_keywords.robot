*** Settings ***
Documentation    Diagnostic keywords backed by Python library.
Resource         ../variables/env.robot
Library          libraries/diagnostics/diag_keyword_library.py
...              ${EXECUTION_BACKEND}
...              ${UDS_TRANSPORT}
...              ${MOCK_FIXTURE_PATH}
...              ${CANOE_CONFIG_PATH}
...              ${AUTO_START_MEASUREMENT}
...              ${CANOE_DIAG_METHOD}
...              ${UDS_TIMEOUT_S}
...              ${UDS_RETRY_COUNT}
...              ${UDS_RETRY_DELAY_S}
...              ${UDS_WAIT_POLL_INTERVAL_S}
...              WITH NAME    DiagLib

*** Keywords ***
Send Raw UDS Request
    [Arguments]    ${bytes_req}
    ${result}=    DiagLib.Send Raw Uds Request    ${bytes_req}
    [Return]    ${result}

Send Symbolic UDS Request
    [Arguments]    ${name}    ${params}={}
    ${result}=    DiagLib.Send Symbolic Uds Request    ${name}    ${params}
    [Return]    ${result}

Wait For Raw UDS Positive Response
    [Arguments]    ${bytes_req}    ${timeout_s}=${EMPTY}    ${poll_interval_s}=${EMPTY}
    ${result}=    DiagLib.Wait For Raw Uds Positive Response    ${bytes_req}    ${timeout_s}    ${poll_interval_s}
    [Return]    ${result}

Wait For Raw UDS NRC Response
    [Arguments]    ${bytes_req}    ${expected_nrc}    ${timeout_s}=${EMPTY}    ${poll_interval_s}=${EMPTY}
    ${result}=    DiagLib.Wait For Raw Uds Nrc Response    ${bytes_req}    ${expected_nrc}    ${timeout_s}    ${poll_interval_s}
    [Return]    ${result}

Wait For Symbolic UDS Positive Response
    [Arguments]    ${name}    ${params}={}    ${timeout_s}=${EMPTY}    ${poll_interval_s}=${EMPTY}
    ${result}=    DiagLib.Wait For Symbolic Uds Positive Response    ${name}    ${params}    ${timeout_s}    ${poll_interval_s}
    [Return]    ${result}

Wait For Symbolic UDS NRC Response
    [Arguments]    ${name}    ${expected_nrc}    ${params}={}    ${timeout_s}=${EMPTY}    ${poll_interval_s}=${EMPTY}
    ${result}=    DiagLib.Wait For Symbolic Uds Nrc Response    ${name}    ${expected_nrc}    ${params}    ${timeout_s}    ${poll_interval_s}
    [Return]    ${result}
