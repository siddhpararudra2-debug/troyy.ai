#!/usr/bin/env python3
"""Verify Sprint 17 - Engineering Governance, Configuration Management, etc."""
import sys

print("=== Sprint 17 Verification ===")
print()

all_passed = True

# Module 1: Configuration Management
try:
    print("1. Testing Configuration Management...")
    from configuration import (
        BaselineManager,
        ReleaseManager,
        RevisionController,
        ConfigurationAuditor,
        ChangeManager,
    )
    print("   - OK: All imports passed!")

    manager = BaselineManager()
    baseline = manager.create_baseline(
        project_id="proj-test",
        name="Test Baseline",
        description="Test",
    )
    print(f"   - OK: Created baseline {baseline['id']}")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    import traceback
    traceback.print_exc()
    all_passed = False
    print()

# Module 2: Change Management
try:
    print("2. Testing Change Management...")
    from change_management import (
        ChangeRequestManager,
        ImpactAnalyzer,
        DependencyTracker,
        ChangeApprover,
    )
    print("   - OK: All imports passed!")

    cr = ChangeRequestManager()
    request = cr.create_request(
        project_id="proj-test",
        title="Test Change Request"
    )
    print(f"   - OK: Created change request {request['id']}")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    print()

# Module 3: Workflow
try:
    print("3. Testing Workflow Engine...")
    from workflow import (
        WorkflowEngine,
        WorkflowBuilder,
        WorkflowTemplates,
        StateMachine,
    )
    print("   - OK: All imports passed!")

    workflow = WorkflowEngine().create_workflow(
        project_id="proj-test",
        name="Test Workflow",
        definition=WorkflowBuilder.build_default_engineering_workflow(),
    )
    print(f"   - OK: Created workflow {workflow['id']}")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    print()

# Module 4: Reviews
try:
    print("4. Testing Review & Approval...")
    from reviews import (
        ReviewManager,
        ApprovalManager,
        SignoffEngine,
        ValidationGate,
    )
    print("   - OK: All imports passed!")

    rm = ReviewManager()
    review = rm.create_review(
        project_id="proj-test",
        artifact_id="art-test",
        title="Test Review"
    )
    print(f"   - OK: Created review {review['id']}")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    print()

# Module 5: Knowledge
try:
    print("5. Testing Personal Knowledge Base...")
    from personal_knowledge import (
        EngineeringJournal,
        LessonsLearnedManager,
        DesignPatternsManager,
        BestPracticesManager,
        FailureLibrary,
    )
    print("   - OK: All imports passed!")

    journal = EngineeringJournal()
    entry = journal.add_entry("proj-test", "Test journal entry!")
    print(f"   - OK: Added journal entry {entry['id']}")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    print()

# Module 9: Backup & Recovery
try:
    print("9. Testing Backup & Recovery...")
    from backup import (
        PostgresBackup,
        StorageBackup,
        RecoveryManager,
        SnapshotManager,
    )
    print("   - OK: All imports passed!")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    print()

# API Routes
try:
    print("10. Testing API Routes...")
    from api.routes_sprint17 import router
    print("   - OK: Routes imported!")
    print()
except Exception as e:
    print(f"   ERROR: {e}")
    all_passed = False
    print()

print("=== Summary ===")
if all_passed:
    print("[PASSED] ALL SPRINT 17 TESTS PASSED!")
    sys.exit(0)
else:
    print("[FAILED] Some Sprint 17 tests failed!")
    sys.exit(1)
