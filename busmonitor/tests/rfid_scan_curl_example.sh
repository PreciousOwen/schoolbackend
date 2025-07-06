# Example curl command to POST to /rfid-scan/
# Save this as rfid_scan_curl_example.sh and run: sh rfid_scan_curl_example.sh

curl -X POST http://localhost:8081/rfid-scan/ \
  -H "Content-Type: application/json" \
  -d '{"rfid": "TEST_RFID_123", "bus_id": 1}'

# If authentication is required, add a session cookie or token as needed.
# Example with session cookie:
# curl -X POST http://localhost:8081/rfid-scan/ \
#   -H "Content-Type: application/json" \
#   -H "Cookie: sessionid=YOUR_SESSION_ID" \
#   -d '{"rfid": "TEST_RFID_123", "bus_id": 1}'
