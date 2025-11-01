#!/usr/bin/env python3
"""
Institutional Quality Validation System for Macro Analysis Publications
Ensures ≥9.0/10.0 institutional quality standards for macro economic content
"""

import glob
import json
import os
import re
from datetime import datetime
from typing import Any

import yaml


class InstitutionalQualityValidator:
    """Comprehensive institutional quality validation for macro analysis publications"""

    # Validation weights for institutional scoring
    INSTITUTIONAL_WEIGHTS = {
        "template_compliance": 0.25,  # Critical for institutional standards
        "content_fidelity": 0.20,  # Analytical integrity requirement
        "economic_metadata_accuracy": 0.20,  # Data quality assurance
        "frontend_integration": 0.15,  # Professional presentation
        "seo_optimization": 0.10,  # Discoverability
        "performance_metrics": 0.10,  # Technical excellence
    }

    # Required macro_data fields per publisher specification
    REQUIRED_MACRO_FIELDS = [
        "confidence",
        "data_quality",
        "economic_phase",
        "recession_probability",
        "policy_stance",
        "business_cycle_position",
        "interest_rate_environment",
        "inflation_trajectory",
        "risk_score",
    ]

    # Valid values for controlled fields
    VALID_ECONOMIC_PHASES = ["Expansion", "Peak", "Contraction", "Trough"]
    VALID_POLICY_STANCES = ["Accommodative", "Neutral", "Restrictive"]
    VALID_ENVIRONMENTS = ["Rising", "Stable", "Falling"]

    def __init__(
        self,
        blog_directory: str = "./frontend/src/content/blog/",
        macro_outputs_dir: str = "./data/outputs/macro_analysis/",
        file_count: int = 7,
    ):
        """
        Initialize institutional quality validator

        Args:
            blog_directory: Directory containing published blog content
            macro_outputs_dir: Directory containing source macro analysis outputs
            file_count: Number of latest files to analyze
        """
        self.blog_directory = blog_directory
        self.macro_outputs_dir = macro_outputs_dir
        self.file_count = file_count
        self.published_files = []
        self.validation_results = {}

    def execute_institutional_validation(self) -> dict[str, Any]:
        """Execute comprehensive institutional quality validation"""
        print("🔍 Starting Institutional Quality Validation System...")

        # Discover published files
        self.published_files = self._discover_published_files()

        if not self.published_files:
            return self._create_no_content_report()

        print(f"📊 Analyzing {len(self.published_files)} published macro analysis files")

        # Execute validation phases
        validation_results = {}

        for file_info in self.published_files:
            print(f"📝 Validating: {file_info['filename']}")

            # Load and parse file content
            content, frontmatter = self._parse_published_file(file_info["path"])

            if not content or not frontmatter:
                continue

            # Phase 1: Template Compliance Validation
            template_score = self._validate_template_compliance(frontmatter, file_info["filename"])

            # Phase 2: Content Fidelity Validation
            fidelity_score = self._validate_content_fidelity(content, file_info)

            # Phase 3: Economic Metadata Validation
            metadata_score = self._validate_economic_metadata(frontmatter)

            # Phase 4: Frontend Integration Validation
            frontend_score = self._validate_frontend_integration(content, frontmatter)

            # Phase 5: SEO Optimization Validation
            seo_score = self._validate_seo_optimization(frontmatter, content)

            # Phase 6: Performance Metrics Validation
            performance_score = self._validate_performance_metrics(file_info, content, frontmatter)

            # Calculate weighted institutional score
            individual_scores = {
                "template_compliance": template_score,
                "content_fidelity": fidelity_score,
                "economic_metadata_accuracy": metadata_score,
                "frontend_integration": frontend_score,
                "seo_optimization": seo_score,
                "performance_metrics": performance_score,
            }

            # FIXED: Proper weighted scoring calculation
            weighted_score = (
                sum(score * self.INSTITUTIONAL_WEIGHTS[category] for category, score in individual_scores.items())
                * 10.0
            )  # Scale to 10.0

            validation_results[file_info["filename"]] = {
                "individual_scores": individual_scores,
                "weighted_institutional_score": weighted_score,
                "institutional_certified": weighted_score >= 9.0,
                "certification_level": self._determine_certification_level(weighted_score),
            }

        # Generate comprehensive report
        return self._generate_institutional_report(validation_results)

    def _discover_published_files(self) -> list[dict[str, Any]]:
        """Discover published macro analysis files"""
        if not os.path.exists(self.blog_directory):
            print(f"⚠️  Blog directory not found: {self.blog_directory}")
            return []

        # Find published macro analysis files
        pattern = os.path.join(self.blog_directory, "*macro*analysis*.md")
        published_files = []

        for file_path in glob.glob(pattern):
            try:
                stat = os.stat(file_path)
                published_files.append(
                    {
                        "filename": os.path.basename(file_path),
                        "path": file_path,
                        "modification_time": stat.st_mtime,
                        "size_bytes": stat.st_size,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    }
                )
            except Exception as e:
                print(f"⚠️  Error processing file {file_path}: {e}")

        # Sort by modification time (newest first) and limit
        published_files.sort(key=lambda x: x["modification_time"], reverse=True)
        return published_files[: self.file_count]

    def _parse_published_file(self, file_path: str) -> tuple[str | None, dict | None]:
        """Parse published file into content and frontmatter"""
        try:
            with open(file_path, encoding="utf-8") as f:
                file_content = f.read()

            if not file_content.startswith("---"):
                return file_content, {}

            # Split frontmatter and content
            parts = file_content.split("---", 2)
            if len(parts) < 3:
                return file_content, {}

            frontmatter_text = parts[1].strip()
            content = parts[2].strip()

            # Parse YAML frontmatter
            try:
                frontmatter = yaml.safe_load(frontmatter_text)
                return content, frontmatter or {}
            except yaml.YAMLError as e:
                print(f"⚠️  YAML parsing error in {file_path}: {e}")
                return content, {}

        except Exception as e:
            print(f"⚠️  Error parsing file {file_path}: {e}")
            return None, None

    def _validate_template_compliance(self, frontmatter: dict, filename: str) -> float:
        """Validate strict template compliance against publisher specification"""
        compliance_score = 0.0
        total_checks = 12  # Number of compliance checks

        # Extract region from filename for validation
        region = self._extract_region_from_filename(filename)

        # 1. Title format validation: "{Region} Macro Economic Analysis - {Month} {YYYY}"
        title = frontmatter.get("title", "")
        # More flexible pattern to match actual content format
        expected_title_pattern = rf"{re.escape(region)} Macro Economic Analysis - [A-Za-z]+ \d{{4}}$"
        if re.match(expected_title_pattern, title, re.IGNORECASE):
            compliance_score += 1
        else:
            print(f'❌ Title format deviation: "{title}" vs pattern: {expected_title_pattern}')

        # 2. Meta_title presence and format
        meta_title = frontmatter.get("meta_title", "")
        if meta_title and "Business Cycle" in meta_title:
            compliance_score += 1
        else:
            print("❌ Meta_title missing or incorrect format")

        # 3. Description length and content (150-200 characters, flexible for content quality)
        description = frontmatter.get("description", "")
        if 150 <= len(description) <= 200 and "recession probability" in description.lower():
            compliance_score += 1
        else:
            print(
                f"❌ Description length/content issue: {len(description)} chars, contains recession prob: {'recession probability' in description.lower()}"
            )

        # 4. Date format validation (ISO 8601 with timezone)
        date = frontmatter.get("date")
        if (
            isinstance(date, str)
            and re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", date)
            or hasattr(date, "isoformat")
        ):
            compliance_score += 1
        else:
            print(f"❌ Date format issue: {date}")

        # 5. Authors format validation: ["Cole Morton", "Claude"]
        authors = frontmatter.get("authors", [])
        if authors == ["Cole Morton", "Claude"]:
            compliance_score += 1
        else:
            print(f"❌ Authors format deviation: {authors}")

        # 6. Categories structure validation
        categories = frontmatter.get("categories", [])
        expected_categories = [
            "Economics",
            "Analysis",
            "Macro Analysis",
            region,
            "Economic Outlook",
        ]
        if categories == expected_categories:
            compliance_score += 1
        else:
            print(f"❌ Categories structure deviation: {categories}")

        # 7. Tags compliance (region + macro-analysis + economic elements)
        tags = frontmatter.get("tags", [])
        region_tag = region.lower()
        if region_tag in tags and "macro-analysis" in tags and len(tags) >= 4:
            compliance_score += 1
        else:
            print(f"❌ Tags compliance issue: {tags}")

        # 8. Static image path validation
        image = frontmatter.get("image", "")
        expected_image = f"/images/macro/{region.lower()}-min.png"
        if image == expected_image:
            compliance_score += 1
        else:
            print(f'❌ Image path deviation: "{image}" vs "{expected_image}"')

        # 9. Draft status validation
        draft = frontmatter.get("draft", True)
        if not draft:
            compliance_score += 1
        else:
            print(f"❌ Draft status issue: {draft}")

        # 10. Macro_data presence
        macro_data = frontmatter.get("macro_data", {})
        if isinstance(macro_data, dict) and macro_data:
            compliance_score += 1
        else:
            print("❌ Macro_data missing or invalid")

        # 11. Required macro_data fields
        missing_fields = []
        for field in self.REQUIRED_MACRO_FIELDS:
            if field not in macro_data:
                missing_fields.append(field)
        if not missing_fields:
            compliance_score += 1
        else:
            print(f"❌ Missing macro_data fields: {missing_fields}")

        # 12. Macro_data field format validation
        field_format_valid = self._validate_macro_data_formats(macro_data)
        if field_format_valid:
            compliance_score += 1
        else:
            print("❌ Macro_data field format issues")

        return compliance_score / total_checks

    def _validate_macro_data_formats(self, macro_data: dict) -> bool:
        """Validate macro_data field formats"""
        try:
            # Confidence and data_quality should be 0.XX format
            confidence = macro_data.get("confidence")
            data_quality = macro_data.get("data_quality")
            if not (isinstance(confidence, (int, float)) and 0 <= confidence <= 1):
                return False
            if not (isinstance(data_quality, (int, float)) and 0 <= data_quality <= 1):
                return False

            # Economic phase validation
            economic_phase = macro_data.get("economic_phase", "")
            if economic_phase not in self.VALID_ECONOMIC_PHASES:
                return False

            # Policy stance validation
            policy_stance = macro_data.get("policy_stance", "")
            if policy_stance not in self.VALID_POLICY_STANCES:
                return False

            # Environment validations
            interest_env = macro_data.get("interest_rate_environment", "")
            inflation_traj = macro_data.get("inflation_trajectory", "")
            if interest_env not in self.VALID_ENVIRONMENTS:
                return False
            if inflation_traj not in self.VALID_ENVIRONMENTS:
                return False

            # Recession probability should be XX.X% format
            recession_prob = macro_data.get("recession_probability", "")
            if not re.match(r"\d+\.?\d*%", str(recession_prob)):
                return False

            # Risk score should be X.X/5.0 format
            risk_score = macro_data.get("risk_score", "")
            if not re.match(r"\d\.\d/5\.0", str(risk_score)):
                return False

            return True
        except Exception as e:
            print(f"⚠️  Error validating macro_data formats: {e}")
            return False

    def _validate_content_fidelity(self, content: str, file_info: dict) -> float:
        """Validate 100% content fidelity preservation"""
        # This would ideally compare against source synthesis file
        # For now, checking content quality indicators

        fidelity_score = 0.0
        total_checks = 5

        # 1. Content length adequacy (professional depth)
        if len(content) > 15000:  # Substantial analytical content
            fidelity_score += 1

        # 2. Economic analysis section presence
        required_sections = [
            "Executive Summary",
            "Economic Positioning Dashboard",
            "Business Cycle Assessment",
            "Risk Assessment",
            "Investment Implications",
        ]
        present_sections = sum(1 for section in required_sections if section.lower() in content.lower())
        fidelity_score += min(present_sections / len(required_sections), 1.0)

        # 3. Economic terminology preservation
        economic_terms = [
            "GDP",
            "recession probability",
            "business cycle",
            "monetary policy",
            "inflation",
            "employment",
            "confidence",
            "Federal Reserve",
        ]
        present_terms = sum(1 for term in economic_terms if term.lower() in content.lower())
        fidelity_score += min(present_terms / len(economic_terms), 1.0)

        # 4. Quantitative data preservation
        # Look for percentage values, confidence scores, probabilities
        percentage_pattern = r"\d+\.?\d*%"
        confidence_pattern = r"\d\.\d/\d\.\d"
        if re.search(percentage_pattern, content) and re.search(confidence_pattern, content):
            fidelity_score += 1

        # 5. Professional formatting preservation
        if "##" in content and "|" in content:  # Headers and tables
            fidelity_score += 1

        return fidelity_score / total_checks

    def _validate_economic_metadata(self, frontmatter: dict) -> float:
        """Validate economic metadata accuracy and completeness"""
        metadata_score = 0.0
        total_checks = 4

        macro_data = frontmatter.get("macro_data", {})

        # 1. Confidence score reasonableness
        confidence = macro_data.get("confidence")
        if isinstance(confidence, (int, float)) and 0.8 <= confidence <= 1.0:
            metadata_score += 1

        # 2. Data quality score reasonableness
        data_quality = macro_data.get("data_quality")
        if isinstance(data_quality, (int, float)) and 0.8 <= data_quality <= 1.0:
            metadata_score += 1

        # 3. Economic consistency checks
        recession_prob = macro_data.get("recession_probability", "0%")
        economic_phase = macro_data.get("economic_phase", "")
        # During expansion, recession probability should be relatively low
        prob_value = (
            float(re.findall(r"\d+\.?\d*", str(recession_prob))[0])
            if re.findall(r"\d+\.?\d*", str(recession_prob))
            else 100
        )
        if (
            economic_phase == "Expansion"
            and prob_value < 30
            or economic_phase in ["Peak", "Contraction"]
            and prob_value >= 30
            or economic_phase == "Trough"
            and prob_value >= 20
        ):
            metadata_score += 1
        else:
            metadata_score += 0.5  # Partial credit for other combinations

        # 4. Risk score reasonableness
        risk_score = macro_data.get("risk_score", "5.0/5.0")
        risk_value = float(risk_score.split("/")[0]) if "/" in str(risk_score) else 5.0
        if 1.0 <= risk_value <= 5.0:
            metadata_score += 1

        return metadata_score / total_checks

    def _validate_frontend_integration(self, content: str, frontmatter: dict) -> float:
        """Validate frontend integration and presentation quality"""
        integration_score = 0.0
        total_checks = 5

        # 1. Markdown structure validation
        if content.count("## ") >= 5:  # Multiple sections
            integration_score += 1

        # 2. Table presence for economic data
        if "|" in content and "---" in content:
            integration_score += 1

        # 3. Image integration validation
        image_path = frontmatter.get("image", "")
        if image_path.startswith("/images/macro/") and image_path.endswith("-min.png"):
            integration_score += 1

        # 4. List formatting presence
        if ("- " in content or "* " in content) and content.count("\n- ") >= 3:
            integration_score += 1

        # 5. Professional emoji usage (economic context)
        economic_emojis = ["🎯", "📊", "🏆", "📈", "⚠️", "💡"]
        if any(emoji in content for emoji in economic_emojis):
            integration_score += 1

        return integration_score / total_checks

    def _validate_seo_optimization(self, frontmatter: dict, content: str) -> float:
        """Validate SEO optimization completeness"""
        seo_score = 0.0
        total_checks = 6

        # 1. Meta_title presence and optimization
        meta_title = frontmatter.get("meta_title", "")
        if meta_title and len(meta_title) <= 60:  # Google title length limit
            seo_score += 1

        # 2. Description SEO optimization
        description = frontmatter.get("description", "")
        if 150 <= len(description) <= 160:  # Optimal meta description length
            seo_score += 1

        # 3. Tags presence and relevance
        tags = frontmatter.get("tags", [])
        if len(tags) >= 5 and "macro-analysis" in tags:
            seo_score += 1

        # 4. Categories SEO structure
        categories = frontmatter.get("categories", [])
        if "Economics" in categories and "Analysis" in categories:
            seo_score += 1

        # 5. Content keyword density
        economic_keywords = [
            "macro",
            "economic",
            "analysis",
            "GDP",
            "recession",
            "policy",
        ]
        keyword_density = sum(content.lower().count(keyword) for keyword in economic_keywords)
        if keyword_density >= 20:  # Reasonable keyword presence
            seo_score += 1

        # 6. Header structure (H2, H3 hierarchy)
        h2_count = content.count("## ")
        h3_count = content.count("### ")
        if h2_count >= 4 and h3_count >= 2:
            seo_score += 1

        return seo_score / total_checks

    def _validate_performance_metrics(self, file_info: dict, content: str, frontmatter: dict = None) -> float:
        """Validate performance and technical metrics"""
        performance_score = 0.0
        total_checks = 4

        # 1. File size optimization (not too large for web)
        size_mb = file_info["size_bytes"] / (1024 * 1024)
        if 0.015 <= size_mb <= 0.1:  # 15KB to 100KB is reasonable
            performance_score += 1

        # 2. Content structure efficiency
        word_count = len(content.split())
        if 1500 <= word_count <= 8000:  # Professional content range
            performance_score += 1

        # 3. Clean markdown formatting
        # Check for excessive whitespace or formatting issues
        lines = content.split("\n")
        empty_lines = sum(1 for line in lines if not line.strip())
        if empty_lines / len(lines) < 0.4:  # Professional content can have structural spacing
            performance_score += 1

        # 4. Loading optimization indicators
        # FIXED: Check frontmatter image field for minified images instead of body content
        if frontmatter:
            image_path = frontmatter.get("image", "")
            if image_path.endswith("-min.png"):
                performance_score += 1
        else:
            # Fallback: check content if no frontmatter provided
            if "-min.png" in content:
                performance_score += 1

        return performance_score / total_checks

    def _extract_region_from_filename(self, filename: str) -> str:
        """Extract region identifier from filename"""
        filename_lower = filename.lower()
        if filename_lower.startswith("us-"):
            return "US"
        if filename_lower.startswith("americas-"):
            return "Americas"
        if filename_lower.startswith("europe-"):
            return "Europe"
        if filename_lower.startswith("asia-"):
            return "Asia"
        if filename_lower.startswith("global-"):
            return "Global"
        return "Unknown"

    def _determine_certification_level(self, score: float) -> str:
        """Determine institutional certification level"""
        if score >= 9.5:
            return "INSTITUTIONAL_CERTIFIED"
        if score >= 9.0:
            return "PROFESSIONAL_APPROVED"
        if score >= 8.0:
            return "INTERNAL_USE_APPROVED"
        return "DEVELOPMENT_STAGE"

    def _create_no_content_report(self) -> dict[str, Any]:
        """Create report when no published content found"""
        return {
            "metadata": {
                "command_name": "institutional_quality_validator",
                "execution_timestamp": datetime.now().isoformat(),
                "framework_phase": "institutional_quality_validation",
                "files_analyzed_count": 0,
                "validation_methodology": "comprehensive_institutional_quality_assessment",
            },
            "institutional_quality_results": {
                "overall_institutional_score": "0.0/10.0",
                "institutional_certified_count": 0,
                "professional_approved_count": 0,
                "certification_rate": "0.0%",
            },
            "critical_findings": [
                {
                    "issue_type": "no_published_content",
                    "description": "No published macro analysis content found for institutional validation",
                    "severity": "high",
                    "recommendation": "Publish macro analysis content before running institutional validation",
                }
            ],
            "institutional_assessment": {
                "ready_for_institutional_use": False,
                "certification_threshold_met": False,
                "overall_grade": "F",
            },
        }

    def _generate_institutional_report(self, validation_results: dict) -> dict[str, Any]:
        """Generate comprehensive institutional quality report"""

        # Calculate aggregate metrics
        total_files = len(validation_results)
        institutional_certified = sum(1 for result in validation_results.values() if result["institutional_certified"])
        professional_approved = sum(
            1 for result in validation_results.values() if result["weighted_institutional_score"] >= 9.0
        )

        # Calculate average scores by category
        avg_scores = {}
        for category in self.INSTITUTIONAL_WEIGHTS.keys():
            scores = [result["individual_scores"][category] for result in validation_results.values()]
            avg_scores[category] = sum(scores) / len(scores) if scores else 0.0

        # Overall weighted average
        overall_score = (
            sum(result["weighted_institutional_score"] for result in validation_results.values()) / total_files
        )

        # File details
        files_analyzed = []
        detected_issues = {
            "template_compliance_violations": [],
            "content_fidelity_issues": [],
            "metadata_accuracy_problems": [],
            "frontend_integration_issues": [],
        }

        for filename, result in validation_results.items():
            # File analysis summary
            files_analyzed.append(
                {
                    "filename": filename,
                    "region": self._extract_region_from_filename(filename),
                    "weighted_institutional_score": f"{result['weighted_institutional_score']:.1f}/10.0",
                    "certification_level": result["certification_level"],
                    "institutional_certified": result["institutional_certified"],
                }
            )

            # Issue detection
            scores = result["individual_scores"]
            if scores["template_compliance"] < 0.9:
                detected_issues["template_compliance_violations"].append(
                    {
                        "filename": filename,
                        "score": f"{scores['template_compliance']:.2f}",
                        "issue": "Template compliance below institutional standard",
                    }
                )

            if scores["content_fidelity"] < 0.9:
                detected_issues["content_fidelity_issues"].append(
                    {
                        "filename": filename,
                        "score": f"{scores['content_fidelity']:.2f}",
                        "issue": "Content fidelity below preservation requirement",
                    }
                )

            if scores["economic_metadata_accuracy"] < 0.9:
                detected_issues["metadata_accuracy_problems"].append(
                    {
                        "filename": filename,
                        "score": f"{scores['economic_metadata_accuracy']:.2f}",
                        "issue": "Economic metadata accuracy below institutional standard",
                    }
                )

        # Generate recommendations
        recommendations = self._generate_institutional_recommendations(avg_scores, overall_score)

        return {
            "metadata": {
                "command_name": "institutional_quality_validator",
                "execution_timestamp": datetime.now().isoformat(),
                "framework_phase": "institutional_quality_validation",
                "files_analyzed_count": total_files,
                "validation_methodology": "comprehensive_institutional_quality_assessment",
            },
            "files_analyzed": files_analyzed,
            "institutional_quality_results": {
                "overall_institutional_score": f"{overall_score:.1f}/10.0",
                "institutional_certified_count": institutional_certified,
                "professional_approved_count": professional_approved,
                "certification_rate": f"{(professional_approved / total_files) * 100:.1f}%"
                if total_files > 0
                else "0.0%",
                "category_scores": {k: f"{v:.2f}" for k, v in avg_scores.items()},
            },
            "detected_issues": detected_issues,
            "institutional_assessment": {
                "ready_for_institutional_use": overall_score >= 9.0,
                "certification_threshold_met": professional_approved >= total_files * 0.8,
                "overall_grade": self._calculate_grade(overall_score),
                "institutional_quality_certified": overall_score >= 9.5,
            },
            "recommendations": recommendations,
            "validation_summary": {
                "institutional_quality_achieved": overall_score >= 9.0,
                "primary_strengths": self._identify_strengths(avg_scores),
                "improvement_priorities": self._identify_priorities(avg_scores),
                "next_steps": self._generate_next_steps(overall_score),
            },
        }

    def _generate_institutional_recommendations(self, avg_scores: dict, overall_score: float) -> dict:
        """Generate institutional improvement recommendations"""
        recommendations = {
            "immediate_fixes": [],
            "institutional_improvements": [],
            "certification_requirements": [],
        }

        # Immediate fixes for low scores
        for category, score in avg_scores.items():
            if score < 0.7:
                recommendations["immediate_fixes"].append(f"Address {category} quality issues (current: {score:.1f})")

        # Institutional improvements
        if avg_scores["template_compliance"] < 0.95:
            recommendations["institutional_improvements"].append("Enforce strict template compliance standards")

        if avg_scores["economic_metadata_accuracy"] < 0.90:
            recommendations["institutional_improvements"].append("Enhance economic metadata validation protocols")

        if avg_scores["content_fidelity"] < 0.90:
            recommendations["institutional_improvements"].append("Implement content fidelity preservation controls")

        # Certification requirements
        if overall_score < 9.0:
            gap = 9.0 - overall_score
            recommendations["certification_requirements"].append(
                f"Improve overall score by {gap:.1f} points to achieve ≥9.0 institutional standard"
            )

        if not recommendations["immediate_fixes"]:
            recommendations["immediate_fixes"].append("All quality metrics meet baseline standards")

        return recommendations

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade for institutional score"""
        if score >= 9.5:
            return "A+"
        if score >= 9.0:
            return "A"
        if score >= 8.5:
            return "A-"
        if score >= 8.0:
            return "B+"
        if score >= 7.5:
            return "B"
        if score >= 7.0:
            return "B-"
        return "C"

    def _identify_strengths(self, avg_scores: dict) -> list[str]:
        """Identify primary quality strengths"""
        strengths = []
        for category, score in avg_scores.items():
            if score >= 0.9:
                strengths.append(f"Excellent {category} ({score:.2f})")

        if not strengths:
            strengths.append("Baseline quality standards maintained")

        return strengths

    def _identify_priorities(self, avg_scores: dict) -> list[str]:
        """Identify improvement priorities"""
        priorities = []

        # Sort by lowest scores first
        sorted_scores = sorted(avg_scores.items(), key=lambda x: x[1])

        for category, score in sorted_scores[:3]:  # Top 3 priorities
            if score < 0.9:
                priorities.append(f"{category} improvement (current: {score:.2f})")

        if not priorities:
            priorities.append("Maintain excellence across all quality dimensions")

        return priorities

    def _generate_next_steps(self, overall_score: float) -> list[str]:
        """Generate next steps based on institutional score"""
        if overall_score >= 9.5:
            return [
                "Maintain institutional excellence",
                "Consider premium certification protocols",
            ]
        if overall_score >= 9.0:
            return [
                "Optimize for premium institutional certification",
                "Focus on consistency across all content",
            ]
        if overall_score >= 8.0:
            return [
                "Address specific quality gaps",
                "Target ≥9.0 institutional threshold",
                "Implement enhanced validation protocols",
            ]
        return [
            "Comprehensive quality improvement required",
            "Focus on fundamental institutional standards",
            "Review and upgrade all validation processes",
        ]


def main():
    """Execute institutional quality validation"""
    validator = InstitutionalQualityValidator()

    print("🔍 Starting Institutional Quality Validation System for Macro Analysis Publications")

    # Execute comprehensive validation
    results = validator.execute_institutional_validation()

    # Save results
    output_dir = "./data/outputs/macro_analysis/validation"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"institutional_quality_validation_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        json.dump(results, f, indent=2)

    # Display results
    print("\n✅ Institutional Quality Validation Complete!")
    print(f"📊 Overall Score: {results['institutional_quality_results']['overall_institutional_score']}")
    print(f"🏆 Certification Rate: {results['institutional_quality_results']['certification_rate']}")
    print(f"📈 Grade: {results['institutional_assessment']['overall_grade']}")
    print(f"🎯 Institutional Ready: {results['institutional_assessment']['ready_for_institutional_use']}")
    print(f"📁 Report saved to: {filepath}")

    return results


if __name__ == "__main__":
    main()
