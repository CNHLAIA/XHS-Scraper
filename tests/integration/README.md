# Integration Tests

This directory contains integration tests for the XHS Scraper that interact with the actual Xiaohongshu API.

## Prerequisites

### Setting Up XHS_COOKIES

Integration tests require valid Xiaohongshu (RedBook) cookies to authenticate with the API.

#### Method 1: Environment Variable (Recommended)

Export the cookies as an environment variable:

**Windows (PowerShell):**
```powershell
$env:XHS_COOKIES = "your_cookies_here"
```

**Windows (CMD):**
```cmd
set XHS_COOKIES=your_cookies_here
```

**Linux/macOS:**
```bash
export XHS_COOKIES="your_cookies_here"
```

#### Method 2: .env File

Create a `.env` file in the project root:
```
XHS_COOKIES=your_cookies_here
```

> **IMPORTANT:** Never commit `.env` files or real cookies to version control.

## Running Integration Tests

```bash
# Run all integration tests
pytest tests/integration/

# Run specific test file
pytest tests/integration/test_note.py

# Run with verbose output
pytest tests/integration/ -v

# Run specific test
pytest tests/integration/test_note.py::test_fetch_note_details -v
```

## Test Data - Example IDs

Use these example IDs for testing (replace with real IDs from your environment):

### Note IDs
- Example format: `7123456789012345678`
- Source: Copy from URL when viewing a note on Xiaohongshu

### User IDs
- Example format: `123456789`
- Source: User profile URL on Xiaohongshu

### Search Keywords
- Example: `穿搭` (outfit/clothing)
- Example: `美妆` (makeup)
- Example: `旅游` (travel)

## Rate Limiting Warning ⚠️

The Xiaohongshu API enforces rate limiting. Be aware:

- **Do NOT run integration tests in rapid succession** - wait 1-2 seconds between requests
- **Do NOT make bulk requests** in quick succession
- Excessive requests may result in:
  - Temporary IP blocks
  - Account suspension
  - Authentication failures

**Best Practices:**
- Run tests during development, not in CI/CD pipelines (unless specifically designed)
- Use fixtures with appropriate delays between API calls
- Cache responses when possible
- Mock API responses for most tests, use integration tests sparingly

## Debugging

If tests fail:

1. **Check XHS_COOKIES is set:**
   ```bash
   echo $XHS_COOKIES  # Linux/macOS
   echo %XHS_COOKIES%  # Windows CMD
   ```

2. **Verify cookie validity** - Cookies expire and need refresh

3. **Check rate limiting** - Wait a few minutes and retry

4. **Enable debug logging:**
   ```bash
   pytest tests/integration/ -v --log-cli-level=DEBUG
   ```

## CI/CD Considerations

**Do not include integration tests in automated CI/CD pipelines** without:
- Proper rate limiting controls
- Valid, refreshed authentication tokens
- Environment-specific test data
- Explicit test markers (e.g., `@pytest.mark.integration`)

## References

- [Xiaohongshu Official](https://www.xiaohongshu.com/)
- XHS Scraper Documentation: See project README
