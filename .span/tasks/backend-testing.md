# span Task: Implement Backend Unit Tests (ID: backend-testing)

## Task Description
Write and update unit tests for the backend data fetching functionality in tests/backend.test.py. Reference patterns in backend/CLAUDE.md and ensure that the tests validate correct data retrieval from the World Bank API and proper error handling.

## Component & Technical Context
**Component:** testing
**Estimated Complexity:** 100 Claude Code conversation turns
**Current Retry:** 0 (if > 0, review previous failure context)

## Dependencies & Prerequisites
**Required tasks:** backend-data-fetch

⚠️ Ensure these tasks are completed before
     proceeding. Check their PRs and integration status.

## Environment Variables
```
ESTIMATED_TURNS: 8
DELIVERABLES: tests/backend.test.py (enhanced with tests for the data fetching functionality)
TASK_COMPONENT: testing
```

## Deliverables & Success Criteria
This task must produce:
- **Primary Implementation:** Concrete, working code files that meet ALL requirements
- **Testing:** Comprehensive tests that PASS and validate functionality  
- **Documentation:** Updated docs reflecting new features/changes
- **Git Workflow:** Feature branch with clean, descriptive commits
- **Quality Standards:** Code builds, tests pass, no linting errors
- **Integration:** No breaking changes to existing functionality

## Pull Request Requirements
🚨 **MANDATORY: Submit PR only when ALL success criteria are met**

**PR Submission Checklist:**
- ✅ All deliverables above are complete
- ✅ All tests pass (`npm test` shows 0 failures)
- ✅ Code builds without errors
- ✅ Implementation matches task description exactly
- ✅ Feature branch is up to date with main
- ✅ Commits are clean and descriptive

**If you cannot meet ALL criteria:**
- Document what's blocking completion
- Create an issue describing the blockers instead of a PR
- DO NOT submit incomplete or failing PRs

## Claude Code Execution Guidelines

### Turn Management (Max: 100 turns)
1. **Planning Phase** (1-2 turns): Understand requirements, explore codebase
2. **Implementation Phase** (60-70% of turns): Core development work
3. **Testing Phase** (20-30% of turns): Validation and edge cases  
4. **Finalization** (1-2 turns): Documentation, PR creation

### Required Actions - COMPLETE IN ORDER
1. [ ] Read and follow project conventions in `/CLAUDE.md`
2. [ ] Create a feature branch: `git checkout -b feature/your-task-name`
3. [ ] Implement ALL requirements specified in task description
4. [ ] Run tests and ensure they PASS: `npm test` / `cargo test` / `pytest`
5. [ ] Verify implementation meets ALL deliverables listed above
6. [ ] Commit changes with descriptive messages
7. [ ] Push branch: `git push -u origin feature/your-task-name`
8. [ ] **ONLY IF ALL TESTS PASS AND REQUIREMENTS MET:** Create PR using `gh pr create`

**⚠️ PR CREATION CRITERIA:**
- ✅ All tests must pass
- ✅ All deliverables must be complete
- ✅ Code must build without errors
- ✅ Implementation must match task requirements

**❌ DO NOT CREATE PR IF:**
- Tests are failing
- Implementation is incomplete
- Build errors exist
- Requirements are not fully met

If unable to complete successfully, document blockers instead of creating PR.

### Error Handling & Quality
- Handle edge cases and error conditions explicitly
- Follow security best practices (input validation, no hardcoded secrets)
- Use existing patterns and utilities in the codebase
- Optimize for readability and maintainability

## span Orchestration Context
- **Project Repository:** gdp-fertility-viz
- **Orchestration System:** This task is part of span's AI-coordinated development
- **Progress Tracking:** Completion will be tracked via GitHub issues automatically
- **Dependency Chain:** Completing this task may trigger dependent tasks
- **Failure Recovery:** Failures create investigation issues for human review

## Implementation Strategy
Based on the component type `testing`, consider:

- Write comprehensive test suites (unit, integration, e2e)
- Set up test automation and coverage reporting
- Create test data and mocking strategies
- Implement performance and security testing
- Document testing procedures and standards

## Final Notes
- **Time Budget:** Complete within 100 conversation turns maximum
- **Focus:** Incremental progress with each turn producing measurable results
- **Communication:** Clear commit messages and PR descriptions for human reviewers
- **Integration:** Coordinate with existing codebase patterns and dependencies

Ready to begin implementation. Start by exploring the codebase to understand the current state and integration points.