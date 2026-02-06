# 🚨 XHS-Scraper Error Reference Guide

## Quick Error Lookup

| Error Code | Error Message | Cause | Solution |
|------------|---------------|-------|----------|
| 401 | Unauthorized | Invalid/expired cookies | Re-extract cookies |
| 403 | Forbidden | Session expired | Get fresh cookies |
| 429 | Too Many Requests | Rate limited | Wait 1-24 hours |
| IP Risk | IP存在风险 | Suspicious IP | Use VPN or wait |
| UnicodeEncodeError | 'ascii' codec error | Chinese in cookie values | Use ASCII placeholders |

---

## 🔴 Error Details & Solutions

### 1. UnicodeEncodeError (FIXED ✅)

**Full Error**:
```
UnicodeEncodeError: 'ascii' codec can't encode characters in position 3-9: ordinal not in range(128)
  File "site-packages/httpx/_models.py", line 236, in __setitem__
    set_value = value.encode(self._encoding or "utf-8")
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**What Happened**: 
- Script used Chinese placeholder text in cookie value
- httpx tried to encode as ASCII but Chinese characters failed
- This is a known issue with httpx cookie handling

**Status**: ✅ FIXED in all scripts
- All Chinese placeholders replaced with ASCII
- All scripts now use `PASTE_YOUR_*_HERE` format

**If You Still See This**:
1. Check you're using latest version of scripts
2. Ensure no Chinese characters in cookie values
3. Verify clipboard didn't auto-translate values

---

### 2. 401 Unauthorized

**Full Error**:
```
httpx.HTTPStatusError: Client error '401 Unauthorized' for url 'https://...'
Response content: {"error_code": "401", "message": "Unauthorized"}
```

**What This Means**:
- Your cookies are invalid or expired
- XHS doesn't recognize your session
- Could be wrong cookie values

**How to Fix**:

**Option A: Quick Fix (5 minutes)**
```
1. Open xiaohongshu.com in browser
2. Verify you're still logged in
3. If logged out, log back in
4. Re-extract cookies (F12 → Application → Cookies)
5. Update script with new values
6. Try again
```

**Option B: Complete Reset (10 minutes)**
```
1. Log out of xiaohongshu.com completely
   - Click profile → Settings → Sign Out
2. Clear all cookies for xiaohongshu.com
   - F12 → Application → Cookies → Delete all for domain
3. Close browser completely
4. Reopen browser (new session)
5. Go to xiaohongshu.com and log in fresh
6. Extract cookies immediately
7. Update scripts
8. Test with python main.py
```

**Option C: Use Backup Cookies (if available)**
```
If you have cookies from another device/account:
1. Try those cookies in the script
2. If they work, use them instead
3. Rotate between multiple accounts if needed
```

---

### 3. 403 Forbidden

**Full Error**:
```
httpx.HTTPStatusError: Client error '403 Forbidden' for url 'https://...'
Response content: {"error_code": "403", "message": "Access Denied"}
```

**What This Means**:
- Your session exists but is no longer valid
- Usually cookies expired during script execution
- Could be 24-hour session timeout

**How to Fix**:
```python
# Quick fix: Run immediately after extracting fresh cookies
import time
from datetime import datetime

# Extract fresh cookies FIRST
print(f"[{datetime.now()}] Extracted cookies")

# Run script immediately
print(f"[{datetime.now()}] Running script...")
# Rest of your code

# Cookies are freshest in first 5 minutes
# After 10+ minutes, they may start expiring
```

**Permanent Fix**:
```
Use chrome_cookies.py to auto-refresh:
    python chrome_cookies.py  # Runs every time before script
    python main.py            # Uses freshest cookies
```

---

### 4. 429 Too Many Requests (Rate Limited)

**Full Error**:
```
httpx.HTTPStatusError: Client error '429 Too Many Requests'
Response content: {"error_code": "429", "message": "Rate limited"}
```

**What This Means**:
- You made too many requests in a short time
- XHS temporarily blocking your account/IP
- Could last 1 hour to 24 hours

**How to Fix**:

**Immediate**:
```
1. Stop running scripts immediately
2. Don't retry for at least 1 hour
3. XHS will unblock you automatically
```

**Prevent It**:
```python
import time
import asyncio

# Add delays between requests
async def scrape_with_delay():
    items = ["item1", "item2", "item3"]
    for item in items:
        # Do work
        await work(item)
        
        # Wait 2-5 seconds between requests
        await asyncio.sleep(3)  # 3 second delay
        
        print(f"Processed {item}, waiting before next...")
```

**For Batch Operations**:
```
# Reduce batch size to avoid hammering server
# BEFORE: Process 100 items in one go
# AFTER: Process 10 items, rest, repeat

batch_size = 10  # Instead of 100
for batch in chunks(items, batch_size):
    process_batch(batch)
    time.sleep(60)  # 1 minute between batches
```

---

### 5. IP Risk / IP存在风险

**Full Error**:
```
Response: {"error_code": "10001", "message": "IP存在风险"}
```

**What This Means**:
- XHS detected unusual activity from your IP
- Could be:
  - New/unfamiliar IP
  - VPN/Proxy detected
  - Multiple login attempts
  - Rapid request patterns

**How to Fix**:

**Option A: Wait It Out (Safest)**
```
1. Stop using scripts for 24 hours
2. Browse xiaohongshu.com normally via browser
3. After 24 hours, risk should clear
4. Resume scripts
```

**Option B: Use VPN/Proxy**
```
1. If your ISP is blocked, use VPN
2. But DON'T use free VPNs (unreliable)
3. Use paid VPN for reliability
4. Log in to XHS with VPN
5. Extract cookies
6. Use scripts with VPN active
```

**Option C: Verify Your Account**
```
1. Log in via browser normally
2. If XHS shows security verification:
   - Complete phone verification if needed
   - Verify identity if asked
3. Once verified, try scripts again
```

**Option D: Use Mobile Data**
```
1. Switch to mobile hotspot if available
2. Different IP source = lower risk
3. Log in fresh to XHS
4. Extract new cookies
5. Try scripts
```

---

### 6. Network Connection Error

**Full Error**:
```
httpx.ConnectError: [Errno 11001] getaddrinfo failed
```

**What This Means**:
- Can't connect to xiaohongshu.com servers
- Could be:
  - Internet connection down
  - DNS resolution failing
  - Firewall blocking
  - XHS servers down

**How to Fix**:

**Check Your Connection**:
```bash
# Test internet
ping 8.8.8.8

# Test DNS
nslookup xiaohongshu.com

# Test accessing XHS
curl https://www.xiaohongshu.com
```

**Fix Common Issues**:
```
If ping fails:
- Check WiFi/ethernet connection
- Restart router
- Check your ISP isn't down

If nslookup fails:
- Change DNS to 8.8.8.8
- Change DNS to 1.1.1.1
- Restart network adapter

If curl fails but ping works:
- XHS servers might be down
- Try again in 1 hour
- Check XHS Twitter for status
```

---

### 7. JSON Decode Error

**Full Error**:
```
json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

**What This Means**:
- Response from server wasn't valid JSON
- Could be:
  - HTML error page instead of JSON
  - Redirect page
  - Server error
  - Malformed response

**How to Fix**:
```python
# Debug: Print actual response
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get("https://...")
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Response: {response.text[:500]}")  # First 500 chars
    
    # Only try JSON if it looks like JSON
    if 'application/json' in response.headers.get('content-type', ''):
        data = response.json()
    else:
        print("Not JSON response!")
```

---

### 8. Cookie Value Issues

**Error**: Various (depends on issue)

**Common Issues**:

**Issue A: Extra Spaces in Cookie**
```
# Wrong - has leading space
a1 = " 1a2b3c4d5e6f7g8h"

# Correct - no extra spaces
a1 = "1a2b3c4d5e6f7g8h"

# Fix: Use .strip()
cookies = {
    "a1": value.strip(),
    "web_session": value.strip()
}
```

**Issue B: Incomplete Cookie Value**
```
# Wrong - partial value
a1 = "1a2b3c4d"

# Correct - full value
a1 = "1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7"

# Fix: Copy entire value from DevTools, not just part
```

**Issue C: Wrong Cookie Name**
```
# Wrong cookie names:
- "A1" (capital) instead of "a1"
- "session" instead of "web_session"
- "xhs_a1" instead of "a1"

# Always verify exact names in browser
```

---

### 9. Module Not Found

**Full Error**:
```
ModuleNotFoundError: No module named 'httpx'
or
No module named 'xhs_scraper'
```

**What This Means**:
- Required package not installed
- Python can't find the module

**How to Fix**:

```bash
# Install required packages
pip install -r requirements.txt

# Or install individually
pip install httpx
pip install pytest
pip install python-dotenv

# Verify installation
python -c "import httpx; print(httpx.__version__)"
```

---

### 10. Session Expired During Execution

**Error**: Sudden 401/403 mid-execution

**What This Means**:
- Cookie was valid at start
- Expired while script running
- XHS has session timeout (usually 24 hours)

**How to Fix**:
```python
import asyncio
from datetime import datetime, timedelta

async def scrape_with_timeout():
    start_time = datetime.now()
    max_duration = timedelta(hours=12)  # Refresh every 12 hours
    
    while True:
        # Check if cookies need refresh
        if datetime.now() - start_time > max_duration:
            print("Refreshing cookies...")
            # Re-extract or reload cookies
            break
        
        # Do work
        await do_work()
```

---

## 🛠️ Debugging Checklist

When you encounter an error, go through this checklist:

1. **Read the error message carefully**
   - First line usually tells you the main problem
   - Look for "401", "403", "429", etc.

2. **Check your cookies**
   ```bash
   # Verify cookies in script
   python -c "from main import cookies; print(cookies)"
   ```

3. **Test connectivity**
   ```bash
   # Can you reach XHS?
   curl -I https://www.xiaohongshu.com
   ```

4. **Check if XHS is down**
   - Visit https://www.xiaohongshu.com in browser
   - Can you browse normally?
   - If not, wait for XHS to come back online

5. **Try with fresh cookies**
   ```bash
   # Extract new cookies
   python chrome_cookies.py
   # OR manually extract via browser
   # Then update script and try again
   ```

6. **Check logs for details**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Run script to see detailed logs
   ```

7. **Try minimal reproduction**
   ```python
   # Instead of full script, test just the error line
   import httpx
   
   cookies = {"a1": "YOUR_VALUE", "web_session": "YOUR_VALUE"}
   async with httpx.AsyncClient(cookies=cookies) as client:
       response = await client.get("https://www.xiaohongshu.com/api/...")
       print(response.status_code)
   ```

---

## 📞 Getting Help

If none of the above solutions work:

1. **Record the exact error message** (copy-paste full traceback)
2. **Note what you were doing** (which script, what input)
3. **Share relevant details**:
   - Python version: `python --version`
   - OS: Windows/Mac/Linux
   - Last time cookies worked: (when?)
   - Error message: (full traceback)

4. **DON'T share**:
   - Cookie values
   - Your account information
   - Device IDs
   - Any sensitive data

---

## 📋 Most Common Solutions

**80% of errors are solved by:**
1. Getting fresh cookies (most common)
2. Waiting 1 hour if rate limited
3. Checking internet connection
4. Making sure values have no extra spaces

**Try these first before debugging deeper!**

---

**Last Updated**: 2025-02-06  
**Version**: 1.0  
**Status**: ✅ Complete
