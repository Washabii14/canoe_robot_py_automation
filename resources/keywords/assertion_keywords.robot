*** Settings ***
Documentation    Reusable assertions with explicit diagnostics context.
Library          Collections

*** Keywords ***
Assert Diag Positive Response
    [Arguments]    ${result}    ${request}    ${expected_service}    ${expected_payload}=${EMPTY}
    ${positive}=    Get From Dictionary    ${result}    positive
    ${service}=    Get From Dictionary    ${result}    service
    ${nrc}=    Get From Dictionary    ${result}    nrc
    ${payload}=    Get From Dictionary    ${result}    payload
    ${transport}=    Get From Dictionary    ${result}    transport
    Should Be True    ${positive}
    ...    msg=Expected positive response for request "${request}", but got positive=${positive}, service=${service}, nrc=${nrc}, payload=${payload}, transport=${transport}
    Should Be Equal As Strings    ${service}    ${expected_service}
    ...    msg=Service mismatch for request "${request}": expected service=${expected_service}, got service=${service}, payload=${payload}, nrc=${nrc}, transport=${transport}
    Run Keyword If    '${expected_payload}' != '${EMPTY}'
    ...    Should Be Equal As Strings    ${payload}    ${expected_payload}
    ...    msg=Payload mismatch for request "${request}": expected payload=${expected_payload}, got payload=${payload}, service=${service}, nrc=${nrc}, transport=${transport}

Assert Diag Negative NRC
    [Arguments]    ${result}    ${request}    ${expected_nrc}    ${expected_service}=${EMPTY}
    ${positive}=    Get From Dictionary    ${result}    positive
    ${service}=    Get From Dictionary    ${result}    service
    ${nrc}=    Get From Dictionary    ${result}    nrc
    ${payload}=    Get From Dictionary    ${result}    payload
    ${transport}=    Get From Dictionary    ${result}    transport
    Should Be Equal    ${positive}    ${False}
    ...    msg=Expected negative response for request "${request}" with NRC=${expected_nrc}, but got positive=${positive}, service=${service}, nrc=${nrc}, payload=${payload}, transport=${transport}
    Should Be Equal As Strings    ${nrc}    ${expected_nrc}
    ...    msg=Expected NRC ${expected_nrc} for request "${request}", but got nrc=${nrc}, service=${service}, payload=${payload}, transport=${transport}
    Run Keyword If    '${expected_service}' != '${EMPTY}'
    ...    Should Be Equal As Strings    ${service}    ${expected_service}
    ...    msg=Service mismatch in negative response for request "${request}": expected service=${expected_service}, got service=${service}, nrc=${nrc}, payload=${payload}, transport=${transport}

Assert Flash Success
    [Arguments]    ${result}    ${test_context}    ${expected_step}=complete
    ${success}=    Get From Dictionary    ${result}    success
    ${step}=    Get From Dictionary    ${result}    step
    ${reason}=    Get From Dictionary    ${result}    reason
    ${aborted}=    Get From Dictionary    ${result}    aborted
    ${history}=    Get From Dictionary    ${result}    history
    Should Be True    ${success}
    ...    msg=Expected flashing success in "${test_context}", but got success=${success}, step=${step}, reason=${reason}, aborted=${aborted}, history=${history}
    Should Be Equal As Strings    ${step}    ${expected_step}
    ...    msg=Expected final step=${expected_step} in "${test_context}", but got step=${step}, success=${success}, reason=${reason}, aborted=${aborted}, history=${history}

Assert Flash Controlled Abort
    [Arguments]    ${result}    ${test_context}    ${expected_reason_contains}=${EMPTY}
    ${success}=    Get From Dictionary    ${result}    success
    ${step}=    Get From Dictionary    ${result}    step
    ${reason}=    Get From Dictionary    ${result}    reason
    ${aborted}=    Get From Dictionary    ${result}    aborted
    ${history}=    Get From Dictionary    ${result}    history
    Should Be Equal    ${success}    ${False}
    ...    msg=Expected flashing failure in "${test_context}", but got success=${success}, step=${step}, reason=${reason}, aborted=${aborted}, history=${history}
    Should Be Equal    ${aborted}    ${True}
    ...    msg=Expected controlled abort=True in "${test_context}", but got aborted=${aborted}, success=${success}, step=${step}, reason=${reason}, history=${history}
    Run Keyword If    '${expected_reason_contains}' != '${EMPTY}'
    ...    Should Contain    ${reason}    ${expected_reason_contains}
    ...    msg=Expected failure reason to contain "${expected_reason_contains}" in "${test_context}", but got reason=${reason}, success=${success}, step=${step}, aborted=${aborted}, history=${history}
