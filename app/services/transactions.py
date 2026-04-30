from datetime import date
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..utils.enums import DiscountType
from ..models import AdminTransaction, StudentTransaction, TeacherTransaction


async def create_student_transactions(
    session: AsyncSession,
    admin_id: int,
    student_id: int,
    group_id: int,
    teacher_id: int,
    from_when: date,
    until_when: date,
    student_discount: int,
    discount_type: DiscountType,
    center_share: Decimal,
    teacher_share: Decimal,
    amount: int,
) -> StudentTransaction:
    transaction = StudentTransaction(
        admin_id=admin_id,
        student_id=student_id,
        group_id=group_id,
        teacher_id=teacher_id,
        from_when=from_when,
        until_when=until_when,
        student_discount=student_discount,
        discount_type=discount_type,
        center_share=center_share,
        teacher_share=teacher_share,
        amount=amount,
    )
    session.add(transaction)
    await session.flush()

    return transaction
