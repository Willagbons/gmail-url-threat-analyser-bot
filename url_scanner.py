import requests
import time

class SimpleURLScanner:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://urlscan.io/api/v1/"
        self.headers = {"API-Key": api_key} if api_key else {}

    def scan_url(self, url: str) -> dict:
        # Submit URL for scanning
        resp = requests.post(
            self.base_url + "scan/",
            json={"url": url, "public": "on"},
            headers=self.headers
        )
        if resp.status_code != 200:
            print(f"Error submitting URL: {resp.text}")
            return {"error": resp.text}
        
        scan_id = resp.json().get("uuid")
        print(f"Submitted {url} for scanning. Scan ID: {scan_id}")
        
        # Rate limiting: wait between submissions
        time.sleep(2)
        
        # Poll for result with longer timeout
        max_attempts = 30  # 30 attempts × 3 seconds = 1.5 minutes
        for attempt in range(max_attempts):
            time.sleep(3)
            try:
                result = requests.get(self.base_url + f"result/{scan_id}/").json()
                state = result.get("task", {}).get("state")
                
                if state == "done":
                    print(f"Scan completed for {url}")
                    return result
                elif state == "pending":
                    print(f"Scan still pending for {url} (attempt {attempt + 1}/{max_attempts})")
                elif state == "error":
                    print(f"Scan failed for {url}: {result.get('task', {}).get('error', 'Unknown error')}")
                    return {"error": "scan_failed"}
                else:
                    print(f"Scan state for {url}: {state} (attempt {attempt + 1}/{max_attempts})")
                    
            except Exception as e:
                print(f"Error checking scan status for {url}: {e}")
                
        print(f"Timeout waiting for scan result for {url} after {max_attempts * 3} seconds")
        return {"error": "timeout"} 