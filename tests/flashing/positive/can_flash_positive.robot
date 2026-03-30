*** Settings ***
Documentation    Positive flashing suite (mock backend).
Resource         ../../../resources/keywords/flash_keywords.robot
Resource         ../../../resources/keywords/assertion_keywords.robot

*** Test Cases ***
Default Flash Plan Completes Successfully
    ${result}=    Start CAN Flashing
    Assert Flash Success    ${result}    Default Flash Plan Completes Successfully    complete

Verify Positive Flashing Result
    Start CAN Flashing
    ${result}=    Verify Flashing Result    ${True}
    Assert Flash Success    ${result}    Verify Positive Flashing Result    complete
