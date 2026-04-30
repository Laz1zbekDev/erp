# from decimal import Decimal
# from datetime import time

# from sqlalchemy.orm import Mapped, mapped_column, relationship
# from sqlalchemy import String, Integer, Enum, Numeric, SmallInteger, ForeignKey, TIME

# from ..db.base import Base, TimeMixin


# class Science(Base, TimeMixin):
#     __tablename__ = "sciences"

#     science_id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

#     groups: Mapped["Group"] = relationship("Group", back_populates="science")
