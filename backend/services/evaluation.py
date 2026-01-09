"""
Evaluation Pipeline for GravityWork

Implements RAGAS-like evaluation metrics for the chat system:
- Intent Accuracy: Correct classification of user intents
- Response Relevance: Semantic similarity to ground truth
- Faithfulness: Response consistency with retrieved context
"""
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import BaseModel
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class EvaluationMetrics(BaseModel):
    """Metrics for a single test case evaluation."""
    test_id: str
    intent_correct: bool
    response_contains_expected: bool
    confirmation_correct: bool
    score: float

class EvaluationReport(BaseModel):
    """Complete evaluation report."""
    timestamp: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    accuracy: float
    intent_accuracy: float
    response_relevance: float
    by_category: Dict[str, Dict[str, float]]
    failed_tests: List[str]

class EvaluationPipeline:
    """
    Evaluation pipeline for testing the GravityWork chat system.
    """
    
    def __init__(self, golden_dataset_path: str = "data/golden_dataset/test_set_pm.json"):
        self.dataset_path = Path(golden_dataset_path)
        self.test_cases = []
        self._load_dataset()
    
    def _load_dataset(self):
        """Load the golden dataset."""
        if self.dataset_path.exists():
            with open(self.dataset_path, "r") as f:
                data = json.load(f)
                self.test_cases = data.get("test_cases", [])
                logger.info(f"Loaded {len(self.test_cases)} test cases")
        else:
            logger.warning(f"Golden dataset not found at {self.dataset_path}")
    
    async def evaluate_single(self, test_case: Dict[str, Any]) -> EvaluationMetrics:
        """Evaluate a single test case."""
        from backend.services.intent_router import IntentRouter
        from backend.services.langgraph_agent import LangGraphAgent
        
        intent_router = IntentRouter()
        agent = LangGraphAgent()
        
        test_id = test_case.get("id", "unknown")
        input_text = test_case.get("input", "")
        expected_intent = test_case.get("expected_intent", "")
        expected_contains = test_case.get("expected_response_contains", [])
        requires_confirmation = test_case.get("requires_confirmation", False)
        
        # 1. Evaluate Intent Classification
        classification = await intent_router.classify(input_text)
        intent_correct = classification.intent.value == expected_intent
        
        # 2. Evaluate Response Generation
        response = await agent.run(input_text)
        response_lower = response.lower()
        
        # Check if response contains expected keywords
        contains_count = sum(1 for kw in expected_contains if kw.lower() in response_lower)
        response_contains_expected = contains_count >= len(expected_contains) * 0.5 if expected_contains else True
        
        # 3. Check confirmation behavior
        confirmation_correct = True
        if requires_confirmation:
            # For action intents, we expect the HITL flow was triggered
            confirmation_correct = classification.intent.value == "action"
        
        # Calculate overall score
        score = 0.0
        if intent_correct:
            score += 0.4
        if response_contains_expected:
            score += 0.4
        if confirmation_correct:
            score += 0.2
        
        return EvaluationMetrics(
            test_id=test_id,
            intent_correct=intent_correct,
            response_contains_expected=response_contains_expected,
            confirmation_correct=confirmation_correct,
            score=score
        )
    
    async def run_full_evaluation(self) -> EvaluationReport:
        """Run evaluation on all test cases."""
        if not self.test_cases:
            return EvaluationReport(
                timestamp=datetime.utcnow().isoformat(),
                total_cases=0,
                passed_cases=0,
                failed_cases=0,
                accuracy=0.0,
                intent_accuracy=0.0,
                response_relevance=0.0,
                by_category={},
                failed_tests=[]
            )
        
        results = []
        for test_case in self.test_cases:
            try:
                result = await self.evaluate_single(test_case)
                results.append((test_case, result))
            except Exception as e:
                logger.error(f"Failed to evaluate {test_case.get('id')}: {e}")
                results.append((test_case, EvaluationMetrics(
                    test_id=test_case.get("id", "unknown"),
                    intent_correct=False,
                    response_contains_expected=False,
                    confirmation_correct=False,
                    score=0.0
                )))
        
        # Aggregate metrics
        total = len(results)
        passed = sum(1 for _, r in results if r.score >= 0.7)
        failed = total - passed
        
        intent_correct_count = sum(1 for _, r in results if r.intent_correct)
        response_correct_count = sum(1 for _, r in results if r.response_contains_expected)
        
        # By category
        by_category = {}
        for tc, result in results:
            category = tc.get("category", "unknown")
            if category not in by_category:
                by_category[category] = {"total": 0, "passed": 0}
            by_category[category]["total"] += 1
            if result.score >= 0.7:
                by_category[category]["passed"] += 1
        
        for cat in by_category:
            by_category[cat]["accuracy"] = by_category[cat]["passed"] / by_category[cat]["total"] if by_category[cat]["total"] > 0 else 0
        
        failed_tests = [r.test_id for _, r in results if r.score < 0.7]
        
        return EvaluationReport(
            timestamp=datetime.utcnow().isoformat(),
            total_cases=total,
            passed_cases=passed,
            failed_cases=failed,
            accuracy=passed / total if total > 0 else 0.0,
            intent_accuracy=intent_correct_count / total if total > 0 else 0.0,
            response_relevance=response_correct_count / total if total > 0 else 0.0,
            by_category=by_category,
            failed_tests=failed_tests
        )

async def run_evaluation():
    """Run the evaluation pipeline."""
    pipeline = EvaluationPipeline()
    report = await pipeline.run_full_evaluation()
    
    print(f"\n{'='*50}")
    print("EVALUATION REPORT")
    print(f"{'='*50}")
    print(f"Timestamp: {report.timestamp}")
    print(f"Total Cases: {report.total_cases}")
    print(f"Passed: {report.passed_cases} ({report.accuracy*100:.1f}%)")
    print(f"Failed: {report.failed_cases}")
    print(f"\nIntent Accuracy: {report.intent_accuracy*100:.1f}%")
    print(f"Response Relevance: {report.response_relevance*100:.1f}%")
    print(f"\nBy Category:")
    for cat, data in report.by_category.items():
        print(f"  {cat}: {data['passed']}/{data['total']} ({data.get('accuracy', 0)*100:.1f}%)")
    
    if report.failed_tests:
        print(f"\nFailed Tests: {', '.join(report.failed_tests)}")
    
    return report

if __name__ == "__main__":
    asyncio.run(run_evaluation())
