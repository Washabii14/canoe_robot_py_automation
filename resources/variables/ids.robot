*** Variables ***
# Placeholder IDs for diagnostics/flashing addressing.
# Replace these values with project-specific real bench setup values.

# Transport selection hint used by test planning/documentation.
${ID_PROFILE}                  PLACEHOLDER

# CAN/CAN-FD addressing (examples shown as hex string placeholders).
${CAN_TESTER_PHYSICAL_ID}      0x7E0
${CAN_ECU_PHYSICAL_ID}         0x7E8
${CAN_TESTER_FUNCTIONAL_ID}    0x7DF

# DoIP/Ethernet addressing (placeholders only).
${DOIP_TESTER_SOURCE_ADDR}     0x0E80
${DOIP_ECU_TARGET_ADDR}        0x0001

# Logical naming placeholders used by test docs/keywords.
${ECU_LOGICAL_NAME}            ECU_PLACEHOLDER
${PROGRAMMING_VARIANT}         VARIANT_PLACEHOLDER
