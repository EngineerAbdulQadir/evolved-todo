"""
Multi-Tenant Query Performance Analysis

Script to run EXPLAIN ANALYZE on key multi-tenant queries to verify:
1. Indexes are being used properly
2. Queries execute in <100ms (target)
3. Organization_id filtering is efficient

Task: T147 [P] [US6] - Run EXPLAIN ANALYZE on all multi-tenant queries
References:
- specs/005-multi-tenant-collab/spec.md User Story 6
- Constitution v5.0.0 Principle XX: Multi-Tenant Data Isolation
- Database Performance Requirements: All queries <100ms
"""

import asyncio
from datetime import datetime, UTC
from uuid import uuid4

from sqlalchemy import text
from sqlmodel import select

from app.core.database import engine
from app.models import Organization, Team, Project, Task, User


async def explain_analyze_query(query_name: str, sql_query: str) -> dict:
    """
    Run EXPLAIN ANALYZE on a query and return results.

    Args:
        query_name: Human-readable query name
        sql_query: SQL query to analyze

    Returns:
        Dict with query plan and execution time
    """
    print(f"\n{'='*80}")
    print(f"Analyzing: {query_name}")
    print(f"{'='*80}")

    async with engine.begin() as conn:
        # Run EXPLAIN ANALYZE
        explain_query = f"EXPLAIN ANALYZE {sql_query}"
        result = await conn.execute(text(explain_query))

        plan_lines = [row[0] for row in result]

        # Print query plan
        print("\nQuery Plan:")
        print("-" * 80)
        for line in plan_lines:
            print(line)

        # Extract execution time (last line usually contains "Execution Time")
        execution_time = None
        for line in plan_lines:
            if "Execution Time" in line or "Planning Time" in line:
                print(f"\n{line}")
            if "Execution Time" in line:
                # Extract time value
                try:
                    time_str = line.split(":")[1].strip().split()[0]
                    execution_time = float(time_str)
                except:
                    pass

        return {
            "query_name": query_name,
            "plan": plan_lines,
            "execution_time_ms": execution_time,
        }


async def analyze_multi_tenant_queries():
    """
    Analyze all key multi-tenant queries for performance.

    Verifies:
    1. Index usage on organization_id, team_id, project_id
    2. Index usage on deleted_at IS NULL filters
    3. Composite index usage for multi-column filters
    4. Query execution time <100ms
    """
    print("\n" + "="*80)
    print("Multi-Tenant Query Performance Analysis")
    print("Target: All queries <100ms with proper index usage")
    print("="*80)

    # Sample organization_id for testing (use a UUID that might exist)
    sample_org_id = "00000000-0000-0000-0000-000000000001"
    sample_team_id = "00000000-0000-0000-0000-000000000002"
    sample_project_id = "00000000-0000-0000-0000-000000000003"

    queries_to_analyze = [
        # Query 1: List organizations for user (with membership join)
        (
            "List organizations by user membership",
            f"""
            SELECT organizations.*
            FROM organizations
            JOIN organization_members ON organizations.id = organization_members.organization_id
            WHERE organization_members.user_id = 'user@example.com'
              AND organizations.deleted_at IS NULL
            ORDER BY organizations.created_at DESC
            """
        ),

        # Query 2: List teams filtered by organization_id
        (
            "List teams by organization_id",
            f"""
            SELECT * FROM teams
            WHERE organization_id = '{sample_org_id}'
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            """
        ),

        # Query 3: List projects filtered by team_id and organization_id
        (
            "List projects by team_id and organization_id",
            f"""
            SELECT * FROM projects
            WHERE team_id = '{sample_team_id}'
              AND organization_id = '{sample_org_id}'
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            """
        ),

        # Query 4: List tasks filtered by project_id and organization_id
        (
            "List tasks by project_id and organization_id",
            f"""
            SELECT * FROM task
            WHERE project_id = '{sample_project_id}'
              AND organization_id = '{sample_org_id}'
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            """
        ),

        # Query 5: List tasks filtered by organization_id only (cross-project query)
        (
            "List tasks by organization_id (cross-project)",
            f"""
            SELECT * FROM task
            WHERE organization_id = '{sample_org_id}'
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            """
        ),

        # Query 6: Count tasks by project (aggregate query)
        (
            "Count tasks by project_id",
            f"""
            SELECT project_id, COUNT(*) as task_count
            FROM task
            WHERE organization_id = '{sample_org_id}'
              AND deleted_at IS NULL
            GROUP BY project_id
            """
        ),

        # Query 7: Get organization by ID with membership check
        (
            "Get organization by ID with membership validation",
            f"""
            SELECT organizations.*
            FROM organizations
            JOIN organization_members ON organizations.id = organization_members.organization_id
            WHERE organizations.id = '{sample_org_id}'
              AND organization_members.user_id = 'user@example.com'
              AND organizations.deleted_at IS NULL
            """
        ),

        # Query 8: List organization members
        (
            "List organization members",
            f"""
            SELECT * FROM organization_members
            WHERE organization_id = '{sample_org_id}'
            ORDER BY created_at
            """
        ),

        # Query 9: Check project membership
        (
            "Check project membership",
            f"""
            SELECT * FROM project_members
            WHERE project_id = '{sample_project_id}'
              AND user_id = 'user@example.com'
            """
        ),

        # Query 10: List tasks assigned to user in organization
        (
            "List tasks assigned to user in organization",
            f"""
            SELECT * FROM task
            WHERE organization_id = '{sample_org_id}'
              AND assigned_to = 'user@example.com'
              AND deleted_at IS NULL
            ORDER BY created_at DESC
            """
        ),
    ]

    results = []

    for query_name, sql_query in queries_to_analyze:
        try:
            result = await explain_analyze_query(query_name, sql_query)
            results.append(result)
        except Exception as e:
            print(f"\nError analyzing query '{query_name}': {e}")
            results.append({
                "query_name": query_name,
                "error": str(e),
            })

    # Summary report
    print("\n" + "="*80)
    print("Performance Summary")
    print("="*80)

    slow_queries = []
    missing_indexes = []

    for result in results:
        query_name = result["query_name"]
        exec_time = result.get("execution_time_ms")
        plan = result.get("plan", [])

        print(f"\n{query_name}:")

        if "error" in result:
            print(f"  ❌ ERROR: {result['error']}")
            continue

        if exec_time:
            if exec_time < 100:
                print(f"  ✅ Execution time: {exec_time:.2f}ms (GOOD)")
            else:
                print(f"  ⚠️  Execution time: {exec_time:.2f}ms (SLOW - target <100ms)")
                slow_queries.append((query_name, exec_time))

        # Check for index usage
        plan_text = " ".join(plan)

        if "Index Scan" in plan_text or "Index Only Scan" in plan_text:
            print(f"  ✅ Uses index")
        elif "Seq Scan" in plan_text:
            print(f"  ⚠️  Sequential scan detected (may need index)")
            missing_indexes.append(query_name)

    # Final recommendations
    print("\n" + "="*80)
    print("Recommendations")
    print("="*80)

    if slow_queries:
        print("\n⚠️  Slow queries (>100ms):")
        for query_name, exec_time in slow_queries:
            print(f"  - {query_name}: {exec_time:.2f}ms")
        print("\nAction: Review query plans above and add indexes if needed")
    else:
        print("\n✅ All queries execute in <100ms")

    if missing_indexes:
        print("\n⚠️  Queries with sequential scans:")
        for query_name in missing_indexes:
            print(f"  - {query_name}")
        print("\nAction: Consider adding indexes on frequently filtered columns")
    else:
        print("\n✅ All queries use indexes")

    print("\n" + "="*80)
    print("Analysis Complete")
    print("="*80)


async def check_existing_indexes():
    """
    Check what indexes currently exist on multi-tenant tables.
    """
    print("\n" + "="*80)
    print("Existing Indexes on Multi-Tenant Tables")
    print("="*80)

    tables = ["organizations", "teams", "projects", "task",
              "organization_members", "team_members", "project_members"]

    async with engine.begin() as conn:
        for table in tables:
            print(f"\n{table}:")
            print("-" * 80)

            result = await conn.execute(text(f"""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = '{table}'
                ORDER BY indexname
            """))

            indexes = list(result)

            if indexes:
                for idx_name, idx_def in indexes:
                    print(f"  {idx_name}")
                    print(f"    {idx_def}")
            else:
                print("  No indexes found")


async def main():
    """Main entry point for query performance analysis."""
    print("\n" + "="*80)
    print("Multi-Tenant Query Performance Analysis Script")
    print("Task: T147 [US6] - Verify index usage and query performance")
    print("="*80)

    # Check existing indexes first
    await check_existing_indexes()

    # Analyze query performance
    await analyze_multi_tenant_queries()


if __name__ == "__main__":
    asyncio.run(main())
