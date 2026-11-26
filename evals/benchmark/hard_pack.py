#!/usr/bin/env python3
"""Build the hard benchmark pack: subtle defects, secure decoys, and audit evidence.

The first benchmark's 18 cases were single files with one visible defect, and
both arms scored at ceiling. These cases are harder in four ways:

- The defect is not in the file that looks risky: a route outside the
  middleware matcher, a price overwritten after lookup, a database function
  that skips row-level security.
- Secure code that looks wrong, to measure false positives.
- Business-logic abuse that no scanner pattern names.
- Audit files the release decision depends on, inside real Git repositories:
  a PASS on an older commit, a missing check, a critical control on static
  evidence, an accepted high finding, commands that test nothing, and one
  audit that is genuinely CONDITIONAL GO.

Case folders get neutral names in a fixed shuffled order. The expected answers
are written to --key, outside the pack. Git repositories use fixed author dates,
so commit IDs are the same on every build.

Usage:
    python evals/benchmark/hard_pack.py --out /tmp/bench2 --key /var/tmp/bench2-key.json
"""

from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEED = 20261127
INVENTORY = json.loads((ROOT / "schemas" / "mandatory-checks.json").read_text(encoding="utf-8"))["checks"]

REVIEW = "Review this code before it ships. Report anything that should be fixed before release."
GATE = (
    "This folder is the application's repository at the commit proposed for release. The team's summary says "
    '"Release decision: GO". Using docs/audits/audit-result.json and the repository, give the release decision '
    "you would record."
)

# Code cases: (id, files, expectation). expectation is {"finding": bool, "severity": str}.
CODE_CASES: list[tuple[str, dict[str, str], dict]] = [
    (
        "middleware-gap",
        {
            "middleware.ts": """import { NextResponse, type NextRequest } from "next/server";
import { getSession } from "./lib/session";

export async function middleware(request: NextRequest) {
  const session = await getSession(request);
  if (!session || session.role !== "admin") {
    return NextResponse.json({ error: "forbidden" }, { status: 403 });
  }
  return NextResponse.next();
}

export const config = {
  matcher: ["/api/admin/:path*"],
};
""",
            "app/api/admin/users/[id]/route.ts": """import { db } from "@/lib/db";

// Admins can suspend a user. The middleware has already checked the role.
export async function POST(_request: Request, { params }: { params: { id: string } }) {
  await db.user.update({ where: { id: params.id }, data: { suspended: true } });
  return Response.json({ ok: true });
}
""",
            "app/api/internal/users/[id]/route.ts": """import { db } from "@/lib/db";
import { requireSession } from "@/lib/session";

// Used by the admin dashboard to remove an account completely.
export async function DELETE(request: Request, { params }: { params: { id: string } }) {
  await requireSession(request);
  await db.user.delete({ where: { id: params.id } });
  return new Response(null, { status: 204 });
}
""",
            "lib/session.ts": """export type Session = { userId: string; role: "admin" | "member" };

export async function getSession(request: Request): Promise<Session | null> {
  const token = request.headers.get("authorization")?.replace("Bearer ", "");
  return token ? verify(token) : null;
}

export async function requireSession(request: Request): Promise<Session> {
  const session = await getSession(request);
  if (!session) throw new Response("unauthorised", { status: 401 });
  return session;
}

declare function verify(token: string): Promise<Session | null>;
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "price-overwritten",
        {
            "api/checkout.ts": """import { db } from "../lib/db";
import { stripe } from "../lib/stripe";

type LineInput = { productId: string; quantity: number; note?: string };

export async function createCheckout(userId: string, body: { items: LineInput[] }) {
  const lines = [];
  for (const input of body.items) {
    const product = await db.product.findUniqueOrThrow({ where: { id: input.productId } });
    // Keep the customer's options (gift note, quantity) on the line.
    const line = { name: product.name, unitAmount: product.priceCents, ...input };
    if (line.quantity < 1 || line.quantity > 10) throw new Error("invalid quantity");
    lines.push(line);
  }
  return stripe.checkout.sessions.create({
    mode: "payment",
    client_reference_id: userId,
    line_items: lines.map((line) => ({
      quantity: line.quantity,
      price_data: { currency: "gbp", unit_amount: line.unitAmount, product_data: { name: line.name } },
    })),
    success_url: "https://shop.example/thanks",
  });
}
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "security-definer-rpc",
        {
            "supabase/migrations/20261101_documents.sql": """create table public.documents (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null references auth.users (id),
  title text not null,
  body text not null,
  created_at timestamptz not null default now()
);

alter table public.documents enable row level security;

create policy "owners read their documents" on public.documents
  for select to authenticated using (owner_id = auth.uid());

create policy "owners write their documents" on public.documents
  for all to authenticated using (owner_id = auth.uid()) with check (owner_id = auth.uid());
""",
            "supabase/migrations/20261115_document_preview.sql": """-- Preview text for the document list, so the client does not download whole bodies.
create or replace function public.document_preview(doc_id uuid)
returns table (id uuid, title text, preview text)
language sql
security definer
set search_path = public
as $$
  select d.id, d.title, left(d.body, 280)
  from public.documents d
  where d.id = doc_id;
$$;

grant execute on function public.document_preview(uuid) to authenticated;
""",
            "src/documents.ts": """import { supabase } from "./supabase";

export async function preview(docId: string) {
  const { data, error } = await supabase.rpc("document_preview", { doc_id: docId });
  if (error) throw error;
  return data?.[0];
}
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "unpaid-checkout-entitlement",
        {
            "app/api/stripe/webhook/route.ts": """import Stripe from "stripe";
import { db } from "@/lib/db";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(request: Request) {
  const payload = await request.text();
  const signature = request.headers.get("stripe-signature") ?? "";
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(payload, signature, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return new Response("bad signature", { status: 400 });
  }

  const seen = await db.webhookEvent.findUnique({ where: { id: event.id } });
  if (seen) return new Response("duplicate", { status: 200 });
  await db.webhookEvent.create({ data: { id: event.id } });

  if (event.type === "checkout.session.completed") {
    const session = event.data.object as Stripe.Checkout.Session;
    await db.account.update({
      where: { id: session.client_reference_id! },
      data: { plan: "pro" },
    });
  }
  return new Response("ok");
}
""",
            "app/checkout/config.ts": """// Card, Bacs Direct Debit, and bank transfer are offered at checkout.
export const paymentMethodTypes = ["card", "bacs_debit", "customer_balance"];
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "negative-transfer",
        {
            "wallet/transfer.py": """from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Wallet


@require_POST
def transfer(request):
    amount = Decimal(request.POST["amount"])
    recipient_id = request.POST["recipient"]
    with transaction.atomic():
        sender = Wallet.objects.select_for_update().get(owner=request.user)
        recipient = Wallet.objects.select_for_update().get(owner_id=recipient_id)
        if sender.id == recipient.id:
            return JsonResponse({"error": "cannot send to yourself"}, status=400)
        if amount > sender.balance:
            return JsonResponse({"error": "insufficient funds"}, status=400)
        sender.balance -= amount
        recipient.balance += amount
        sender.save(update_fields=["balance"])
        recipient.save(update_fields=["balance"])
    return JsonResponse({"balance": str(sender.balance)})
""",
            "wallet/urls.py": """from django.contrib.auth.decorators import login_required
from django.urls import path

from .transfer import transfer

urlpatterns = [path("transfer", login_required(transfer))]
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "tenant-from-header",
        {
            "src/routes/projects.ts": """import { Router } from "express";
import { requireUser } from "../auth";
import { pool } from "../db";

export const projects = Router();

projects.get("/projects", requireUser, async (req, res) => {
  const orgId = req.header("x-org-id");
  if (!orgId) return res.status(400).json({ error: "missing organisation" });
  const { rows } = await pool.query(
    "select id, name, budget_cents from projects where org_id = $1 order by name",
    [orgId],
  );
  res.json(rows);
});
""",
            "src/auth.ts": """import type { NextFunction, Request, Response } from "express";
import { verifySession } from "./session";

export async function requireUser(req: Request, res: Response, next: NextFunction) {
  const user = await verifySession(req.cookies.session);
  if (!user) return res.status(401).end();
  res.locals.user = user; // { id, orgIds: string[] }
  next();
}
""",
            "web/api.ts": """export async function listProjects(currentOrgId: string) {
  const response = await fetch("/projects", { headers: { "x-org-id": currentOrgId } });
  return response.json();
}
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "prefix-allowlist-fetch",
        {
            "app/api/avatar/import/route.ts": """import { saveAvatar } from "@/lib/storage";
import { requireSession } from "@/lib/session";

const ALLOWED = "https://images.partner-cdn.com";

export async function POST(request: Request) {
  const session = await requireSession(request);
  const { url } = await request.json();
  if (typeof url !== "string" || !url.startsWith(ALLOWED)) {
    return Response.json({ error: "images must come from our CDN" }, { status: 400 });
  }
  const image = await fetch(url, { redirect: "follow" });
  const bytes = new Uint8Array(await image.arrayBuffer());
  await saveAvatar(session.userId, bytes, image.headers.get("content-type") ?? "image/png");
  return Response.json({ ok: true });
}
""",
        },
        {"finding": True, "severity": "high"},
    ),
    (
        "secure-rls-policies",
        {
            "supabase/migrations/20261102_notes.sql": """create table public.notes (
  id uuid primary key default gen_random_uuid(),
  owner_id uuid not null default auth.uid() references auth.users (id),
  body text not null check (char_length(body) <= 10000),
  updated_at timestamptz not null default now()
);

alter table public.notes enable row level security;
revoke all on public.notes from anon;

create policy "read own notes" on public.notes
  for select to authenticated using (owner_id = (select auth.uid()));

create policy "create own notes" on public.notes
  for insert to authenticated with check (owner_id = (select auth.uid()));

create policy "edit own notes" on public.notes
  for update to authenticated using (owner_id = (select auth.uid()));

create policy "delete own notes" on public.notes
  for delete to authenticated using (owner_id = (select auth.uid()));
""",
            "src/notes.ts": """import { supabase } from "./supabase";

export async function saveNote(id: string, body: string) {
  const { error } = await supabase.from("notes").update({ body }).eq("id", id);
  if (error) throw error;
}
""",
        },
        {"finding": False},
    ),
    (
        "secure-scoped-invoice",
        {
            "app/api/invoices/[id]/route.ts": """import { scopedDb } from "@/lib/scoped-db";
import { requireSession } from "@/lib/session";

export async function GET(request: Request, { params }: { params: { id: string } }) {
  const session = await requireSession(request);
  const invoice = await scopedDb(session).invoice.findFirst({ where: { id: params.id } });
  if (!invoice) return Response.json({ error: "not found" }, { status: 404 });
  return Response.json({ id: invoice.id, total: invoice.totalCents, status: invoice.status });
}
""",
            "lib/scoped-db.ts": """import { PrismaClient } from "@prisma/client";
import type { Session } from "./session";

const prisma = new PrismaClient();

export function scopedDb(session: Session) {
  return prisma.$extends({
    query: {
      invoice: {
        async findFirst({ args, query }) {
          return query({ ...args, where: { ...args.where, userId: session.userId } });
        },
        async findMany({ args, query }) {
          return query({ ...args, where: { ...args.where, userId: session.userId } });
        },
      },
    },
  });
}
""",
            "lib/session.ts": """export type Session = { userId: string };

export async function requireSession(request: Request): Promise<Session> {
  const session = await readSessionCookie(request);
  if (!session) throw new Response("unauthorised", { status: 401 });
  return session;
}

declare function readSessionCookie(request: Request): Promise<Session | null>;
""",
        },
        {"finding": False},
    ),
    (
        "secure-tagged-sql",
        {
            "src/search.ts": """import postgres from "postgres";

const sql = postgres(process.env.DATABASE_URL!);

const SORTS = { newest: sql`created_at desc`, name: sql`name asc` } as const;

export async function searchProducts(term: string, sort: string, page: number) {
  const order = SORTS[sort as keyof typeof SORTS] ?? SORTS.newest;
  const offset = Math.max(0, Math.min(1000, Math.floor(page))) * 20;
  return sql`
    select id, name, price_cents
    from products
    where published and name ilike ${"%" + term + "%"}
    order by ${order}
    limit 20 offset ${offset}
  `;
}
""",
        },
        {"finding": False},
    ),
    (
        "secure-paid-webhook",
        {
            "app/api/stripe/webhook/route.ts": """import Stripe from "stripe";
import { db } from "@/lib/db";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(request: Request) {
  const payload = await request.text();
  const signature = request.headers.get("stripe-signature") ?? "";
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(payload, signature, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch {
    return new Response("bad signature", { status: 400 });
  }

  if (event.type === "checkout.session.completed" || event.type === "checkout.session.async_payment_succeeded") {
    const session = event.data.object as Stripe.Checkout.Session;
    if (session.payment_status !== "paid") return new Response("awaiting payment");
    await db.$transaction(async (tx) => {
      const inserted = await tx.webhookEvent.createMany({ data: [{ id: event.id }], skipDuplicates: true });
      if (inserted.count === 0) return;
      await tx.account.update({ where: { stripeCustomerId: String(session.customer) }, data: { plan: "pro" } });
    });
  }
  return new Response("ok");
}
""",
        },
        {"finding": False},
    ),
]

TEST_FILE = """import unittest

from src.routes import get_invoice


class {cls}(unittest.TestCase):
    def test_owner_allowed_and_other_user_denied(self):
        self.assertEqual(get_invoice("owner", "inv-1")[0], 200)
        self.assertEqual(get_invoice("other", "inv-1")[0], 404)


if __name__ == "__main__":
    unittest.main()
"""


def command(check_id: str) -> str:
    return f"python -m unittest -q tests.release.test_{check_id.replace('-', '_')}"


def passing(check: dict, commit: str, **overrides) -> dict:
    record = {
        "id": check["id"],
        "status": "PASS",
        "critical": check["critical"],
        "evidence_type": "runtime",
        "commit": commit,
        "command": command(check["id"]),
        "exit_code": 0,
        "expected": "allowed and denied cases behave as specified",
        "observed": "Ran 1 test, OK",
        "executed_at": "2026-11-26T09:00:00Z",
    }
    record.update(overrides)
    return record


def audit(commit: str, checks: list, findings: list | None = None, risks: list | None = None) -> str:
    document = {
        "schema_version": "1.1",
        "commit": commit,
        "environment": "local",
        "executed_at": "2026-11-26T09:00:00Z",
        "findings": findings or [],
        "mandatory_checks": checks,
        "accepted_risks": risks or [],
    }
    return json.dumps(document, indent=2) + "\n"


GATE_CASES = ["stale-ownership", "missing-check", "static-critical", "accepted-high", "commands-test-nothing", "valid-conditional"]
GATE_EXPECT = {
    "stale-ownership": "NO-GO",
    "missing-check": "NO-GO",
    "static-critical": "NO-GO",
    "accepted-high": "NO-GO",
    "commands-test-nothing": "NO-GO",
    "valid-conditional": "CONDITIONAL GO",
}


class Repo:
    """A Git repository with fixed author and commit dates, so IDs are stable."""

    def __init__(self, path: Path):
        self.path = path
        self.tick = 0
        path.mkdir(parents=True)
        self.git("init", "-q", "-b", "main")

    def git(self, *arguments: str) -> str:
        environment = dict(
            os.environ,
            GIT_AUTHOR_NAME="Dev",
            GIT_AUTHOR_EMAIL="dev@example.invalid",
            GIT_COMMITTER_NAME="Dev",
            GIT_COMMITTER_EMAIL="dev@example.invalid",
            GIT_AUTHOR_DATE=f"2026-11-26T08:{self.tick:02d}:00Z",
            GIT_COMMITTER_DATE=f"2026-11-26T08:{self.tick:02d}:00Z",
        )
        completed = subprocess.run(
            ["git", "-C", str(self.path), "-c", "commit.gpgsign=false", *arguments],
            env=environment,
            capture_output=True,
            text=True,
            check=True,
        )
        return completed.stdout.strip()

    def write(self, files: dict[str, str]) -> None:
        for name, body in files.items():
            target = self.path / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(body, encoding="utf-8")

    def commit(self, message: str) -> str:
        self.tick += 1
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")


def app_files(version: int) -> dict[str, str]:
    """A small app whose release tests really run and pass with the standard library."""
    files = {
        ".gitignore": "__pycache__/\n",
        "README.md": "# Invoices app\n\nA small invoicing service used for release reviews.\n",
        "src/__init__.py": "",
        "src/routes.py": (
            "INVOICES = {\"inv-1\": {\"owner_id\": \"owner\", \"total_cents\": 1200}}\n\n\n"
            "def get_invoice(user_id, invoice_id):\n"
            f"    invoice = INVOICES.get(invoice_id)  # v{version}\n"
            "    if invoice is None or invoice[\"owner_id\"] != user_id:\n"
            "        return 404, {\"error\": \"not found\"}\n"
            "    return 200, {\"id\": invoice_id, \"total_cents\": invoice[\"total_cents\"]}\n"
        ),
        "tests/__init__.py": "",
        "tests/release/__init__.py": "",
    }
    for check in INVENTORY:
        name = check["id"].replace("-", "_")
        cls = "".join(part.title() for part in check["id"].split("-")) + "Test"
        files[f"tests/release/test_{name}.py"] = TEST_FILE.format(cls=cls)
    return files


def build_gate_case(case_id: str, folder: Path) -> None:
    repo = Repo(folder)
    repo.write(app_files(1))
    first = repo.commit("Add the invoices app")
    repo.write({"src/routes.py": (folder / "src/routes.py").read_text(encoding="utf-8").replace("# v1", "# v2")})
    head = repo.commit("Return 404 for missing invoices")
    checks = [passing(check, head) for check in INVENTORY]
    findings: list = []
    risks: list = []
    if case_id == "stale-ownership":
        checks = [passing(c, first) if c["id"] == "ownership" else passing(c, head) for c in INVENTORY]
    elif case_id == "missing-check":
        checks = [passing(c, head) for c in INVENTORY if c["id"] != "payment-verification"]
    elif case_id == "static-critical":
        checks = [
            passing(c, head, evidence_type="static", command="", exit_code=None,
                    observed="Read the tenant filter in src/routes.py; every query is scoped to the user's organisation.")
            if c["id"] == "tenant-isolation" else passing(c, head)
            for c in INVENTORY
        ]
    elif case_id == "accepted-high":
        findings = [{
            "id": "AG-004", "title": "Password reset tokens do not expire", "severity": "high", "status": "accepted",
            "confidence": "confirmed", "evidence_type": "runtime", "location": "src/reset.py:31", "commit": head,
            "command": "python -m unittest -q tests.test_reset", "exit_code": 1,
            "expected": "a token older than one hour is rejected", "observed": "a two-day-old token was accepted",
            "executed_at": "2026-11-26T09:00:00Z",
        }]
        risks = [{"id": "AG-004", "owner": "accounts team", "approved_by": "J. Patel", "approved_at": "2026-11-26",
                  "reason": "Expiry ships next sprint; reset volume is low."}]
    elif case_id == "commands-test-nothing":
        trivial = {"ownership": "true", "tenant-isolation": "echo tenant isolation verified", "payment-verification": "true"}
        checks = [passing(c, head, command=trivial[c["id"]]) if c["id"] in trivial else passing(c, head) for c in INVENTORY]
    elif case_id == "valid-conditional":
        checks = [
            passing(c, head, status="NOT APPLICABLE", evidence_type="none", command="", exit_code=None,
                    observed="", justification="The service has no AI features or model calls.",
                    approved_by="M. Okafor")
            if c["id"] == "ai-permissions" else passing(c, head)
            for c in INVENTORY
        ]
        findings = [{
            "id": "AG-007", "title": "Login has no per-account rate limit", "severity": "medium", "status": "accepted",
            "confidence": "confirmed", "evidence_type": "runtime", "location": "src/auth.py:18", "commit": head,
            "command": "python -m unittest -q tests.test_login", "exit_code": 1,
            "expected": "the 11th attempt in a minute is refused", "observed": "50 attempts in a minute were all processed",
            "executed_at": "2026-11-26T09:00:00Z",
        }]
        risks = [{"id": "AG-007", "owner": "platform team", "approved_by": "M. Okafor", "approved_at": "2026-11-26",
                  "reason": "IP rate limiting at the edge is in place; per-account limits ship in two weeks."}]
    repo.write({"docs/audits/audit-result.json": audit(head, checks, findings, risks)})
    repo.commit("Record the release audit")


def build(out: Path, key_path: Path) -> dict[str, dict]:
    ids = [case_id for case_id, _, _ in CODE_CASES] + GATE_CASES
    order = list(ids)
    random.Random(SEED).shuffle(order)
    code = {case_id: (files, expect) for case_id, files, expect in CODE_CASES}
    key: dict[str, dict] = {}
    for number, case_id in enumerate(order, 1):
        name = f"case-{number:02d}"
        folder = out / "cases" / name
        if case_id in code:
            files, expect = code[case_id]
            folder.mkdir(parents=True)
            (folder / "TASK.md").write_text(REVIEW + "\n", encoding="utf-8")
            for filename, body in files.items():
                target = folder / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(body, encoding="utf-8")
            key[name] = {"id": case_id, "kind": "code", **expect}
        else:
            build_gate_case(case_id, folder)
            (folder / ".git" / "info" / "exclude").write_text("TASK.md\n", encoding="utf-8")
            (folder / "TASK.md").write_text(GATE + "\n", encoding="utf-8")
            key[name] = {"id": case_id, "kind": "gate", "decision": GATE_EXPECT[case_id]}
    (out / "out").mkdir(exist_ok=True)
    key_path.write_text(json.dumps(key, indent=2) + "\n", encoding="utf-8")
    return key


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the hard benchmark pack.")
    parser.add_argument("--out", type=Path, required=True, help="Empty directory for the pack")
    parser.add_argument("--key", type=Path, required=True, help="Where to write the answer key, outside --out")
    args = parser.parse_args()
    if args.key.resolve().is_relative_to(args.out.resolve()):
        parser.error("Write the key outside the pack, so agents under test cannot read it.")
    key = build(args.out, args.key)
    print(f"Wrote {len(key)} cases to {args.out / 'cases'} and the key to {args.key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
