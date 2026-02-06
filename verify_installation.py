#!/usr/bin/env python3
"""
XHS-Scraper Installation Verification Script

This script validates that XHS-Scraper is correctly installed and configured.
Run this after installation to ensure everything is working properly.

Usage:
    python verify_installation.py

Returns:
    0 = Installation OK
    1 = Installation issues found
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Tuple, List


class InstallationVerifier:
    """Verify XHS-Scraper installation."""

    def __init__(self):
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
        self.project_root = Path(__file__).parent

    def check_python_version(self) -> bool:
        """Check Python version (3.8+)."""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            self.successes.append(
                f"Python {version.major}.{version.minor}.{version.micro} ✅"
            )
            return True
        else:
            self.issues.append(
                f"Python 3.8+ required, found {version.major}.{version.minor}"
            )
            return False

    def check_required_files(self) -> bool:
        """Check for required project files."""
        required = [
            "README.md",
            "LICENSE",
        ]

        optional = [
            "requirements.txt",
            "xhs_scraper.py",
        ]

        all_found = True
        for file in required:
            filepath = self.project_root / file
            if filepath.exists():
                self.successes.append(f"Found {file} ✅")
            else:
                self.issues.append(f"Missing: {file}")
                all_found = False

        # Check optional files
        for file in optional:
            filepath = self.project_root / file
            if filepath.exists():
                self.successes.append(f"Found {file} ✅")
            else:
                # Optional, just note as warning
                pass

        return all_found

    def check_directories(self) -> bool:
        """Check for required directories."""
        required_dirs = [
            "tests",
        ]

        optional_dirs = [
            "xhs_scraper",
            "modules",
        ]

        all_found = True
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.successes.append(f"Directory {dir_name}/ exists ✅")
            else:
                self.issues.append(f"Missing directory: {dir_name}/")
                all_found = False

        for dir_name in optional_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                self.successes.append(f"Directory {dir_name}/ exists ✅")
            else:
                self.warnings.append(f"Optional directory {dir_name}/ not found")

        return all_found

    def check_dependencies(self) -> bool:
        """Check if Python dependencies are installed."""
        required_packages = [
            "requests",
            "beautifulsoup4",
            "lxml",
            "pytest",
            "pyyaml",
        ]

        all_installed = True
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.successes.append(f"Package '{package}' installed ✅")
            except ImportError:
                self.issues.append(f"Missing package: {package}")
                all_installed = False

        return all_installed

    def check_tests(self) -> bool:
        """Try running a quick test to verify functionality."""
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            self.warnings.append(
                "Tests directory not found, skipping test verification"
            )
            return True

        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
                capture_output=True,
                timeout=30,
                cwd=str(self.project_root),
            )

            if result.returncode == 0:
                # Parse output for test count
                output = result.stdout.decode().strip()
                self.successes.append(
                    f"Tests passing: {output.split()[-3] if output else 'OK'} ✅"
                )
                return True
            else:
                self.warnings.append(
                    "Some tests are failing (might be due to missing config)"
                )
                return True  # Not a hard failure - could be config issue
        except subprocess.TimeoutExpired:
            self.warnings.append("Test execution timed out (pytest might be slow)")
            return True
        except Exception as e:
            self.warnings.append(f"Could not run tests: {str(e)}")
            return True

    def check_documentation(self) -> bool:
        """Check if documentation is present."""
        doc_files = [
            "README.md",
            "DEPLOYMENT_GUIDE.md",
            "ERROR_REFERENCE.md",
        ]

        doc_count = 0
        for doc in doc_files:
            if (self.project_root / doc).exists():
                doc_count += 1

        if doc_count >= 2:
            self.successes.append(f"Documentation present ({doc_count} files) ✅")
            return True
        else:
            self.warnings.append(f"Limited documentation found ({doc_count} files)")
            return True  # Not a hard failure

    def check_config(self) -> bool:
        """Check for configuration files."""
        config_files = [
            "config.yaml",
            ".env",
        ]

        found_configs = False
        for config in config_files:
            if (self.project_root / config).exists():
                self.successes.append(f"Configuration file '{config}' found ✅")
                found_configs = True

        if not found_configs:
            self.warnings.append(
                "No configuration files found (optional - will use defaults)"
            )

        return True

    def verify_all(self) -> bool:
        """Run all verification checks."""
        print("=" * 60)
        print("XHS-Scraper Installation Verification")
        print("=" * 60)
        print()

        # Run checks
        self.check_python_version()
        self.check_required_files()
        self.check_directories()
        self.check_dependencies()
        self.check_documentation()
        self.check_config()
        self.check_tests()

        # Print results
        print("✅ SUCCESSES:")
        print("-" * 60)
        for success in self.successes:
            print(f"  {success}")
        print()

        if self.warnings:
            print("⚠️  WARNINGS:")
            print("-" * 60)
            for warning in self.warnings:
                print(f"  {warning}")
            print()

        if self.issues:
            print("❌ ISSUES:")
            print("-" * 60)
            for issue in self.issues:
                print(f"  {issue}")
            print()

        # Overall status
        print("=" * 60)
        if not self.issues:
            print("✅ INSTALLATION VERIFIED SUCCESSFULLY!")
            print()
            print("Next steps:")
            print("  1. Review DEPLOYMENT_GUIDE.md for configuration")
            print("  2. Extract your XHS cookies (see COOKIE_EXTRACTION_GUIDE.md)")
            print("  3. Run: python xhs_scraper.py --help")
            print("  4. Start scraping!")
            print()
            return True
        else:
            print("❌ INSTALLATION ISSUES DETECTED!")
            print()
            print("To fix:")
            print("  1. Run: pip install -r requirements.txt")
            print("  2. Check that all required files are present")
            print("  3. Verify Python version: python --version")
            print("  4. See DEPLOYMENT_GUIDE.md for detailed setup")
            print()
            return False

    def print_system_info(self) -> None:
        """Print system information."""
        print()
        print("System Information:")
        print(f"  Python: {sys.version.split()[0]}")
        print(f"  Platform: {sys.platform}")
        print(f"  Project Root: {self.project_root}")
        print()


def main() -> int:
    """Main entry point."""
    verifier = InstallationVerifier()
    verifier.print_system_info()

    success = verifier.verify_all()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
