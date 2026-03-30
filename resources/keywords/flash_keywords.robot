*** Settings ***
Documentation    Flashing keywords backed by Python library.
Resource         ../variables/env.robot
Library          libraries/software_update/flash_keyword_library.py
...              ${EXECUTION_BACKEND}
...              ${UDS_TRANSPORT}
...              ${MOCK_FIXTURE_PATH}
...              ${CANOE_CONFIG_PATH}
...              ${AUTO_START_MEASUREMENT}
...              ${CANOE_DIAG_METHOD}
...              ${UDS_TIMEOUT_S}
...              ${UDS_RETRY_COUNT}
...              ${UDS_RETRY_DELAY_S}
...              WITH NAME    FlashLib

*** Keywords ***
Start CAN Flashing
    [Arguments]    ${image_meta}={}
    ${result}=    FlashLib.Start Can Flashing    ${image_meta}
    [Return]    ${result}

Verify Flashing Result
    [Arguments]    ${expected}=True
    ${result}=    FlashLib.Verify Flashing Result    ${expected}
    [Return]    ${result}
