"""
Template Customization Validator

Ensures industry analysis files are properly customized and not using generic template placeholders.
Detects and flags template artifacts that indicate insufficient industry-specific customization.
"""

import json
import re
from pathlib import Path
from typing import Any


class TemplateCustomizationValidator:
    """Validates industry analysis files for proper customization vs template artifacts"""

    def __init__(self):
        # Generic template indicators
        self.generic_placeholders = [
            r"placeholder",
            r"template",
            r"example",
            r"_segment_1",
            r"_segment_2",
            r"emerging_technology",
            r"digital_transformation",
            r"N/A",
            r"Representative",
            r"company_name_here",
            r"industry_leader_1",
        ]

        # Generic numeric patterns that suggest template reuse
        self.generic_numeric_patterns = [
            (r"adoption_rate.*0\.75", "Generic 75% adoption rate"),
            (r"confidence.*0\.85", "Generic 85% confidence"),
            (r"growth_rate.*0\.15", "Generic 15% growth rate"),
            (r"market_share.*0\.25", "Generic 25% market share"),
        ]

        # Industry-specific validation requirements
        self.industry_requirements = {
            "software_infrastructure": {
                "required_companies": ["MSFT", "GOOGL", "AMZN", "CRM"],
                "required_technologies": ["cloud", "saas", "api", "microservices"],
                "prohibited_generic": ["Consumer_Electronics", "Medical_Device"],
            },
            "medical_devices": {
                "required_companies": ["MDT", "ABT", "BSX", "SYK"],
                "required_technologies": [
                    "diagnostic",
                    "surgical",
                    "robotic",
                    "implant",
                ],
                "prohibited_generic": ["Software_Infrastructure", "Internet_Retail"],
            },
            "internet_retail": {
                "required_companies": ["AMZN", "BABA", "JD", "SHOP"],
                "required_technologies": [
                    "ecommerce",
                    "logistics",
                    "fulfillment",
                    "marketplace",
                ],
                "prohibited_generic": ["Medical_Device", "Semiconductor"],
            },
            "semiconductors": {
                "required_companies": ["NVDA", "INTC", "TSM", "AMD"],
                "required_technologies": ["chip", "processor", "gpu", "fabrication"],
                "prohibited_generic": ["Internet_Retail", "Software_Infrastructure"],
            },
        }

    def validate_file(self, file_path: str) -> dict[str, Any]:
        """Validate a single industry analysis file for customization quality"""

        try:
            with open(file_path) as f:
                if file_path.endswith(".json"):
                    data = json.load(f)
                    return self._validate_json_file(data, file_path)
                content = f.read()
                return self._validate_markdown_file(content, file_path)

        except Exception as e:
            return {
                "file_path": file_path,
                "validation_status": "error",
                "error": str(e),
                "customization_score": 0.0,
            }

    def _validate_json_file(self, data: dict[str, Any], file_path: str) -> dict[str, Any]:
        """Validate JSON file for template customization"""

        # Extract industry from metadata or filename
        industry = self._extract_industry(data, file_path)

        # Check for generic placeholders
        placeholder_issues = self._find_generic_placeholders(data)

        # Check for industry-specific content
        industry_specificity = self._validate_industry_specificity(data, industry)

        # Check representative companies
        company_validation = self._validate_representative_companies(data, industry)

        # Calculate customization score
        customization_score = self._calculate_customization_score(
            placeholder_issues, industry_specificity, company_validation
        )

        return {
            "file_path": file_path,
            "industry": industry,
            "validation_status": "completed",
            "customization_score": customization_score,
            "customization_grade": self._score_to_grade(customization_score),
            "placeholder_issues": placeholder_issues,
            "industry_specificity": industry_specificity,
            "company_validation": company_validation,
            "recommendations": self._generate_recommendations(
                placeholder_issues, industry_specificity, company_validation, industry
            ),
        }

    def _validate_markdown_file(self, content: str, file_path: str) -> dict[str, Any]:
        """Validate Markdown file for template customization"""

        # Extract industry from filename
        industry = self._extract_industry_from_filename(file_path)

        # Check for generic placeholders in text
        placeholder_count = 0
        placeholder_examples = []

        for pattern in self.generic_placeholders:
            matches = re.findall(pattern, content, re.IGNORECASE)
            placeholder_count += len(matches)
            if matches:
                placeholder_examples.extend(matches[:3])  # Limit examples

        # Check for industry-specific terminology
        industry_terms_found = 0
        if industry in self.industry_requirements:
            for tech in self.industry_requirements[industry]["required_technologies"]:
                if tech.lower() in content.lower():
                    industry_terms_found += 1

        # Calculate customization score for markdown
        max_score = 1.0
        placeholder_penalty = min(0.5, placeholder_count * 0.1)
        industry_bonus = min(0.3, industry_terms_found * 0.1)

        customization_score = max(0.0, max_score - placeholder_penalty + industry_bonus)

        return {
            "file_path": file_path,
            "industry": industry,
            "validation_status": "completed",
            "customization_score": customization_score,
            "customization_grade": self._score_to_grade(customization_score),
            "placeholder_count": placeholder_count,
            "placeholder_examples": placeholder_examples[:5],
            "industry_terms_found": industry_terms_found,
            "recommendations": [
                "Remove generic placeholders and template text",
                f"Add more {industry}-specific terminology and analysis",
                "Ensure all content is customized for the specific industry",
            ],
        }

    def _extract_industry(self, data: dict[str, Any], file_path: str) -> str:
        """Extract industry from data or filename"""

        # Try metadata first
        if "metadata" in data and "industry" in data["metadata"]:
            return data["metadata"]["industry"]

        # Try industry_scope
        if "industry_scope" in data and "industry_name" in data["industry_scope"]:
            return data["industry_scope"]["industry_name"]

        # Fall back to filename
        return self._extract_industry_from_filename(file_path)

    def _extract_industry_from_filename(self, file_path: str) -> str:
        """Extract industry from filename"""

        filename = Path(file_path).stem

        # Common industry patterns in filenames
        if "software_infrastructure" in filename.lower():
            return "software_infrastructure"
        if "medical_devices" in filename.lower():
            return "medical_devices"
        if "internet_retail" in filename.lower():
            return "internet_retail"
        if "semiconductors" in filename.lower():
            return "semiconductors"
        if "internet_content" in filename.lower():
            return "internet_content_and_information"

        return "unknown"

    def _find_generic_placeholders(self, data: Any, path: str = "") -> list[dict[str, str]]:
        """Recursively find generic placeholders in data structure"""

        issues = []

        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key

                # Check key for placeholders
                for pattern in self.generic_placeholders:
                    if re.search(pattern, key, re.IGNORECASE):
                        issues.append(
                            {
                                "type": "placeholder_key",
                                "path": current_path,
                                "issue": f"Generic placeholder in key: {key}",
                                "severity": "high",
                            }
                        )

                # Recursively check value
                issues.extend(self._find_generic_placeholders(value, current_path))

        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                issues.extend(self._find_generic_placeholders(item, current_path))

        elif isinstance(data, str):
            # Check string values for placeholders
            for pattern in self.generic_placeholders:
                if re.search(pattern, data, re.IGNORECASE):
                    issues.append(
                        {
                            "type": "placeholder_value",
                            "path": path,
                            "issue": f"Generic placeholder in value: {data}",
                            "severity": ("high" if "N/A" in data or "Representative" in data else "medium"),
                        }
                    )
                    break

        return issues

    def _validate_industry_specificity(self, data: dict[str, Any], industry: str) -> dict[str, Any]:
        """Validate that content is industry-specific"""

        if industry not in self.industry_requirements:
            return {
                "status": "unknown_industry",
                "score": 0.5,
                "details": f"No validation rules for industry: {industry}",
            }

        requirements = self.industry_requirements[industry]

        # Convert data to string for searching
        data_str = json.dumps(data, default=str).lower()

        # Check for required technologies
        tech_found = []
        for tech in requirements["required_technologies"]:
            if tech.lower() in data_str:
                tech_found.append(tech)

        # Check for prohibited generic terms
        prohibited_found = []
        for term in requirements["prohibited_generic"]:
            if term.lower() in data_str:
                prohibited_found.append(term)

        # Calculate specificity score
        tech_score = len(tech_found) / len(requirements["required_technologies"])
        prohibited_penalty = len(prohibited_found) * 0.2

        specificity_score = max(0.0, tech_score - prohibited_penalty)

        return {
            "status": "validated",
            "score": specificity_score,
            "technologies_found": tech_found,
            "technologies_missing": [t for t in requirements["required_technologies"] if t not in tech_found],
            "prohibited_terms_found": prohibited_found,
            "details": f"Found {len(tech_found)}/{len(requirements['required_technologies'])} required technologies",
        }

    def _validate_representative_companies(self, data: dict[str, Any], industry: str) -> dict[str, Any]:
        """Validate representative companies are industry-appropriate"""

        # Find representative companies in data
        companies_found = []

        def find_companies(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if "compan" in key.lower() or "representative" in key.lower():
                        if isinstance(value, list):
                            for item in value:
                                if isinstance(item, dict) and "symbol" in item:
                                    companies_found.append(item["symbol"])
                        elif isinstance(value, dict) and "symbol" in value:
                            companies_found.append(value["symbol"])
                    find_companies(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_companies(item, f"{path}[{i}]")

        find_companies(data)

        if not companies_found:
            return {
                "status": "no_companies_found",
                "score": 0.0,
                "details": "No representative companies found in data",
            }

        # Check for placeholder companies
        placeholder_companies = [c for c in companies_found if "N/A" in c or "Representative" in c]
        real_companies = [c for c in companies_found if c not in placeholder_companies]

        # Check industry appropriateness
        industry_appropriate = []
        if industry in self.industry_requirements:
            expected_companies = self.industry_requirements[industry]["required_companies"]
            industry_appropriate = [c for c in real_companies if c in expected_companies]

        # Calculate score
        if placeholder_companies:
            score = 0.0  # Placeholders are blocking issues
        elif real_companies:
            score = min(1.0, len(industry_appropriate) / max(1, len(real_companies)))
        else:
            score = 0.0

        return {
            "status": "validated",
            "score": score,
            "total_companies": len(companies_found),
            "real_companies": real_companies,
            "placeholder_companies": placeholder_companies,
            "industry_appropriate": industry_appropriate,
            "details": f"Found {len(real_companies)} real companies, {len(placeholder_companies)} placeholders",
        }

    def _calculate_customization_score(
        self,
        placeholder_issues: list[dict],
        industry_specificity: dict,
        company_validation: dict,
    ) -> float:
        """Calculate overall customization score"""

        # Base score
        score = 1.0

        # Placeholder penalty
        high_severity_issues = [i for i in placeholder_issues if i.get("severity") == "high"]
        medium_severity_issues = [i for i in placeholder_issues if i.get("severity") == "medium"]

        placeholder_penalty = len(high_severity_issues) * 0.3 + len(medium_severity_issues) * 0.1
        score -= min(0.8, placeholder_penalty)

        # Industry specificity bonus/penalty
        specificity_score = industry_specificity.get("score", 0.5)
        score = score * (0.5 + 0.5 * specificity_score)

        # Company validation impact
        company_score = company_validation.get("score", 0.5)
        if company_score == 0.0 and company_validation.get("placeholder_companies"):
            score = 0.0  # Placeholder companies are blocking
        else:
            score = score * (0.7 + 0.3 * company_score)

        return max(0.0, min(1.0, score))

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""

        if score >= 0.9:
            return "A"
        if score >= 0.8:
            return "B"
        if score >= 0.7:
            return "C"
        if score >= 0.6:
            return "D"
        return "F"

    def _generate_recommendations(
        self,
        placeholder_issues: list[dict],
        industry_specificity: dict,
        company_validation: dict,
        industry: str,
    ) -> list[str]:
        """Generate specific recommendations for improvement"""

        recommendations = []

        # Placeholder issues
        if placeholder_issues:
            high_severity = [i for i in placeholder_issues if i.get("severity") == "high"]
            if high_severity:
                recommendations.append("CRITICAL: Remove placeholder companies and generic template content")
            recommendations.append(f"Fix {len(placeholder_issues)} placeholder issues in the analysis")

        # Industry specificity
        if industry_specificity.get("score", 0) < 0.7:
            missing_techs = industry_specificity.get("technologies_missing", [])
            if missing_techs:
                recommendations.append(f"Add {industry}-specific technologies: {', '.join(missing_techs[:3])}")

        # Company validation
        if company_validation.get("placeholder_companies"):
            recommendations.append("Replace placeholder companies with real industry representatives")
        elif company_validation.get("score", 0) < 0.7:
            recommendations.append(f"Add more industry-appropriate companies for {industry}")

        # Generic recommendations
        if not recommendations:
            recommendations.append(f"Enhance industry-specific analysis depth for {industry}")

        return recommendations


def validate_industry_analysis_customization(
    directory: str = "./data/outputs/industry_analysis",
) -> dict[str, Any]:
    """Validate template customization across all industry analysis files"""

    validator = TemplateCustomizationValidator()
    results = []

    # Validate discovery files
    discovery_dir = Path(directory) / "discovery"
    if discovery_dir.exists():
        for file_path in discovery_dir.glob("*.json"):
            result = validator.validate_file(str(file_path))
            result["file_type"] = "discovery"
            results.append(result)

    # Validate analysis files
    analysis_dir = Path(directory) / "analysis"
    if analysis_dir.exists():
        for file_path in analysis_dir.glob("*.json"):
            result = validator.validate_file(str(file_path))
            result["file_type"] = "analysis"
            results.append(result)

    # Validate synthesis files (markdown)
    for file_path in Path(directory).glob("*.md"):
        result = validator.validate_file(str(file_path))
        result["file_type"] = "synthesis"
        results.append(result)

    # Summary statistics
    total_files = len(results)
    avg_score = sum(r["customization_score"] for r in results) / max(1, total_files)
    grade_distribution: dict[str, int] = {}
    for result in results:
        grade = result.get("customization_grade", "F")
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1

    # Find critical issues
    critical_issues = [r for r in results if r["customization_score"] < 0.3]

    return {
        "summary": {
            "total_files_validated": total_files,
            "average_customization_score": round(avg_score, 3),
            "grade_distribution": grade_distribution,
            "critical_issues_count": len(critical_issues),
        },
        "critical_issues": critical_issues,
        "detailed_results": results,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "./data/outputs/industry_analysis"

    print("Validating template customization in {directory}")
    results = validate_industry_analysis_customization(directory)

    print("\nCustomization Validation Results:")
    print(json.dumps(results["summary"], indent=2))

    if results["critical_issues"]:
        print("\nCritical Issues Found ({len(results['critical_issues'])}):")
        for issue in results["critical_issues"]:
            print("  - {issue['file_path']}: Score {issue['customization_score']:.2f}")
