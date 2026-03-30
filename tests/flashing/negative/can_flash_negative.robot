*** Settings ***
Documentation    Negative flashing suite (mock backend).
Resource         ../../../resources/keywords/flash_keywords.robot
Resource         ../../../resources/keywords/assertion_keywords.robot

*** Test Cases ***
InvalidTransferBlockTriggersControlledAbort
    ${blocks}=    Create List    FE ED FA CE
    ${plan}=    Create Dictionary    transfer_blocks=${blocks}
    ${result}=    Start CAN Flashing    ${plan}
    Assert Flash Controlled Abort
    ...    ${result}
    ...    InvalidTransferBlockTriggersControlledAbort
    ...    Transfer failed
