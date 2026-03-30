*** Variables ***
${EXECUTION_BACKEND}    mock
${UDS_TRANSPORT}        can
${MOCK_FIXTURE_PATH}    config/fixtures/uds_mock_responses.json
${CANOE_CONFIG_PATH}    config/canoe_env/placeholder.cfg
${AUTO_START_MEASUREMENT}    ${True}
${CANOE_DIAG_METHOD}    diagnostics:SendRequest
${UDS_TIMEOUT_S}    2.0
${UDS_RETRY_COUNT}    1
${UDS_RETRY_DELAY_S}    0.2
${UDS_WAIT_POLL_INTERVAL_S}    0.2
