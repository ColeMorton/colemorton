# Development Standards Guide: Python & TypeScript Excellence

**Version**: 2.0 | **Last Updated**: 2025-08-12 | **Status**: Mandatory
**Authority**: Documentation Owner | **Audience**: All Developers

## Table of Contents

1. [Overview & Philosophy](#overview--philosophy)
2. [Python Type Annotation Standards](#python-type-annotation-standards)
3. [Code Quality Standards](#code-quality-standards)
4. [Dependency Management](#dependency-management)
5. [Testing & Validation](#testing--validation)
6. [Quality Assurance Pipeline](#quality-assurance-pipeline)
7. [Common Anti-Patterns to Avoid](#common-anti-patterns-to-avoid)

---

## Overview & Philosophy

### Development Principles

**Core Standards:**
- **DRY (Don't Repeat Yourself)**: No code duplication across modules
- **SOLID Design**: Well-structured, maintainable object-oriented design
- **KISS (Keep It Simple, Stupid)**: Elegant solutions over complex implementations
- **YAGNI (You Aren't Gonna Need It)**: Implement only required functionality
- **Fail-Fast**: Meaningful exceptions with context over silent failures

### Quality Targets

**Institutional-Grade Standards:**
- **Type Coverage**: 95% across Python and TypeScript codebases
- **Test Coverage**: 85% minimum with focus on critical paths
- **Security Scan**: 100% passing (zero high-severity vulnerabilities)
- **Build Performance**: <2 minutes with optimized caching
- **Code Review**: 100% of changes reviewed before merge

---

## Python Type Annotation Standards

### Core Type Annotation Patterns

#### 1. Basic Type Annotations
```python
# Variables with explicit types
name: str = "AAPL"
price: float = 150.25
count: int = 100
is_active: bool = True

# Collections with type parameters
trades: List[TradeData] = []
metrics: Dict[str, float] = {}
symbols: Set[str] = {"AAPL", "GOOGL", "MSFT"}
```

#### 2. Function Signatures
```python
def calculate_returns(
    prices: List[float],
    weights: Optional[List[float]] = None
) -> List[float]:
    """Always annotate parameters and return types."""
    if weights is None:
        weights = [1.0] * len(prices)
    return [p * w for p, w in zip(prices, weights)]
```

#### 3. Numpy Array Types
```python
import numpy as np
import numpy.typing as npt

# Preferred: Use numpy.typing for array annotations
def process_data(values: List[float]) -> npt.NDArray[np.float64]:
    """Convert lists to numpy arrays with proper typing."""
    return np.array(values)

# Type-safe array operations
def safe_cumsum(data: Union[List[float], npt.NDArray]) -> npt.NDArray[np.float64]:
    """Handle both lists and arrays safely."""
    return np.cumsum(np.asarray(data))
```

#### 4. Dataclass Usage
```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class TradeData:
    """Strongly typed trade data structure."""
    symbol: str
    price: float
    quantity: int
    timestamp: datetime
    fees: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate data integrity after initialization."""
        if self.price <= 0:
            raise ValueError(f"Invalid price: {self.price}")
        if self.quantity == 0:
            raise ValueError("Quantity cannot be zero")
```

#### 5. Protocol Definitions
```python
from typing import Protocol

class DataProvider(Protocol):
    """Define interface for data providers."""

    def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Retrieve stock data for given symbol."""
        ...

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate data structure and content."""
        ...
```

### Advanced Type Patterns

#### Union Types and Type Guards
```python
from typing import Union, TypeGuard

def is_trade_data(value: Union[TradeData, Dict[str, Any]]) -> TypeGuard[TradeData]:
    """Type guard for trade data validation."""
    return isinstance(value, TradeData)

def process_trade(data: Union[TradeData, Dict[str, Any]]) -> TradeData:
    """Process trade data with type safety."""
    if is_trade_data(data):
        return data  # TypeGuard ensures this is TradeData
    else:
        return TradeData(**data)  # Convert dict to TradeData
```

#### Generic Types
```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class DataCache(Generic[T]):
    """Generic cache implementation with type safety."""

    def __init__(self) -> None:
        self._data: Dict[str, T] = {}

    def get(self, key: str) -> Optional[T]:
        """Retrieve cached item with correct type."""
        return self._data.get(key)

    def set(self, key: str, value: T) -> None:
        """Store item in cache."""
        self._data[key] = value

# Usage with specific types
trade_cache: DataCache[TradeData] = DataCache()
price_cache: DataCache[float] = DataCache()
```

### MyPy Configuration

**mypy.ini Configuration:**
```ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

---

## Code Quality Standards

### Error Handling Excellence

**Custom Exception Hierarchy:**
```python
class ColemortonError(Exception):
    """Base exception for Colemorton-specific errors."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.context = context or {}

class ValidationError(ColemortonError):
    """Schema validation errors with detailed feedback."""
    pass

class DataProviderError(ColemortonError):
    """Data provider service errors."""
    pass

class AnalysisError(ColemortonError):
    """Analysis computation errors."""
    pass
```

**Fail-Fast Implementation:**
```python
def validate_stock_symbol(symbol: str) -> str:
    """Validate stock symbol with immediate failure."""
    if not symbol:
        raise ValidationError("Stock symbol cannot be empty")

    if not symbol.isalpha():
        raise ValidationError(
            f"Invalid symbol format: {symbol}",
            context={"symbol": symbol, "validation": "alpha_only"}
        )

    if len(symbol) > 5:
        raise ValidationError(
            f"Symbol too long: {symbol} (max 5 characters)",
            context={"symbol": symbol, "length": len(symbol)}
        )

    return symbol.upper()
```

### Performance Optimization Patterns

**Multi-Level Caching Strategy:**
```python
from functools import lru_cache
from typing import Optional
import time

class DataCache:
    """Multi-level caching with TTL management."""

    def __init__(self, ttl: int = 3600):
        self._cache: Dict[str, Tuple[Any, float]] = {}
        self._ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        """Retrieve with TTL validation."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """Store with timestamp."""
        self._cache[key] = (value, time.time())

# Session-based caching for expensive computations
@lru_cache(maxsize=128)
def expensive_calculation(symbol: str, period: str) -> float:
    """Cache expensive calculations within session."""
    # Expensive computation here
    return 0.0
```

### Logging Standards

**Structured Logging:**
```python
import structlog
from typing import Any, Dict

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def process_trade_data(symbol: str) -> Dict[str, Any]:
    """Example with structured logging."""
    logger.info(
        "Processing trade data",
        symbol=symbol,
        operation="trade_processing",
        stage="start"
    )

    try:
        # Processing logic here
        result = {"symbol": symbol, "status": "processed"}

        logger.info(
            "Trade processing completed",
            symbol=symbol,
            operation="trade_processing",
            stage="complete",
            result_count=len(result)
        )

        return result

    except Exception as e:
        logger.error(
            "Trade processing failed",
            symbol=symbol,
            operation="trade_processing",
            stage="error",
            error=str(e),
            exc_info=True
        )
        raise
```

---

## Dependency Management

### Python Dependencies Strategy

**Security and Stability:**
- **requirements.txt**: Production dependencies with version bounds
- **requirements-dev.txt**: Development and testing dependencies
- **Upper bounds**: Prevent major version updates that could break compatibility
- **Security scanning**: Safety and Bandit for vulnerability detection

**Production Dependencies Structure:**
```text
# requirements.txt
pandas>=2.0.0,<3.0.0       # Data manipulation
numpy>=1.24.0,<2.0.0       # Numerical computing
scikit-learn>=1.3.0,<2.0.0 # Machine learning
plotly>=5.15.0,<6.0.0      # Visualization
sqlalchemy>=2.0.0,<3.0.0   # Database ORM
structlog>=23.0.0,<24.0.0  # Structured logging
pyyaml>=6.0,<7.0           # Configuration
requests>=2.28.0,<3.0.0    # HTTP client
```

**Development Dependencies:**
```text
# requirements-dev.txt
pytest>=7.0.0,<8.0.0       # Testing framework
pytest-cov>=4.0.0,<5.0.0   # Coverage reporting
mypy>=1.0.0,<2.0.0         # Type checking
black>=23.0.0,<24.0.0      # Code formatting
isort>=5.10.0,<6.0.0       # Import sorting
flake8>=6.0.0,<7.0.0       # Linting
bandit>=1.7.0,<2.0.0       # Security scanning
safety>=2.0.0,<3.0.0       # Vulnerability scanning
```

### Frontend Dependencies

**Modern Stack Management:**
```json
{
  "dependencies": {
    "astro": "^5.7.8",
    "react": "^19.1.0",
    "tailwindcss": "^4.1.4",
    "typescript": "^5.8.3"
  },
  "devDependencies": {
    "eslint": "^9.0.0",
    "prettier": "^3.0.0",
    "vitest": "^3.2.4",
    "@typescript-eslint/parser": "^8.0.0"
  }
}
```

### Security Procedures

**Python Security Scanning:**
```bash
# Run safety check for known vulnerabilities
python3 -m safety scan

# Run bandit for security issues in code
python3 -m bandit -r scripts/ -f json

# Check for outdated packages
pip list --outdated
```

**Frontend Security Scanning:**
```bash
# Run yarn audit for vulnerabilities
yarn audit

# Check for high-severity issues only
yarn audit --level high

# Update vulnerable packages
yarn upgrade [package-name]
```

### Automated Updates

**Dependabot Configuration (`.github/dependabot.yml`):**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    reviewers:
      - "development-team"

  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

---

## Testing & Validation

### Testing Strategy

**Test Categories:**
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow validation
- **Performance Tests**: Load and scalability testing

**Pytest Configuration:**
```python
# conftest.py
import pytest
from typing import Generator
from unittest.mock import Mock

@pytest.fixture
def mock_data_provider() -> Generator[Mock, None, None]:
    """Mock data provider for testing."""
    mock = Mock()
    mock.get_stock_data.return_value = {
        "symbol": "AAPL",
        "price": 150.0,
        "volume": 1000000
    }
    yield mock

@pytest.fixture
def sample_trade_data() -> TradeData:
    """Sample trade data for testing."""
    return TradeData(
        symbol="AAPL",
        price=150.0,
        quantity=100,
        timestamp=datetime.now()
    )

# Test example
def test_trade_validation(sample_trade_data: TradeData) -> None:
    """Test trade data validation."""
    assert sample_trade_data.symbol == "AAPL"
    assert sample_trade_data.price > 0
    assert sample_trade_data.quantity > 0
```

### Coverage Requirements

**Coverage Configuration:**
```ini
# .coveragerc
[run]
source = scripts/
omit =
    */tests/*
    */venv/*
    */node_modules/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

---

## Quality Assurance Pipeline

### Pre-Commit Pipeline (12 Hooks)

**Python Quality Gates:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black
        args: [--line-length=88]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, scripts/]
```

**Frontend Quality Gates:**
```yaml
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0
    hooks:
      - id: prettier
        files: \.(js|jsx|ts|tsx|css|md|json)$

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.0.0
    hooks:
      - id: eslint
        files: \.(js|jsx|ts|tsx)$
```

### Continuous Integration

**Quality Validation Workflow:**
```bash
# Complete quality check
make format              # Format with black/isort
make lint               # Lint with flake8
make test               # Run pytest with coverage
make type-check         # Run mypy validation
make security-scan      # Run bandit security scan
```

---

## Common Anti-Patterns to Avoid

### Code Quality Anti-Patterns

**❌ Technical Debt:**
- Accumulated shortcuts or legacy logic
- Historical artifacts and leftover reasoning
- Unused abstractions and dead code

**❌ Code Smell:**
- Narrative bloat in comments and documentation
- Poor design symptoms
- Excessive complexity without justification

**❌ Leaky Abstraction:**
- Internal details exposed breaking encapsulation
- Implementation-specific logic in interfaces
- Tight coupling between components

**❌ Narrative Bloat:**
- Excessive or outdated commentary
- Code that explains obvious functionality
- Historical reasoning in current implementation

**❌ Historical Artifacts:**
- Obsolete logic left behind after refactors
- Confusing naming from previous implementations
- Legacy patterns inconsistent with current standards

**❌ Leaky Reasoning:**
- Implementation reveals unnecessary rationale
- Violation of information hiding principles
- Exposing decision-making processes in interfaces

### Enforcement Standards

**Zero Tolerance Policy:**
- **No backwards compatibility** unless explicitly required
- **No rollback mechanisms** unless specifically requested
- **No narrative bloat** in code comments
- **No leaky reasoning** in public interfaces
- **Fail-fast methodology** preferred over fallback functionality

---

## Implementation Checklist

### Developer Onboarding
- [ ] Install pre-commit hooks
- [ ] Configure IDE with type checking
- [ ] Set up testing environment
- [ ] Review code quality standards
- [ ] Complete typing guidelines training

### Code Review Checklist
- [ ] Type annotations on all functions
- [ ] Error handling with custom exceptions
- [ ] Tests covering critical paths
- [ ] Documentation for public interfaces
- [ ] Security considerations addressed

### Quality Gates
- [ ] 95% type coverage achieved
- [ ] 85% test coverage maintained
- [ ] Zero high-severity security issues
- [ ] All quality checks passing
- [ ] Performance requirements met

---

**Development Authority**: Institutional-Grade Code Quality Excellence
**Implementation Confidence**: 9.6/10.0
**Quality Standards**: Zero-tolerance for anti-patterns
**Status**: Mandatory for all development activities
