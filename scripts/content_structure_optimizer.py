#!/usr/bin/env python3
"""
Content Structure Optimizer
Optimize markdown structure to improve performance metrics while maintaining readability
"""

import glob
import os


class ContentStructureOptimizer:
    """Optimize content structure for performance metrics"""

    def __init__(self, blog_directory: str = "./frontend/src/content/blog/"):
        self.blog_directory = blog_directory

    def optimize_all_files(self):
        """Optimize all macro analysis files"""
        print("🔧 Optimizing content structure for performance metrics...")

        pattern = os.path.join(self.blog_directory, "*macro*analysis*.md")
        published_files = glob.glob(pattern)

        results = {"files_processed": 0, "files_optimized": 0, "empty_lines_removed": 0}

        for file_path in published_files:
            filename = os.path.basename(file_path)
            print(f"📝 Optimizing: {filename}")

            empty_lines_removed = self._optimize_file(file_path)
            results["files_processed"] += 1

            if empty_lines_removed > 0:
                results["files_optimized"] += 1
                results["empty_lines_removed"] += empty_lines_removed
                print(f"  ✓ Removed {empty_lines_removed} excessive empty lines")
            else:
                print("  ℹ️  Already optimized")

        return results

    def _optimize_file(self, file_path: str) -> int:
        """Optimize a single file's content structure"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        original_lines = content.split("\n")
        optimized_lines = []
        consecutive_empty = 0
        empty_lines_removed = 0

        for line in original_lines:
            # If line is empty
            if not line.strip():
                consecutive_empty += 1

                # Allow maximum 2 consecutive empty lines
                if consecutive_empty <= 2:
                    optimized_lines.append(line)
                else:
                    empty_lines_removed += 1
            else:
                consecutive_empty = 0
                optimized_lines.append(line)

        # Remove trailing empty lines (keep max 1)
        while len(optimized_lines) > 1 and not optimized_lines[-1].strip():
            optimized_lines.pop()
            empty_lines_removed += 1

        # Ensure file ends with single newline
        if optimized_lines and optimized_lines[-1].strip():
            optimized_lines.append("")

        # Save if optimized
        if empty_lines_removed > 0:
            optimized_content = "\n".join(optimized_lines)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(optimized_content)

        return empty_lines_removed

    def analyze_content_metrics(self):
        """Analyze current content metrics"""
        print("📊 Analyzing content structure metrics...")

        pattern = os.path.join(self.blog_directory, "*macro*analysis*.md")
        published_files = glob.glob(pattern)

        metrics = []

        for file_path in published_files:
            filename = os.path.basename(file_path)

            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Split into frontmatter and body
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    body_content = parts[2].strip()
                else:
                    body_content = content
            else:
                body_content = content

            lines = body_content.split("\n")
            empty_lines = sum(1 for line in lines if not line.strip())
            total_lines = len(lines)
            empty_ratio = empty_lines / total_lines if total_lines > 0 else 0

            word_count = len(body_content.split())
            file_size_kb = len(content) / 1024

            metrics.append(
                {
                    "filename": filename,
                    "empty_ratio": empty_ratio,
                    "empty_lines": empty_lines,
                    "total_lines": total_lines,
                    "word_count": word_count,
                    "file_size_kb": file_size_kb,
                    "performance_score": self._calculate_performance_score(
                        empty_ratio, word_count, file_size_kb, body_content
                    ),
                }
            )

        return metrics

    def _calculate_performance_score(
        self, empty_ratio: float, word_count: int, file_size_kb: float, content: str
    ) -> float:
        """Calculate performance score like the validator"""
        score = 0.0

        # File size check (15KB-100KB)
        if 15 <= file_size_kb <= 100:
            score += 1

        # Word count check (2000-8000 words)
        if 2000 <= word_count <= 8000:
            score += 1

        # Empty lines ratio check (<40%)
        if empty_ratio < 0.4:
            score += 1

        # Minified images check
        if "-min.png" in content:
            score += 1

        return score / 4


def main():
    """Execute content structure optimization"""
    optimizer = ContentStructureOptimizer()

    print("📊 Content Structure Performance Analysis")

    # Analyze current metrics
    metrics = optimizer.analyze_content_metrics()

    print("\n📈 Current Performance Metrics:")
    for metric in metrics:
        print(
            f"{metric['filename']:35} | "
            f"Empty Ratio: {metric['empty_ratio']:.1%} | "
            f"Words: {metric['word_count']:5} | "
            f"Size: {metric['file_size_kb']:.1f}KB | "
            f"Perf Score: {metric['performance_score']:.2f}/1.0"
        )

    # Optimize structure
    print("\n🔧 Optimizing Content Structure...")
    results = optimizer.optimize_all_files()

    # Analyze after optimization
    print("\n📊 Re-analyzing after optimization...")
    metrics_after = optimizer.analyze_content_metrics()

    print("\n📈 Optimized Performance Metrics:")
    for metric in metrics_after:
        print(
            f"{metric['filename']:35} | "
            f"Empty Ratio: {metric['empty_ratio']:.1%} | "
            f"Words: {metric['word_count']:5} | "
            f"Size: {metric['file_size_kb']:.1f}KB | "
            f"Perf Score: {metric['performance_score']:.2f}/1.0"
        )

    print("\n✅ Content Structure Optimization Complete!")
    print(f"📊 Files Processed: {results['files_processed']}")
    print(f"🔧 Files Optimized: {results['files_optimized']}")
    print(f"📉 Empty Lines Removed: {results['empty_lines_removed']}")

    # Calculate average performance improvement
    avg_before = sum(m["performance_score"] for m in metrics) / len(metrics)
    avg_after = sum(m["performance_score"] for m in metrics_after) / len(metrics_after)
    improvement = (avg_after - avg_before) * 100

    print(f"📈 Average Performance Score: {avg_before:.3f} → {avg_after:.3f} (+{improvement:.1f}%)")

    return results


if __name__ == "__main__":
    main()
