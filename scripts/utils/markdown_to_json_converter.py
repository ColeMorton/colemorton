#!/usr/bin/env python3
"""
Markdown to JSON Converter for Fundamental Analysis Data

Converts fundamental analysis markdown files to JSON format for script processing.
"""

import json
import re
from pathlib import Path
from typing import Any


class MarkdownToJsonConverter:
    """Converts fundamental analysis markdown to JSON format"""

    def __init__(self):
        self.data = {}

    def convert_file(self, markdown_file: Path) -> dict[str, Any]:
        """Convert markdown file to JSON structure"""

        with open(markdown_file, encoding="utf-8") as f:
            content = f.read()

        # Extract frontmatter
        frontmatter = self._extract_frontmatter(content)

        # Extract key sections
        _ = self._parse_sections(content)

        # Extract all the data
        catalysts = self._extract_catalysts(content)
        risk_factors = self._extract_risk_factors(content)
        fair_value = self._extract_fair_value(content)
        current_price = self._extract_current_price(content)

        # Calculate additional fields for templates
        total_expected_value = self._calculate_total_expected_value(catalysts, current_price)
        top_risk_factor = self._get_top_risk_factor(risk_factors)
        timeline_detail = self._extract_timeline_detail(content)

        # Build JSON structure
        json_data = {
            "ticker": self._extract_ticker(frontmatter.get("title", "")),
            "date": self._extract_date(frontmatter.get("date", "")),
            "current_price": current_price,
            "fair_value": fair_value,
            "recommendation": self._extract_recommendation(content),
            "catalysts": catalysts,
            "risk_factors": risk_factors,
            "valuation_metrics": self._extract_valuation_metrics(content),
            "financial_health": self._extract_financial_health(content),
            "economic_sensitivity": self._extract_economic_sensitivity(content),
            "moat_strength": self._extract_moat_strength(content),
            "template_context": self._determine_template_context(content),
            "metadata": frontmatter,
            # Additional fields for template compatibility
            "total_expected_value": total_expected_value,
            "top_risk_factor": top_risk_factor,
            "timeline_detail": timeline_detail,
            # Individual catalyst fields (fallback)
            "catalyst_1": (catalysts[0]["name"] if len(catalysts) > 0 else "AI memory demand growth"),
            "catalyst_1_probability": (catalysts[0]["probability"] if len(catalysts) > 0 else 85),
            "catalyst_1_impact": catalysts[0]["impact"] if len(catalysts) > 0 else 15,
            "catalyst_2": (catalysts[1]["name"] if len(catalysts) > 1 else "Memory pricing recovery"),
            "catalyst_2_probability": (catalysts[1]["probability"] if len(catalysts) > 1 else 70),
            "catalyst_2_impact": catalysts[1]["impact"] if len(catalysts) > 1 else 25,
            "catalyst_3": (catalysts[2]["name"] if len(catalysts) > 2 else "Data center upgrades"),
            "catalyst_3_probability": (catalysts[2]["probability"] if len(catalysts) > 2 else 75),
            "catalyst_3_impact": catalysts[2]["impact"] if len(catalysts) > 2 else 12,
        }

        return json_data

    def _extract_frontmatter(self, content: str) -> dict[str, Any]:
        """Extract YAML frontmatter"""

        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not match:
            return {}

        frontmatter_text = match.group(1)
        frontmatter = {}

        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def _parse_sections(self, content: str) -> dict[str, str]:
        """Parse content into sections"""

        sections = {}
        current_section = None
        current_content: list[str] = []

        lines = content.split("\n")

        for line in lines:
            if line.startswith("##") or line.startswith("#"):
                if current_section:
                    sections[current_section] = "\n".join(current_content)

                current_section = line.strip("# ").lower().replace(" ", "_")
                current_content = []
            else:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content)

        return sections

    def _extract_ticker(self, title: str) -> str:
        """Extract ticker from title"""

        match = re.search(r"\(([A-Z]+)\)", title)
        return match.group(1) if match else ""

    def _extract_date(self, date_str: str) -> str:
        """Extract date in YYYYMMDD format"""

        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", date_str)
        if match:
            return f"{match.group(1)}{match.group(2)}{match.group(3)}"
        return ""

    def _extract_current_price(self, content: str) -> float:
        """Extract current price"""

        match = re.search(r"Current:\s*\$(\d+\.?\d*)", content)
        return float(match.group(1)) if match else 0.0

    def _extract_fair_value(self, content: str) -> dict[str, float]:
        """Extract fair value range"""

        match = re.search(r"Fair Value Range.*?\$(\d+)\s*-\s*\$(\d+)", content)
        if match:
            return {
                "low": float(match.group(1)),
                "high": float(match.group(2)),
                "mid": (float(match.group(1)) + float(match.group(2))) / 2,
            }
        return {"low": 0.0, "high": 0.0, "mid": 0.0}

    def _extract_recommendation(self, content: str) -> dict[str, Any]:
        """Extract investment recommendation"""

        recommendation = {}

        # Extract recommendation
        rec_match = re.search(r"Recommendation:\s*(\w+)", content)
        if rec_match:
            recommendation["action"] = rec_match.group(1)

        # Extract conviction
        conv_match = re.search(r"Conviction:\s*(\d+\.?\d*)", content)
        if conv_match:
            recommendation["conviction"] = float(conv_match.group(1))

        # Extract expected return
        ret_match = re.search(r"Expected Return.*?(\d+)%", content)
        if ret_match:
            recommendation["expected_return"] = float(ret_match.group(1)) / 100

        return recommendation

    def _extract_catalysts(self, content: str) -> list[dict[str, Any]]:
        """Extract key catalysts"""

        catalysts = []

        # Look for catalyst section
        catalyst_section = re.search(r"Key Quantified Catalysts.*?\n(.*?)(?=###|\n##|\Z)", content, re.DOTALL)
        if catalyst_section:
            catalyst_text = catalyst_section.group(1)

            # Parse numbered catalysts
            for match in re.finditer(
                r"(\d+)\.\s*(.*?)-\s*Probability:\s*(\d+\.?\d*)\s*\|\s*Impact:\s*\$(\d+)",
                catalyst_text,
            ):
                catalysts.append(
                    {
                        "name": match.group(2).strip(),
                        "description": match.group(2).strip(),
                        "probability": float(match.group(3)) * 100,  # Convert to percentage
                        "impact": float(match.group(4)),
                        "impact_per_share": float(match.group(4)),
                    }
                )

        return catalysts

    def _extract_risk_factors(self, content: str) -> list[dict[str, Any]]:
        """Extract risk factors"""

        risks = []

        # Look for risk matrix section
        risk_section = re.search(r"Risk Matrix.*?\n(.*?)(?=###|\n##|\Z)", content, re.DOTALL)
        if risk_section:
            risk_text = risk_section.group(1)

            # Parse risk table
            for line in risk_text.split("\n"):
                if "|" in line and "Risk Factor" not in line and "---" not in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 4:
                        try:
                            risks.append(
                                {
                                    "factor": parts[1],
                                    "probability": float(parts[2]),
                                    "impact": int(parts[3]),
                                    "score": float(parts[4]) if len(parts) > 4 else 0.0,
                                }
                            )
                        except (ValueError, IndexError):
                            continue

        return risks

    def _extract_valuation_metrics(self, content: str) -> dict[str, Any]:
        """Extract valuation metrics"""

        metrics = {}

        # Extract P/E ratio
        pe_match = re.search(r"P/E Ratio.*?(\d+\.?\d*)", content)
        if pe_match:
            metrics["pe_ratio"] = float(pe_match.group(1))

        # Extract weighted average fair value
        weighted_match = re.search(r"Weighted Average.*?\$(\d+)", content)
        if weighted_match:
            metrics["weighted_fair_value"] = float(weighted_match.group(1))

        return metrics

    def _extract_financial_health(self, content: str) -> dict[str, Any]:
        """Extract financial health metrics"""

        health = {}

        # Extract debt-to-equity
        de_match = re.search(r"D/E:\s*(\d+\.?\d*)", content)
        if de_match:
            health["debt_to_equity"] = float(de_match.group(1))

        # Extract current ratio
        cr_match = re.search(r"Current Ratio:\s*(\d+\.?\d*)", content)
        if cr_match:
            health["current_ratio"] = float(cr_match.group(1))

        # Extract FCF
        fcf_match = re.search(r"FCF:\s*\$(\d+\.?\d*)B", content)
        if fcf_match:
            health["free_cash_flow"] = float(fcf_match.group(1)) * 1000000000

        return health

    def _extract_economic_sensitivity(self, content: str) -> dict[str, Any]:
        """Extract economic sensitivity data"""

        sensitivity = {}

        # Extract GDP correlation
        gdp_match = re.search(r"GDP Growth Rate.*?([+-]?\d+\.?\d*)", content)
        if gdp_match:
            sensitivity["gdp_correlation"] = float(gdp_match.group(1))

        # Extract interest rate sensitivity
        rate_match = re.search(r"Fed Funds Rate.*?([+-]?\d+\.?\d*)", content)
        if rate_match:
            sensitivity["interest_rate_sensitivity"] = float(rate_match.group(1))

        return sensitivity

    def _extract_moat_strength(self, content: str) -> dict[str, Any]:
        """Extract competitive moat information"""

        moat = {}

        # Extract overall moat strength (simplified)
        if "Strong" in content and "competitive" in content.lower():
            moat["strength"] = "Strong"
            moat["score"] = "8.0"
        elif "Moderate" in content and "competitive" in content.lower():
            moat["strength"] = "Moderate"
            moat["score"] = "6.0"
        else:
            moat["strength"] = "Weak"
            moat["score"] = "4.0"

        return moat

    def _determine_template_context(self, content: str) -> dict[str, Any]:
        """Determine optimal template context"""

        context = {}

        # Check for valuation disconnect (Template A)
        fair_value = self._extract_fair_value(content)
        current_price = self._extract_current_price(content)

        if fair_value["mid"] > 0 and current_price > 0:
            upside = (fair_value["mid"] - current_price) / current_price
            if upside > 0.25:  # 25%+ upside
                context["template_preference"] = "A_valuation"
                context["valuation_disconnect"] = "True"
                context["upside_potential"] = str(upside)

        # Check for catalyst-driven (Template B)
        catalysts = self._extract_catalysts(content)
        if len(catalysts) >= 2:
            high_prob_catalysts = [c for c in catalysts if c.get("probability", 0) > 0.7]
            if high_prob_catalysts:
                context["template_preference"] = "B_catalyst"
                context["catalyst_driven"] = "True"

        # Default to balanced if no clear preference
        if "template_preference" not in context:
            context["template_preference"] = "C_balanced"

        return context

    def _calculate_total_expected_value(self, catalysts: list[dict[str, Any]], current_price: float) -> float:
        """Calculate total expected value if all catalysts hit"""

        if not catalysts or current_price <= 0:
            return current_price

        total_impact = sum(catalyst.get("impact", 0) for catalyst in catalysts)
        return current_price + total_impact

    def _get_top_risk_factor(self, risk_factors: list[dict[str, Any]]) -> str:
        """Get the highest scoring risk factor"""

        if not risk_factors:
            return "Market volatility and execution risk"

        # Sort by risk score (probability * impact)
        sorted_risks = sorted(risk_factors, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_risks[0].get("factor", "Key risk factor")

    def _extract_timeline_detail(self, content: str) -> str:
        """Extract timeline information"""

        # Look for timeline mentions
        timeline_patterns = [
            r"Timeline:\s*([^|\n]+)",
            r"(\d+-\d+\s*month[s]?)",
            r"(within\s+\d+\s+months?)",
            r"(next\s+\d+-\d+\s+quarters?)",
        ]

        for pattern in timeline_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return "Multiple catalysts expected within 6-18 months"

    def save_json(self, json_data: dict[str, Any], output_file: Path) -> None:
        """Save JSON data to file"""

        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def convert_markdown_to_json(markdown_file: Path, output_file: Path | None = None) -> Path:
    """Convert markdown file to JSON format"""

    converter = MarkdownToJsonConverter()
    json_data = converter.convert_file(markdown_file)

    if output_file is None:
        output_file = markdown_file.with_suffix(".json")

    converter.save_json(json_data, output_file)
    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python markdown_to_json_converter.py <markdown_file> [output_file]")
        sys.exit(1)

    markdown_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    result_file = convert_markdown_to_json(markdown_file, output_file)
    print("Converted to: {result_file}")
