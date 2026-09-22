"""Route: Economy."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from simai.economy import (
    JobService,
    LotOwnershipService,
    MarketService,
    MortgageService,
    ShopItem,
)
from simai.economy.banking import (
    BankAccount,
    BankService,
    Loan,
)
from simai.economy.companies import (
    Company,
    CompanyService,
)
from simai.economy.ledger import JournalEntry, Posting
from simai.npc.models import Character
from simai.ui.app import templates
from simai.ui.deps import get_db
from simai.world.district import District
from simai.world.enums import LocationType
from simai.world.lot import Lot
from simai.world.models import Location

router = APIRouter()


@router.get("/economy", response_class=HTMLResponse)
def economy_dashboard(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dashboard economia."""
    jobs = JobService.all_active_jobs(session)
    job_rows: list[dict[str, object]] = []
    for j in jobs:
        c = session.get(Character, j.character_id)
        wp = session.get(Location, j.workplace_id) if j.workplace_id else None
        job_rows.append(
            {
                "id": j.id,
                "title": j.title,
                "worker": c.full_name if c else "?",
                "wage": j.daily_wage,
                "workplace": wp.name if wp else "—",
                "required_skill": j.required_skill_type or "—",
            }
        )

    shops = list(session.scalars(select(Location).where(Location.type == LocationType.SHOP.value)))
    shop_rows: list[dict[str, object]] = []
    for s in shops:
        items = MarketService.items_in(session, s.id)
        shop_rows.append(
            {
                "id": s.id,
                "name": s.name,
                "items": len(items),
                "stock_total": sum(i.stock if i.stock >= 0 else 0 for i in items),
            }
        )

    entries = list(
        session.scalars(
            select(JournalEntry).order_by(JournalEntry.at_total_seconds.desc()).limit(20)
        )
    )
    tx_rows: list[dict[str, object]] = []
    for e in entries:
        # Somma DEBIT - CREDIT sui posting dell'entry per "delta netto" (flow-based)
        delta = int(
            session.scalar(
                select(
                    func.coalesce(
                        func.sum(
                            case(
                                (Posting.direction == "DEBIT", Posting.amount),
                                else_=-Posting.amount,
                            )
                        ),
                        0,
                    )
                ).where(Posting.entry_id == e.id)
            )
            or 0
        )
        tx_rows.append(
            {
                "id": e.id,
                "character": e.reference_type or "—",
                "kind": e.kind,
                "amount": delta,
                "item_type": e.description,
            }
        )
    n_items = int(session.scalar(select(ShopItem.id).limit(1)) or 0)
    total_items = len(list(session.scalars(select(ShopItem))))

    return templates.TemplateResponse(
        request,
        "economy.html",
        {
            "jobs": job_rows,
            "shops": shop_rows,
            "transactions": tx_rows,
            "total_items": total_items,
            "has_items": n_items != 0,
        },
    )


@router.get("/economy/lots", response_class=HTMLResponse)
def lots_market(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Mercato immobiliare: lista lotti con proprietario e mutuo."""
    lots = list(session.scalars(select(Lot).order_by(Lot.id)))
    rows: list[dict[str, object]] = []
    for lot in lots:
        district = session.get(District, lot.district_id)
        owner = LotOwnershipService.owner_character(session, lot.id)
        mortgage = MortgageService.of_lot(session, lot.id)
        rows.append(
            {
                "id": lot.id,
                "name": lot.name,
                "district": district.name if district else "—",
                "usage": lot.usage,
                "current_value": lot.current_value or lot.base_price,
                "owner": owner.full_name if owner else "—",
                "owner_id": owner.id if owner else None,
                "has_mortgage": mortgage is not None,
                "mortgage_remaining": (mortgage.remaining_principal if mortgage else 0.0),
            }
        )

    # Mutui attivi
    active_mortgages = MortgageService.active_mortgages(session)
    mortgage_rows: list[dict[str, object]] = []
    for m in active_mortgages:
        c = session.get(Character, m.character_id)
        m_lot = session.get(Lot, m.lot_id)
        mortgage_rows.append(
            {
                "id": m.id,
                "character": c.full_name if c else "?",
                "lot": m_lot.name if m_lot else "?",
                "remaining": m.remaining_principal,
                "payment": m.monthly_payment,
                "made": m.payments_made,
                "missed": m.payments_missed,
                "status": m.status,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_lots.html",
        {"lots": rows, "mortgages": mortgage_rows},
    )


# ---------------------------------------------------------------------------
# Banks
# ---------------------------------------------------------------------------


@router.get("/economy/banks", response_class=HTMLResponse)
def banks_list(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Lista delle banche attive con summary."""
    BankService.ensure_primary_bank(session)
    session.commit()

    banks = BankService.all_banks(session, only_active=False)
    rows: list[dict[str, object]] = []
    for b in banks:
        rec = BankService.reconcile_bank(session, b)
        n_accounts = int(
            session.scalar(
                select(func.count())
                .select_from(BankAccount)
                .where(BankAccount.bank_id == b.id, BankAccount.is_active.is_(True))
            )
            or 0
        )
        total_deposits = int(
            session.scalar(
                select(func.coalesce(func.sum(BankAccount.balance), 0)).where(
                    BankAccount.bank_id == b.id, BankAccount.is_active.is_(True)
                )
            )
            or 0
        )
        n_loans = int(
            session.scalar(
                select(func.count())
                .select_from(Loan)
                .where(Loan.bank_id == b.id, Loan.status == "ACTIVE")
            )
            or 0
        )
        total_loans = int(
            session.scalar(
                select(func.coalesce(func.sum(Loan.remaining_principal), 0)).where(
                    Loan.bank_id == b.id, Loan.status == "ACTIVE"
                )
            )
            or 0
        )
        rows.append(
            {
                "id": b.id,
                "code": b.code,
                "name": b.name,
                "kind": b.kind,
                "is_active": b.is_active,
                "deposit_interest_rate": b.deposit_interest_rate,
                "loan_interest_rate": b.loan_interest_rate,
                "reserve_ledger": rec.reserve_ledger,
                "deposits_ledger": rec.deposits_ledger,
                "loans_ledger": rec.loans_ledger,
                "n_accounts": n_accounts,
                "total_deposits": total_deposits,
                "n_loans": n_loans,
                "total_loans": total_loans,
                "reconcile_ok": rec.ok,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_banks.html",
        {"banks": rows},
    )


@router.get("/economy/banks/{code}", response_class=HTMLResponse)
def bank_detail(
    request: Request,
    code: str,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio di una banca: conti, prestiti, ultimi movimenti."""
    BankService.ensure_primary_bank(session)
    session.commit()

    bank = BankService.get_bank(session, code)
    if bank is None:
        raise HTTPException(status_code=404, detail=f"Banca {code!r} non trovata")

    rec = BankService.reconcile_bank(session, bank)

    # Conti attivi
    accounts = list(
        session.scalars(
            select(BankAccount)
            .where(BankAccount.bank_id == bank.id)
            .order_by(BankAccount.balance.desc(), BankAccount.id)
        )
    )
    account_rows: list[dict[str, object]] = []
    for acc in accounts:
        c = session.get(Character, acc.character_id)
        account_rows.append(
            {
                "id": acc.id,
                "character_id": acc.character_id,
                "character_name": c.full_name if c else "?",
                "kind": acc.kind,
                "balance": acc.balance,
                "interest_rate": acc.interest_rate,
                "is_active": acc.is_active,
                "is_frozen": acc.is_frozen,
            }
        )

    # Prestiti (attivi + recenti)
    loans = list(
        session.scalars(
            select(Loan).where(Loan.bank_id == bank.id).order_by(Loan.id.desc()).limit(50)
        )
    )
    loan_rows: list[dict[str, object]] = []
    for loan in loans:
        c = session.get(Character, loan.character_id)
        loan_rows.append(
            {
                "id": loan.id,
                "character_id": loan.character_id,
                "character_name": c.full_name if c else "?",
                "principal": loan.principal,
                "remaining_principal": loan.remaining_principal,
                "annual_interest_rate": loan.annual_interest_rate,
                "term_months": loan.term_months,
                "monthly_payment": loan.monthly_payment,
                "payments_made": loan.payments_made,
                "payments_missed": loan.payments_missed,
                "status": loan.status,
            }
        )

    # Ultime entry ledger della banca (reserve)
    from simai.economy.ledger import JournalEntry, Posting

    reserve_acc = BankService._reserve_account(session, bank)
    recent_postings = list(
        session.scalars(
            select(Posting)
            .join(JournalEntry, JournalEntry.id == Posting.entry_id)
            .where(Posting.account_id == reserve_acc.id)
            .order_by(JournalEntry.at_total_seconds.desc(), JournalEntry.id.desc())
            .limit(20)
        )
    )
    entry_ids = [p.entry_id for p in recent_postings]
    entries_by_id = {
        e.id: e for e in session.scalars(select(JournalEntry).where(JournalEntry.id.in_(entry_ids)))
    }
    ledger_rows: list[dict[str, object]] = []
    for p in recent_postings:
        e = entries_by_id.get(p.entry_id)
        if e is None:
            continue
        signed = int(p.amount) if p.direction == "DEBIT" else -int(p.amount)
        ledger_rows.append(
            {
                "entry_id": e.id,
                "kind": e.kind,
                "description": e.description,
                "direction": p.direction,
                "amount": p.amount,
                "signed_delta": signed,
                "at_total_seconds": e.at_total_seconds,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_bank_detail.html",
        {
            "bank": bank,
            "reconcile": rec,
            "accounts": account_rows,
            "loans": loan_rows,
            "ledger_rows": ledger_rows,
        },
    )


# ---------------------------------------------------------------------------
# Companies
# ---------------------------------------------------------------------------


@router.get("/economy/companies", response_class=HTMLResponse)
def companies_list(
    request: Request,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Lista delle aziende con summary (owner, dipendenti, saldo)."""
    companies = CompanyService.all_companies(session, only_active=False)
    rows: list[dict[str, object]] = []
    for c in companies:
        owner = session.get(Character, c.owner_character_id)
        employees = CompanyService.employees_of(session, c.id, only_active=True)
        rec = CompanyService.reconcile(session, c)
        rows.append(
            {
                "id": c.id,
                "name": c.name,
                "kind": c.kind,
                "status": c.status,
                "is_active": c.is_active,
                "owner_id": c.owner_character_id,
                "owner_name": owner.full_name if owner else "?",
                "n_employees": len(employees),
                "balance": c.athel_balance,
                "base_daily_revenue": c.base_daily_revenue,
                "base_daily_cost": c.base_daily_cost,
                "reconcile_ok": rec.ok,
            }
        )

    return templates.TemplateResponse(
        request,
        "economy_companies.html",
        {"companies": rows},
    )


@router.get("/economy/companies/{company_id}", response_class=HTMLResponse)
def company_detail(
    request: Request,
    company_id: int,
    session: Session = Depends(get_db),
) -> HTMLResponse:
    """Dettaglio azienda: dipendenti, movimenti, riconciliazione."""
    company = session.get(Company, company_id)
    if company is None:
        raise HTTPException(status_code=404, detail=f"Azienda id={company_id} non trovata")

    owner = session.get(Character, company.owner_character_id)
    rec = CompanyService.reconcile(session, company)

    employees = CompanyService.employees_of(session, company.id, only_active=True)
    employee_rows: list[dict[str, object]] = []
    for emp in employees:
        c = session.get(Character, emp.character_id)
        employee_rows.append(
            {
                "id": emp.id,
                "character_id": emp.character_id,
                "character_name": c.full_name if c else "?",
                "role": emp.role,
                "daily_wage": emp.daily_wage,
                "hired_at_total_seconds": emp.hired_at_total_seconds,
            }
        )

    txs = CompanyService.transactions_of(session, company.id, limit=30)
    tx_rows: list[dict[str, object]] = [
        {
            "id": t.id,
            "kind": t.kind,
            "amount": t.amount,
            "character_id": t.character_id,
            "at_total_seconds": t.at_total_seconds,
            "description": t.description,
        }
        for t in txs
    ]

    return templates.TemplateResponse(
        request,
        "economy_company_detail.html",
        {
            "company": company,
            "owner": owner,
            "reconcile": rec,
            "employees": employee_rows,
            "transactions": tx_rows,
        },
    )
