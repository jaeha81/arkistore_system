"""initial schema

Revision ID: 20260312_000000
Revises:
Create Date: 2026-03-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260312_000000"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------ #
    # ENUM types                                                           #
    # ------------------------------------------------------------------ #
    projectstatus = postgresql.ENUM(
        "active", "paused", "archived", name="projectstatus", create_type=False
    )
    operationmode = postgresql.ENUM(
        "normal", "manual_support", "agent_enabled", "hybrid",
        name="operationmode", create_type=False,
    )
    environment = postgresql.ENUM(
        "development", "staging", "production", name="environment", create_type=False
    )
    sitetype = postgresql.ENUM(
        "main_dashboard", "logistics", "sales", "store_manager",
        name="sitetype", create_type=False,
    )
    issuestatus = postgresql.ENUM(
        "new", "grouped", "triaged", "github_created", "resolved", "ignored",
        name="issuestatus", create_type=False,
    )
    inventorystatus = postgresql.ENUM(
        "normal", "low_stock", "out_of_stock", "inbound_pending",
        name="inventorystatus", create_type=False,
    )
    customergrade = postgresql.ENUM(
        "normal", "repeat", "vip", name="customergrade", create_type=False
    )
    leadstatus = postgresql.ENUM(
        "new", "in_progress", "converted", "closed", "dropped",
        name="leadstatus", create_type=False,
    )
    contractstatus = postgresql.ENUM(
        "draft", "signed", "confirmed", "cancelled",
        name="contractstatus", create_type=False,
    )
    purchaserequeststatus = postgresql.ENUM(
        "requested", "reviewed", "approved", "rejected", "converted_to_order",
        name="purchaserequeststatus", create_type=False,
    )
    purchaseorderstatus = postgresql.ENUM(
        "created", "ordered", "invoiced", "shipped", "completed", "cancelled",
        name="purchaseorderstatus", create_type=False,
    )
    paymentstatus = postgresql.ENUM(
        "unpaid", "partially_paid", "paid", name="paymentstatus", create_type=False
    )
    deliverystatus = postgresql.ENUM(
        "scheduled", "confirmed", "in_transit", "completed", "delayed", "cancelled",
        name="deliverystatus", create_type=False,
    )
    slotstatus = postgresql.ENUM(
        "open", "limited", "full", "closed", name="slotstatus", create_type=False
    )
    syncjobstatus = postgresql.ENUM(
        "pending", "running", "completed", "failed",
        name="syncjobstatus", create_type=False,
    )

    # Create enums explicitly
    for enum in [
        projectstatus, operationmode, environment, sitetype, issuestatus,
        inventorystatus, customergrade, leadstatus, contractstatus,
        purchaserequeststatus, purchaseorderstatus, paymentstatus,
        deliverystatus, slotstatus, syncjobstatus,
    ]:
        enum.create(op.get_bind(), checkfirst=True)

    # ------------------------------------------------------------------ #
    # TABLE: roles                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: users                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.Text, nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="arki_store_manager"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ------------------------------------------------------------------ #
    # TABLE: products                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("brand_name", sa.String(200), nullable=False),
        sa.Column("product_code", sa.String(100), nullable=False),
        sa.Column("product_name", sa.String(300), nullable=False),
        sa.Column("category_name", sa.String(200), nullable=True),
        sa.Column("option_text", sa.String(500), nullable=True),
        sa.Column("unit_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("supplier_name", sa.String(200), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_code"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: projects                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("client_name", sa.String(200), nullable=False),
        sa.Column("service_type", sa.String(100), nullable=False),
        sa.Column("main_url", sa.String(500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("active", "paused", "archived", name="projectstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "operation_mode",
            sa.Enum("normal", "manual_support", "agent_enabled", "hybrid", name="operationmode"),
            nullable=False,
            server_default="normal",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_code"),
    )
    op.create_index("ix_projects_project_code", "projects", ["project_code"], unique=True)

    # ------------------------------------------------------------------ #
    # TABLE: capacity_slots                                                #
    # ------------------------------------------------------------------ #
    op.create_table(
        "capacity_slots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slot_date", sa.Date, nullable=False),
        sa.Column("delivery_team", sa.String(100), nullable=False),
        sa.Column("time_slot", sa.String(50), nullable=False),
        sa.Column("max_capacity", sa.Integer, nullable=False),
        sa.Column("used_capacity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("remaining_capacity", sa.Integer, nullable=False),
        sa.Column(
            "slot_status",
            sa.Enum("open", "limited", "full", "closed", name="slotstatus"),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slot_date", "delivery_team", "time_slot", name="uq_capacity_slot"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: attachments  (no FK to users to avoid user->attachment cycle) #
    # ------------------------------------------------------------------ #
    op.create_table(
        "attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("file_key", sa.String(500), nullable=False),
        sa.Column("file_type", sa.String(100), nullable=False),
        sa.Column("file_url", sa.String(1000), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("related_table", sa.String(100), nullable=False),
        sa.Column("related_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_key"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: project_sites                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "project_sites",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_code", sa.String(50), nullable=False),
        sa.Column("site_name", sa.String(200), nullable=False),
        sa.Column("site_url", sa.String(500), nullable=False),
        sa.Column(
            "site_type",
            sa.Enum(
                "main_dashboard", "logistics", "sales", "store_manager",
                name="sitetype",
            ),
            nullable=False,
        ),
        sa.Column("is_enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("site_code"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: customers                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_type", sa.String(50), nullable=False, server_default="individual"),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("phone_masked", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("email_masked", sa.String(255), nullable=True),
        sa.Column("region", sa.String(100), nullable=True),
        sa.Column("source_channel", sa.String(100), nullable=True),
        sa.Column(
            "grade",
            sa.Enum("normal", "repeat", "vip", name="customergrade"),
            nullable=False,
            server_default="normal",
        ),
        sa.Column("is_vip", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: consultations                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "consultations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("manager_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consultation_type", sa.String(100), nullable=False),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("needs_text", sa.Text, nullable=True),
        sa.Column("next_action", sa.Text, nullable=True),
        sa.Column("consultation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["manager_user_id"], ["users.id"], ondelete="RESTRICT"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: leads                                                         #
    # ------------------------------------------------------------------ #
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_channel", sa.String(100), nullable=False),
        sa.Column("inquiry_title", sa.String(300), nullable=False),
        sa.Column("inquiry_content", sa.Text, nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "lead_status",
            sa.Enum("new", "in_progress", "converted", "closed", "dropped", name="leadstatus"),
            nullable=False,
            server_default="new",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["assigned_to"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: issue_groups  (github_issue_id FK added after github_issues) #
    # ------------------------------------------------------------------ #
    op.create_table(
        "issue_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("group_key", sa.String(255), nullable=False),
        sa.Column("group_title", sa.String(500), nullable=False),
        sa.Column("occurrence_count", sa.Integer, nullable=False, server_default="1"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "group_status",
            sa.Enum(
                "new", "grouped", "triaged", "github_created", "resolved", "ignored",
                name="issuestatus",
            ),
            nullable=False,
            server_default="new",
        ),
        # github_issue_id FK added AFTER github_issues table is created
        sa.Column("github_issue_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_key"),
    )
    op.create_index("ix_issue_groups_group_key", "issue_groups", ["group_key"], unique=True)

    # ------------------------------------------------------------------ #
    # TABLE: github_issues                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "github_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("issue_group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("repository", sa.String(200), nullable=False),
        sa.Column("github_issue_number", sa.Integer, nullable=False),
        sa.Column("github_issue_url", sa.String(500), nullable=False),
        sa.Column("state", sa.String(50), nullable=False, server_default="open"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["issue_group_id"], ["issue_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    # Add deferred FK from issue_groups → github_issues (breaks circular dep)
    op.create_foreign_key(
        "fk_issue_groups_github_issue_id",
        "issue_groups",
        "github_issues",
        ["github_issue_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # ------------------------------------------------------------------ #
    # TABLE: error_reports                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "error_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_code", sa.String(50), nullable=False),
        sa.Column(
            "site_type",
            sa.Enum(
                "main_dashboard", "logistics", "sales", "store_manager",
                name="sitetype",
            ),
            nullable=False,
        ),
        sa.Column(
            "environment",
            sa.Enum("development", "staging", "production", name="environment"),
            nullable=False,
        ),
        sa.Column("app_version", sa.String(50), nullable=False),
        sa.Column("screen_name", sa.String(200), nullable=True),
        sa.Column("error_code", sa.String(100), nullable=False),
        sa.Column("error_message", sa.Text, nullable=False),
        sa.Column("error_message_masked", sa.Text, nullable=True),
        sa.Column("user_context", postgresql.JSONB, nullable=True),
        sa.Column(
            "report_status",
            sa.Enum(
                "new", "grouped", "triaged", "github_created", "resolved", "ignored",
                name="issuestatus",
            ),
            nullable=False,
            server_default="new",
        ),
        sa.Column("issue_group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("trace_id", sa.String(200), nullable=True),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["issue_group_id"], ["issue_groups.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_error_reports_project_code", "error_reports", ["project_code"])
    op.create_index("ix_error_reports_error_code", "error_reports", ["error_code"])

    # ------------------------------------------------------------------ #
    # TABLE: event_logs                                                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "event_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_code", sa.String(50), nullable=False),
        sa.Column(
            "environment",
            sa.Enum("development", "staging", "production", name="environment"),
            nullable=False,
        ),
        sa.Column("app_version", sa.String(50), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("event_name", sa.String(200), nullable=False),
        sa.Column("payload", postgresql.JSONB, nullable=True),
        sa.Column(
            "logged_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_logs_project_code", "event_logs", ["project_code"])
    op.create_index("ix_event_logs_event_type", "event_logs", ["event_type"])

    # ------------------------------------------------------------------ #
    # TABLE: admin_actions                                                 #
    # ------------------------------------------------------------------ #
    op.create_table(
        "admin_actions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action_type", sa.String(100), nullable=False),
        sa.Column("target_table", sa.String(100), nullable=False),
        sa.Column("target_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("before_data", postgresql.JSONB, nullable=True),
        sa.Column("after_data", postgresql.JSONB, nullable=True),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_admin_actions_action_type", "admin_actions", ["action_type"])

    # ------------------------------------------------------------------ #
    # TABLE: deployment_records                                            #
    # ------------------------------------------------------------------ #
    op.create_table(
        "deployment_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("site_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "environment",
            sa.Enum("development", "staging", "production", name="environment"),
            nullable=False,
        ),
        sa.Column("version_tag", sa.String(100), nullable=False),
        sa.Column("deployed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deploy_notes", sa.Text, nullable=True),
        sa.Column(
            "deployed_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("status", sa.String(50), nullable=False, server_default="success"),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["site_id"], ["project_sites.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["deployed_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: sheet_sync_jobs                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        "sheet_sync_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_code", sa.String(50), nullable=False),
        sa.Column("sheet_name", sa.String(200), nullable=False),
        sa.Column("dataset", sa.String(200), nullable=False),
        sa.Column("job_type", sa.String(50), nullable=False, server_default="export"),
        sa.Column(
            "job_status",
            sa.Enum("pending", "running", "completed", "failed", name="syncjobstatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("result_url", sa.String(1000), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("idempotency_key"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: contracts                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_number", sa.String(100), nullable=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consultation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("contract_date", sa.Date, nullable=False),
        sa.Column("contract_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column(
            "contract_status",
            sa.Enum("draft", "signed", "confirmed", "cancelled", name="contractstatus"),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("delivery_required", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("remarks", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("contract_number"),
        sa.UniqueConstraint("idempotency_key"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["consultation_id"], ["consultations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: deliveries                                                    #
    # ------------------------------------------------------------------ #
    op.create_table(
        "deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_number", sa.String(100), nullable=True),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_date", sa.Date, nullable=False),
        sa.Column("time_slot", sa.String(50), nullable=False),
        sa.Column("delivery_team", sa.String(100), nullable=False),
        sa.Column("vehicle_code", sa.String(50), nullable=True),
        sa.Column("address_text", sa.Text, nullable=False),
        sa.Column("ladder_required", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column(
            "delivery_status",
            sa.Enum(
                "scheduled", "confirmed", "in_transit", "completed", "delayed", "cancelled",
                name="deliverystatus",
            ),
            nullable=False,
            server_default="scheduled",
        ),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("delivery_number"),
        sa.UniqueConstraint("idempotency_key"),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: happy_calls                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "happy_calls",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("delivery_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("call_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("address_confirmed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("ladder_confirmed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("contact_confirmed", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("special_notes", sa.Text, nullable=True),
        sa.Column("call_result", sa.String(100), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["delivery_id"], ["deliveries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: inventories                                                   #
    # ------------------------------------------------------------------ #
    op.create_table(
        "inventories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("warehouse_name", sa.String(200), nullable=False),
        sa.Column("current_stock", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("reserved_stock", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("available_stock", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("safety_stock", sa.Numeric(12, 4), nullable=False, server_default="0"),
        sa.Column("expected_inbound_date", sa.Date, nullable=True),
        sa.Column(
            "inventory_status",
            sa.Enum(
                "normal", "low_stock", "out_of_stock", "inbound_pending",
                name="inventorystatus",
            ),
            nullable=False,
            server_default="normal",
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: purchase_requests                                             #
    # ------------------------------------------------------------------ #
    op.create_table(
        "purchase_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_number", sa.String(100), nullable=True),
        sa.Column("request_source", sa.String(100), nullable=False),
        sa.Column(
            "request_status",
            sa.Enum(
                "requested", "reviewed", "approved", "rejected", "converted_to_order",
                name="purchaserequeststatus",
            ),
            nullable=False,
            server_default="requested",
        ),
        sa.Column("required_date", sa.Date, nullable=True),
        sa.Column("reason_text", sa.Text, nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_number"),
        sa.UniqueConstraint("idempotency_key"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: purchase_request_items                                        #
    # ------------------------------------------------------------------ #
    op.create_table(
        "purchase_request_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("requested_qty", sa.Numeric(12, 4), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["request_id"], ["purchase_requests.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: purchase_orders                                               #
    # ------------------------------------------------------------------ #
    op.create_table(
        "purchase_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_number", sa.String(100), nullable=True),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("supplier_name", sa.String(200), nullable=False),
        sa.Column("order_date", sa.Date, nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column(
            "payment_status",
            sa.Enum("unpaid", "partially_paid", "paid", name="paymentstatus"),
            nullable=False,
            server_default="unpaid",
        ),
        sa.Column(
            "order_status",
            sa.Enum(
                "created", "ordered", "invoiced", "shipped", "completed", "cancelled",
                name="purchaseorderstatus",
            ),
            nullable=False,
            server_default="created",
        ),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("idempotency_key", sa.String(255), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_number"),
        sa.UniqueConstraint("idempotency_key"),
        sa.ForeignKeyConstraint(
            ["purchase_request_id"], ["purchase_requests.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: purchase_order_items                                          #
    # ------------------------------------------------------------------ #
    op.create_table(
        "purchase_order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ordered_qty", sa.Numeric(12, 4), nullable=False),
        sa.Column("unit_price", sa.Numeric(12, 4), nullable=False),
        sa.Column("line_total", sa.Numeric(14, 2), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["order_id"], ["purchase_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
    )

    # ------------------------------------------------------------------ #
    # TABLE: shipments                                                     #
    # ------------------------------------------------------------------ #
    op.create_table(
        "shipments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("bl_number", sa.String(100), nullable=False),
        sa.Column("shipping_company", sa.String(200), nullable=True),
        sa.Column("departure_date", sa.Date, nullable=True),
        sa.Column("estimated_arrival_date", sa.Date, nullable=True),
        sa.Column("actual_arrival_date", sa.Date, nullable=True),
        sa.Column("customs_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("shipment_status", sa.String(50), nullable=False, server_default="in_transit"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bl_number"),
        sa.ForeignKeyConstraint(
            ["purchase_order_id"], ["purchase_orders.id"], ondelete="RESTRICT"
        ),
    )

    # ------------------------------------------------------------------ #
    # TABLE: invoices                                                      #
    # ------------------------------------------------------------------ #
    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("invoice_number", sa.String(100), nullable=False),
        sa.Column("invoice_date", sa.Date, nullable=False),
        sa.Column("invoice_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("file_attachment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invoice_number"),
        sa.ForeignKeyConstraint(
            ["purchase_order_id"], ["purchase_orders.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["file_attachment_id"], ["attachments.id"], ondelete="SET NULL"
        ),
    )

    # ------------------------------------------------------------------ #
    # Seed: default roles                                                  #
    # ------------------------------------------------------------------ #
    op.execute(
        """
        INSERT INTO roles (id, name, description, created_at) VALUES
        (gen_random_uuid(), 'super_admin',        'Super administrator with all permissions',  now()),
        (gen_random_uuid(), 'ops_admin',          'JH Ops domain administrator',               now()),
        (gen_random_uuid(), 'arki_logistics',     'Arkistore logistics team member',            now()),
        (gen_random_uuid(), 'arki_sales',         'Arkistore sales team member',                now()),
        (gen_random_uuid(), 'arki_store_manager', 'Arkistore store manager',                    now()),
        (gen_random_uuid(), 'support_operator',   'Support/read-only operator',                 now())
        ON CONFLICT (name) DO NOTHING;
        """
    )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table("invoices")
    op.drop_table("shipments")
    op.drop_table("purchase_order_items")
    op.drop_table("purchase_orders")
    op.drop_table("purchase_request_items")
    op.drop_table("purchase_requests")
    op.drop_table("inventories")
    op.drop_table("happy_calls")
    op.drop_table("deliveries")
    op.drop_table("contracts")
    op.drop_table("sheet_sync_jobs")
    op.drop_table("deployment_records")
    op.drop_table("admin_actions")
    op.drop_table("event_logs")
    op.drop_table("error_reports")

    # Drop circular FK before dropping tables
    op.drop_constraint("fk_issue_groups_github_issue_id", "issue_groups", type_="foreignkey")
    op.drop_table("github_issues")
    op.drop_table("issue_groups")

    op.drop_table("leads")
    op.drop_table("consultations")
    op.drop_table("customers")
    op.drop_table("project_sites")
    op.drop_table("attachments")
    op.drop_table("capacity_slots")
    op.drop_table("projects")
    op.drop_table("products")
    op.drop_table("users")
    op.drop_table("roles")

    # Drop enum types
    for enum_name in [
        "projectstatus", "operationmode", "environment", "sitetype",
        "issuestatus", "inventorystatus", "customergrade", "leadstatus",
        "contractstatus", "purchaserequeststatus", "purchaseorderstatus",
        "paymentstatus", "deliverystatus", "slotstatus", "syncjobstatus",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {enum_name}")
