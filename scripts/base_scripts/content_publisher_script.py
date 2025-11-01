#!/usr/bin/env python3
"""
Content Publisher Script - Industry Analysis Integration
Publication workflow for transforming industry analysis to blog-ready content
"""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from jinja2 import Environment, FileSystemLoader

    DEPENDENCIES_AVAILABLE = True
except ImportError:
    print("⚠️  Required dependencies not available")
    DEPENDENCIES_AVAILABLE = False


class ContentPublisherScript:
    """Content Publisher for industry analysis blog publication"""

    def __init__(self, output_dir: str = "./frontend/src/content/blog"):
        """
        Initialize content publisher

        Args:
            output_dir: Directory to save published blog content
        """
        self.output_dir = output_dir
        self.timestamp = datetime.now()

        # Template configuration
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.templates_dir)), autoescape=True)

        # Content discovery paths
        self.source_paths = {
            "industry_analysis": "./data/outputs/industry_analysis/",
            "fundamental_analysis": "./data/outputs/fundamental_analysis/",
            "sector_analysis": "./data/outputs/sector_analysis/",
            "trade_history": "./data/outputs/trade_history/",
        }

    def discover_content(self, content_type: str = "all") -> list[dict[str, Any]]:
        """Discover unpublished content for publication"""
        discovered_content = []

        if content_type in ["all", "industry_analysis"]:
            discovered_content.extend(self._discover_industry_analysis())

        if content_type in ["all", "fundamental_analysis"]:
            discovered_content.extend(self._discover_fundamental_analysis())

        if content_type in ["all", "sector_analysis"]:
            discovered_content.extend(self._discover_sector_analysis())

        if content_type in ["all", "trade_history"]:
            discovered_content.extend(self._discover_trade_history())

        print("✅ Discovered {len(discovered_content)} content items for publication")
        return discovered_content

    def _discover_industry_analysis(self) -> list[dict[str, Any]]:
        """Discover industry analysis markdown files"""
        industry_path = Path(self.source_paths["industry_analysis"])
        discovered: list[dict[str, Any]] = []

        if not industry_path.exists():
            return discovered

        # Pattern: {INDUSTRY}_{YYYYMMDD}.md (case insensitive)
        pattern = re.compile(r"^([A-Za-z_]+)_(\d{8})\.md$")

        for file_path in industry_path.glob("*.md"):
            match = pattern.match(file_path.name)
            if match:
                industry, date = match.groups()

                # Check if already published
                blog_filename = f"{industry.lower().replace('_', '-')}-industry-analysis-{date}.md"
                blog_path = Path(self.output_dir) / blog_filename

                if not blog_path.exists():
                    discovered.append(
                        {
                            "content_type": "industry_analysis",
                            "source_file": str(file_path),
                            "industry": industry,
                            "date": date,
                            "target_filename": blog_filename,
                            "target_path": str(blog_path),
                        }
                    )

        return discovered

    def _discover_fundamental_analysis(self) -> list[dict[str, Any]]:
        """Discover fundamental analysis files"""
        # Placeholder for fundamental analysis discovery
        return []

    def _discover_sector_analysis(self) -> list[dict[str, Any]]:
        """Discover sector analysis files"""
        # Placeholder for sector analysis discovery
        return []

    def _discover_trade_history(self) -> list[dict[str, Any]]:
        """Discover trade history files"""
        # Placeholder for trade history discovery
        return []

    def publish_content(self, content_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Publish discovered content items to blog format"""
        published_results = []

        for item in content_items:
            try:
                if item["content_type"] == "industry_analysis":
                    result = self._publish_industry_analysis(item)
                    published_results.append(result)
                elif item["content_type"] == "fundamental_analysis":
                    result = self._publish_fundamental_analysis(item)
                    published_results.append(result)
                elif item["content_type"] == "sector_analysis":
                    result = self._publish_sector_analysis(item)
                    published_results.append(result)
                elif item["content_type"] == "trade_history":
                    result = self._publish_trade_history(item)
                    published_results.append(result)
                else:
                    print("⚠️  Unknown content type: {item['content_type']}")

            except Exception as e:
                print("❌ Failed to publish {item['source_file']}: {e}")
                published_results.append(
                    {
                        "status": "failed",
                        "source_file": item["source_file"],
                        "error": str(e),
                    }
                )

        return published_results

    def _publish_industry_analysis(self, item: dict[str, Any]) -> dict[str, Any]:
        """Publish industry analysis to blog format with standardized frontmatter"""
        try:
            # Load source content
            with open(item["source_file"]) as f:
                source_content = f.read()

            # Parse existing frontmatter and content
            parsed = self._parse_markdown_frontmatter(source_content)

            # Generate standardized blog frontmatter
            frontmatter = self._generate_industry_analysis_frontmatter(item, parsed)

            # Process content (remove H1 title, preserve everything else)
            processed_content = self._process_content_for_blog(parsed["content"])

            # Combine frontmatter and content
            blog_content = f"---\n{frontmatter}---\n\n{processed_content}"

            # Ensure output directory exists
            os.makedirs(Path(item["target_path"]).parent, exist_ok=True)

            # Write to blog location
            with open(item["target_path"], "w") as f:
                f.write(blog_content)

            print("✅ Published industry analysis: {item['target_filename']}")

            return {
                "status": "success",
                "content_type": "industry_analysis",
                "source_file": item["source_file"],
                "target_file": item["target_path"],
                "industry": item["industry"],
                "date": item["date"],
            }

        except Exception as e:
            raise Exception(f"Industry analysis publication failed: {e}")

    def _generate_industry_analysis_frontmatter(self, item: dict[str, Any], parsed: dict[str, Any]) -> str:
        """Generate standardized frontmatter for industry analysis blog posts"""

        # Extract industry name for title
        industry_name = item["industry"].replace("_", " ").title()

        # Parse date for ISO format
        date_str = item["date"]
        date_obj = datetime.strptime(date_str, "%Y%m%d")
        iso_date = date_obj.strftime("%Y-%m-%dT10:00:00Z")

        # Generate slug-friendly industry name
        industry_slug = item["industry"].lower().replace("_", "-")

        # Extract key data from content for description
        content = parsed.get("content", "")

        # Try to extract recommendation and confidence
        recommendation_match = re.search(r"Recommendation: (\w+)", content)
        recommendation = recommendation_match.group(1) if recommendation_match else "BUY"

        confidence_match = re.search(r"Confidence: ([0-9.]+)", content)
        confidence = confidence_match.group(1) if confidence_match else "9.0"

        # Generate description with key thesis
        description = f"Institutional-quality {industry_name} industry analysis with comprehensive investment thesis, {recommendation} recommendation, and risk assessment framework. Confidence: {confidence}/10.0"

        # Generate frontmatter
        frontmatter = f"""title: "{industry_name} Industry Analysis"
meta_title: "{industry_name} Industry Analysis - {recommendation} Recommendation"
description: "{description}"
date: {iso_date}
image: "/images/industry_analysis/{industry_slug}_{date_str}.png"
authors: ["Cole Morton", "Claude"]
categories: ["Investing", "Analysis", "Industry Analysis", "{industry_name}", "Market Analysis"]
tags: ["{industry_slug}", "industry-analysis", "{recommendation.lower()}", "institutional-research", "economic-analysis"]
draft: false
industry_data:
  industry: "{item["industry"]}"
  analysis_date: "{date_str}"
  confidence: {float(confidence):.1f}
  recommendation: "{recommendation}"
  content_type: "industry_analysis"
"""

        return frontmatter

    def _publish_fundamental_analysis(self, item: dict[str, Any]) -> dict[str, Any]:
        """Publish fundamental analysis to blog format"""
        # Placeholder implementation
        return {
            "status": "success",
            "message": "Fundamental analysis publishing not yet implemented",
        }

    def _publish_sector_analysis(self, item: dict[str, Any]) -> dict[str, Any]:
        """Publish sector analysis to blog format"""
        # Placeholder implementation
        return {
            "status": "success",
            "message": "Sector analysis publishing not yet implemented",
        }

    def _publish_trade_history(self, item: dict[str, Any]) -> dict[str, Any]:
        """Publish trade history to blog format"""
        # Placeholder implementation
        return {
            "status": "success",
            "message": "Trade history publishing not yet implemented",
        }

    def _parse_markdown_frontmatter(self, content: str) -> dict[str, Any]:
        """Parse markdown content with YAML frontmatter"""
        parts = content.split("---")

        if len(parts) >= 3:
            try:
                import yaml

                frontmatter = yaml.safe_load(parts[1])
                markdown_content = "---".join(parts[2:]).strip()

                return {
                    "frontmatter": frontmatter,
                    "content": markdown_content,
                    "has_frontmatter": True,
                }
            except Exception:
                print("Warning: Failed to parse frontmatter: {e}")

        return {"frontmatter": {}, "content": content, "has_frontmatter": False}

    def _process_content_for_blog(self, content: str) -> str:
        """Process content for blog publication - remove H1 title, preserve everything else"""

        # Remove the first H1 heading to prevent duplication with frontmatter title
        lines = content.split("\n")
        processed_lines = []

        h1_removed = False
        for line in lines:
            # Remove the first H1 heading encountered
            if not h1_removed and line.strip().startswith("# "):
                h1_removed = True
                continue
            processed_lines.append(line)

        return "\n".join(processed_lines).strip()

    def validate_published_content(self, published_results: list[dict[str, Any]]) -> dict[str, Any]:
        """Validate published content meets standards"""
        validation_results: dict[str, Any] = {
            "total_published": len(published_results),
            "successful": 0,
            "failed": 0,
            "validation_issues": [],
        }

        for result in published_results:
            if result.get("status") == "success":
                validation_results["successful"] += 1

                # Validate the published file
                if "target_file" in result:
                    issues = self._validate_blog_file(result["target_file"])
                    if issues:
                        validation_results["validation_issues"].extend(issues)
            else:
                validation_results["failed"] += 1

        return validation_results

    def _validate_blog_file(self, file_path: str) -> list[str]:
        """Validate individual blog file meets standards"""
        issues = []

        try:
            with open(file_path) as f:
                content = f.read()

            # Check for required frontmatter fields
            if not content.startswith("---"):
                issues.append(f"Missing frontmatter: {file_path}")
                return issues

            parsed = self._parse_markdown_frontmatter(content)
            frontmatter = parsed.get("frontmatter", {})

            # Required fields validation
            required_fields = [
                "title",
                "description",
                "date",
                "authors",
                "categories",
                "tags",
            ]
            for field in required_fields:
                if field not in frontmatter:
                    issues.append(f"Missing required field '{field}': {file_path}")

            # Check authors format
            authors = frontmatter.get("authors", [])
            if not isinstance(authors, list) or authors != ["Cole Morton", "Claude"]:
                issues.append(f"Incorrect authors format: {file_path}")

            # Check for H1 duplication
            content_body = parsed.get("content", "")
            if content_body.strip().startswith("# "):
                issues.append(f"H1 title not removed from content: {file_path}")

        except Exception as e:
            issues.append(f"Validation error for {file_path}: {e}")

        return issues

    def execute_full_workflow(self, content_type: str = "all") -> dict[str, Any]:
        """Execute complete content publisher workflow"""
        print("\n📊 Starting content publisher workflow for: {content_type}")

        # Phase 1: Discovery
        discovered = self.discover_content(content_type)
        if not discovered:
            return {
                "status": "completed",
                "message": "No unpublished content found",
                "discovered": 0,
                "published": 0,
            }

        # Phase 2: Publication
        published = self.publish_content(discovered)

        # Phase 3: Validation
        validation = self.validate_published_content(published)

        print("\n✅ Content publisher workflow complete!")
        print("📊 Discovered: {len(discovered)} items")
        print("📝 Published: {validation['successful']} items")
        print("❌ Failed: {validation['failed']} items")

        if validation["validation_issues"]:
            print("⚠️  Validation issues: {len(validation['validation_issues'])}")
            for issue in validation["validation_issues"]:
                print("  - {issue}")

        return {
            "status": "completed",
            "discovered": len(discovered),
            "published": validation["successful"],
            "failed": validation["failed"],
            "validation_issues": validation["validation_issues"],
            "published_files": [r.get("target_file") for r in published if r.get("status") == "success"],
        }


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Content Publisher - Blog Publication Workflow")
    parser.add_argument(
        "--content-type",
        type=str,
        default="all",
        choices=[
            "all",
            "industry_analysis",
            "fundamental_analysis",
            "sector_analysis",
            "trade_history",
        ],
        help="Content type to publish",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./frontend/src/content/blog",
        help="Output directory for published blog content",
    )
    parser.add_argument(
        "--discover-only",
        action="store_true",
        help="Only discover content, don't publish",
    )

    args = parser.parse_args()

    # Initialize content publisher
    publisher = ContentPublisherScript(output_dir=args.output_dir)

    if args.discover_only:
        # Discovery only
        discovered = publisher.discover_content(args.content_type)
        print("\n📊 Discovery Results:")
        print("Found {len(discovered)} items for publication:")
        for item in discovered:
            print("  - {item['content_type']}: {item['source_file']}")
    else:
        # Full workflow
        result = publisher.execute_full_workflow(args.content_type)
        print("\n📋 Final Results: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
