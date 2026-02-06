# Decisions - xhs-scraper Scripts Batch

## 2026-02-06

### Script Design Decisions

1. **Configuration at Top**: All user-configurable values placed in clearly marked section
2. **Bilingual Comments**: Chinese + English for international accessibility
3. **Consistent Pattern**: All scripts use same async/await structure
4. **Simple by Default**: get_comments.py doesn't fetch sub-comments to keep it simple
5. **Auto-export**: Scripts with pagination (search, user_notes, comments) auto-export to JSON/CSV
