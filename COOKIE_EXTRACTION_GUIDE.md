# 🍪 XHS-Scraper Cookie Extraction Guide

## ⚠️ What Error Occurs Without Real Cookies?

### The Error You'll See:
```
UnicodeEncodeError: 'ascii' codec can't encode characters in position 3-9: ordinal not in range(128)
  File "site-packages/httpx/_models.py", line 236, in __setitem__
    set_value = value.encode(self._encoding or "utf-8")
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

**What This Means**: The script tried to use the placeholder cookie value, but httpx couldn't encode Chinese characters as ASCII.

### Fixed! ✅
We've now replaced all Chinese placeholders with ASCII values. But to actually use the scripts, you need **real cookies**.

---

## 🛠️ How to Extract Real Cookies

### Method 1: Browser DevTools (Easiest) ✅ RECOMMENDED

#### Chrome/Edge Steps:
1. **Open Xiaohongshu** (https://www.xiaohongshu.com)
2. **Log in** with your account
3. **Open DevTools**:
   - Press `F12` or `Ctrl+Shift+I` (Windows)
   - Press `Cmd+Option+I` (Mac)
4. **Go to Storage/Application tab**:
   - Click "Application" tab (top right)
   - Click "Cookies" in left sidebar
   - Click "https://www.xiaohongshu.com"
5. **Find the cookies you need**:
   - Look for `a1` cookie
   - Look for `web_session` cookie
6. **Copy the values**:
   - Click each cookie to view its value
   - Copy the entire value string

#### Visual Guide:
```
Chrome DevTools:
┌─────────────────────────────────────────┐
│ ☑ Application  Console  Sources  ...   │
├─────────────────────────────────────────┤
│ Storage                                 │
│ ├─ Local Storage                        │
│ ├─ Session Storage                      │
│ ├─ Cookies                              │ ← Click here
│ │  └─ https://www.xiaohongshu.com       │ ← Select domain
│ │     a1         [value here]           │ ← Copy this
│ │     web_session [value here]          │ ← Copy this
│ └─ ...
```

---

### Method 2: Browser Extension

Popular options:
- **EditThisCookie** (Chrome/Firefox)
- **Cookie-Editor** (Chrome/Firefox)
- **Advanced REST Client** (Chrome)

Steps:
1. Install the extension
2. Navigate to xiaohongshu.com and log in
3. Click the extension icon
4. Find and copy `a1` and `web_session` values

---

### Method 3: Python Script (Automatic)

XHS-Scraper includes a helper script:

```bash
python chrome_cookies.py
```

This script:
- Reads cookies directly from Chrome/Edge storage
- No manual copying needed
- Works on Windows, Mac, Linux

**Note**: Requires Chrome/Edge to be installed and your profile to be logged into XHS.

---

## 🔑 What Cookies Do You Need?

### Required Cookies:

| Cookie | Description | Example |
|--------|-------------|---------|
| `a1` | Device fingerprint | `1a2b3c4d5e6f7g8h9i0j` |
| `web_session` | Session token | `abc123def456ghi789jkl` |

### Optional Cookies:

| ID | Used By | Description |
|----|---------|-------------|
| `NOTE_ID` | search_batch.py, get_note.py, get_comments.py, download_media.py | A specific note's ID |
| `USER_ID` | get_user_info.py, get_user_notes.py | A specific user's ID |

---

## 📝 How to Use Extracted Cookies

### Step 1: Get Your Cookies
Follow one of the methods above to extract:
- `a1` value
- `web_session` value

### Step 2: Update Each Script

**Example: For main.py**

```python
# main.py
async def main():
    cookies = {
        "a1": "YOUR_ACTUAL_A1_VALUE_HERE",              # ← Paste real a1
        "web_session": "YOUR_ACTUAL_WEB_SESSION_HERE",  # ← Paste real web_session
    }
    
    # Rest of the script...
```

Replace:
- `YOUR_ACTUAL_A1_VALUE_HERE` → Your real `a1` cookie value
- `YOUR_ACTUAL_WEB_SESSION_HERE` → Your real `web_session` value

### Step 3: Update All Scripts

| Script | Cookie Fields | ID Fields |
|--------|---------------|-----------|
| main.py | ✅ a1, web_session | - |
| search_batch.py | ✅ a1, web_session | - |
| get_note.py | ✅ a1, web_session | ✅ NOTE_ID |
| get_user_notes.py | ✅ a1, web_session | ✅ USER_ID |
| get_user_info.py | ✅ a1, web_session | ✅ USER_ID |
| get_comments.py | ✅ a1, web_session | ✅ NOTE_ID |
| download_media.py | ✅ a1, web_session | ✅ NOTE_ID, XSEC_TOKEN |
| qr_login.py | ✅ a1, web_session | - |

---

## 🧪 How to Test Your Cookies

### Test 1: Run main.py

This is the simplest test - just checks if your cookies are valid.

```bash
cd E:\Hello World\Project\test\xhs-scraper
python main.py
```

**Expected output if cookies are valid:**
```
登录成功！
昵称: Your_Nickname_Here
```

**Error if cookies are invalid:**
```
401 Unauthorized
Please check if a1 and web_session cookies are correct
```

### Test 2: Get User Info

Test fetching user profile information:

```bash
python get_user_info.py
```

**Before running**: Update `USER_ID` in the script with an actual XHS user ID.

---

## 🚨 Common Issues & Solutions

### Issue 1: Invalid Cookie Values
**Error**: `401 Unauthorized`
**Cause**: Cookies are expired or incorrect
**Solution**: 
1. Log out of xiaohongshu.com in your browser
2. Log in again to get fresh cookies
3. Extract and update cookies in scripts
4. Try again

### Issue 2: Wrong Cookie Format
**Error**: `ValueError: Invalid cookie value`
**Cause**: Cookie value contains special characters that weren't properly copied
**Solution**:
1. Re-copy the cookie value carefully
2. Make sure you copy the ENTIRE value, not partial
3. Check for extra spaces at start/end
4. Try again

### Issue 3: "IP Risk" Error
**Error**: `IP存在风险` or `IP Risk Detected`
**Cause**: Xiaohongshu detected suspicious login from your IP
**Solution**:
1. Switch to a different network (mobile data, VPN, etc.)
2. Log in to xiaohongshu.com manually first
3. Verify any security prompts from XHS
4. Extract fresh cookies
5. Try again

### Issue 4: Session Expired
**Error**: `Session expired` or `403 Forbidden`
**Cause**: Cookies are valid but session expired during use
**Solution**:
1. Extract fresh cookies
2. Replace in scripts
3. Run again immediately

---

## 💡 Pro Tips

### Tip 1: Cookie Lifespan
- Cookies typically last 7-30 days
- If scripts stop working, re-extract cookies
- Update scripts with fresh values

### Tip 2: Multiple Accounts
- Extract cookies for each account separately
- Save in different script files or variables
- Rotate between accounts as needed

### Tip 3: Automate Cookie Extraction
- Use `chrome_cookies.py` for automatic extraction
- Reduces manual work
- More reliable than manual copying

### Tip 4: Keep Cookies Private
- Don't share your cookie values
- Don't commit to public GitHub
- Treat cookies like passwords

---

## 🔐 Security Notes

### Important ⚠️
- **Cookies = Password equivalent**
  - Anyone with your cookies can access your XHS account
  - Don't share them with anyone
  - Don't post them publicly
  
- **Keep Them Safe**
  - Use `.env` files for local development
  - Add `.env` to `.gitignore`
  - Never commit cookies to version control

### Safe Storage Pattern:
```python
# .env file (NOT in git)
A1_COOKIE="your_cookie_here"
WEB_SESSION_COOKIE="your_cookie_here"

# Python script
import os
from dotenv import load_dotenv

load_dotenv()
cookies = {
    "a1": os.getenv("A1_COOKIE"),
    "web_session": os.getenv("WEB_SESSION_COOKIE"),
}
```

---

## ✅ Verification Checklist

Before running any script:

- [ ] Extracted `a1` cookie from browser
- [ ] Extracted `web_session` cookie from browser
- [ ] Updated cookie values in script
- [ ] Verified no placeholder text remains (not "PASTE_YOUR_*")
- [ ] For ID-based scripts: Updated `NOTE_ID` or `USER_ID`
- [ ] Ran `python main.py` to test credentials
- [ ] Got "登录成功！" message

---

## 📞 Still Having Issues?

1. **Check the error message carefully** - It usually tells you what's wrong
2. **Re-extract cookies** - They may have expired
3. **Try a fresh browser session** - Log out, log back in
4. **Check your internet connection** - VPN/proxy issues?
5. **Try from a different network** - Some ISPs block XHS
6. **Check if XHS has rate limits** - Try again in 1 hour
7. **Report the issue** - Include full error message

---

## 📋 Quick Reference: Cookie Values Needed

### Minimal Setup (main.py test):
```python
cookies = {
    "a1": "YOUR_A1_HERE",
    "web_session": "YOUR_WEB_SESSION_HERE"
}
```

### Full Setup (all scripts):
```python
# Cookies (required for all scripts)
cookies = {
    "a1": "YOUR_A1_HERE",
    "web_session": "YOUR_WEB_SESSION_HERE"
}

# IDs (required for specific scripts)
NOTE_ID = "PASTE_YOUR_NOTE_ID_HERE"      # For note-related scripts
USER_ID = "PASTE_YOUR_USER_ID_HERE"      # For user-related scripts
XSEC_TOKEN = "PASTE_YOUR_XSEC_HERE"      # For download_media.py (optional)
```

---

## 🔗 Related Files

- **FIXES_SUMMARY.md** - Technical details of Unicode fix
- **STATUS.txt** - Project overview
- **COMPLETION_CHECKLIST.md** - Full verification checklist
- **chrome_cookies.py** - Automatic cookie extraction script

---

## 🎯 Next Steps After Getting Cookies

1. **Update scripts** with real cookie values
2. **Run `python main.py`** to verify credentials work
3. **Run `python search_batch.py`** to test search functionality
4. **Update other scripts** with NOTE_ID or USER_ID as needed
5. **Check test suite** in `tests/` directory for automated testing

---

**Last Updated**: 2025-02-06  
**Status**: ✅ Complete and ready to use
