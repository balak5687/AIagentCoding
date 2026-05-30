"""Cost estimation service for job quotes."""

import logging
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator, field_serializer

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Constants
MAX_QUANTITY = 1000
MIN_MARGIN = Decimal("0")
MAX_MARGIN = Decimal("10")
MIN_VAT = Decimal("0")
MAX_VAT = Decimal("1")


class ServiceRepository:
    """
    Repository for service pricing data.

    WARNING: When replacing mock data with database queries,
    MUST use parameterized queries to prevent SQL injection.
    Example: cursor.execute("SELECT * FROM services WHERE id = %s", (service_id,))
    NEVER use string interpolation: f"SELECT * FROM services WHERE id = '{service_id}'"
    """

    def get_service_price(self, service_id: str) -> Optional[Decimal]:
        """Get base price for a service from service_master table."""
        # Mock data - replace with actual database query using parameterized statements
        mock_prices = {
            "OIL_CHANGE": Decimal("45.00"),
            "BRAKE_SERVICE": Decimal("120.00"),
            "TIRE_ROTATION": Decimal("25.00"),
            "ENGINE_DIAGNOSTIC": Decimal("95.00"),
        }
        return mock_prices.get(service_id)


class InventoryRepository:
    """
    Repository for parts inventory data.

    WARNING: When replacing mock data with database queries,
    MUST use parameterized queries to prevent SQL injection.
    Example: cursor.execute("SELECT * FROM inventory WHERE part_id = %s", (part_id,))
    NEVER use string interpolation: f"SELECT * FROM inventory WHERE part_id = '{part_id}'"
    """

    def get_part_info(self, part_id: str) -> Optional[Dict]:
        """Get part information including price and availability."""
        # Mock data - replace with actual database query using parameterized statements
        mock_parts = {
            "FILTER_OIL_001": {"price": Decimal("12.50"), "available": True},
            "BRAKE_PAD_FRONT": {"price": Decimal("65.00"), "available": True},
            "TIRE_ALLSEASON_185": {"price": Decimal("85.00"), "available": True},
        }
        return mock_parts.get(part_id)


class ServiceLineItem(BaseModel):
    """Line item for a service in the cost estimate."""

    service_id: str
    base_price: Decimal = Field(ge=0)
    margin_amount: Decimal = Field(ge=0)
    final_price: Decimal = Field(ge=0)

    @field_serializer('base_price', 'margin_amount', 'final_price')
    def serialize_decimal(self, value: Decimal) -> str:
        """Serialize Decimal fields to string to preserve precision."""
        return str(value)


class PartLineItem(BaseModel):
    """Line item for a part in the cost estimate."""

    part_id: str
    quantity: int = Field(gt=0, le=MAX_QUANTITY)
    unit_price: Decimal = Field(ge=0)
    margin_amount: Decimal = Field(ge=0)
    final_price: Decimal = Field(ge=0)

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        """Validate quantity is within reasonable bounds."""
        if v > MAX_QUANTITY:
            raise ValueError(f"Quantity exceeds maximum allowed: {MAX_QUANTITY}")
        return v

    @field_serializer('unit_price', 'margin_amount', 'final_price')
    def serialize_decimal(self, value: Decimal) -> str:
        """Serialize Decimal fields to string to preserve precision."""
        return str(value)


class CostEstimate(BaseModel):
    """Complete cost estimate with breakdown."""

    service_items: List[ServiceLineItem]
    part_items: List[PartLineItem]
    subtotal_labor: Decimal = Field(ge=0)
    subtotal_parts: Decimal = Field(ge=0)
    subtotal: Decimal = Field(ge=0)
    vat_amount: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)

    @field_serializer('subtotal_labor', 'subtotal_parts', 'subtotal', 'vat_amount', 'total')
    def serialize_decimal(self, value: Decimal) -> str:
        """Serialize Decimal fields to string to preserve precision."""
        return str(value)


def _apply_margin(base_price: Decimal, margin: Decimal) -> tuple[Decimal, Decimal]:
    """
    Apply margin to base price and return both margin amount and final price.

    Args:
        base_price: Base price before margin
        margin: Margin as decimal (e.g., 0.35 for 35%)

    Returns:
        Tuple of (margin_amount, final_price)
    """
    margin_amount = base_price * margin
    final_price = base_price + margin_amount
    return margin_amount, final_price


class CostEstimationService:
    """Service for calculating job cost estimates."""

    def __init__(
        self,
        labor_margin: Decimal = Decimal("0.35"),
        parts_margin: Decimal = Decimal("0.25"),
        vat_rate: Decimal = Decimal("0.20"),
        service_repo: Optional[ServiceRepository] = None,
        inventory_repo: Optional[InventoryRepository] = None
    ):
        """
        Initialize cost estimation service.

        Args:
            labor_margin: Markup on labor (default 35%)
            parts_margin: Markup on parts (default 25%)
            vat_rate: VAT rate (default 20%)
            service_repo: Optional service repository for testing
            inventory_repo: Optional inventory repository for testing

        Raises:
            ValueError: If margins or VAT rate are out of valid range
        """
        # Validate margins (0-10x or 0-1000%)
        if not (MIN_MARGIN <= labor_margin <= MAX_MARGIN):
            raise ValueError(f"labor_margin must be between {MIN_MARGIN} and {MAX_MARGIN}")
        if not (MIN_MARGIN <= parts_margin <= MAX_MARGIN):
            raise ValueError(f"parts_margin must be between {MIN_MARGIN} and {MAX_MARGIN}")

        # Validate VAT rate (0-100%)
        if not (MIN_VAT <= vat_rate <= MAX_VAT):
            raise ValueError(f"vat_rate must be between {MIN_VAT} and {MAX_VAT}")

        self.labor_margin = labor_margin
        self.parts_margin = parts_margin
        self.vat_rate = vat_rate

        # Initialize repositories
        self.service_repo = service_repo or ServiceRepository()
        self.inventory_repo = inventory_repo or InventoryRepository()

        logger.info(
            f"Initialized CostEstimationService: "
            f"labor_margin={labor_margin}, parts_margin={parts_margin}, vat_rate={vat_rate}"
        )

    def calculate_cost_estimate(
        self,
        services: List[str],
        parts: List[Dict[str, any]]
    ) -> CostEstimate:
        """
        Calculate cost estimate for services and parts.

        Args:
            services: List of service IDs
            parts: List of dicts with 'part_id' and 'quantity' keys

        Returns:
            CostEstimate with full breakdown

        Raises:
            ValueError: If both services and parts are empty, or if items not found
        """
        # Validate inputs
        if not services and not parts:
            raise ValueError("Cannot create estimate with no services and no parts")

        service_items = []
        subtotal_labor = Decimal("0")

        # Process services
        for service_id in services:
            base_price = self.service_repo.get_service_price(service_id)

            if base_price is None:
                raise ValueError(f"Service not found: {service_id}")

            # Apply labor margin
            margin_amount, final_price = _apply_margin(base_price, self.labor_margin)

            service_items.append(ServiceLineItem(
                service_id=service_id,
                base_price=base_price,
                margin_amount=margin_amount,
                final_price=final_price
            ))

            subtotal_labor += final_price

        part_items = []
        subtotal_parts = Decimal("0")

        # Process parts
        for part_spec in parts:
            part_id = part_spec.get("part_id")
            quantity = part_spec.get("quantity", 1)

            if not part_id:
                raise ValueError("Part specification missing 'part_id'")

            # Validate quantity
            if quantity <= 0:
                raise ValueError(f"Invalid quantity for part {part_id}: {quantity}")
            if quantity > MAX_QUANTITY:
                raise ValueError(f"Quantity exceeds maximum for part {part_id}: {quantity}")

            part_info = self.inventory_repo.get_part_info(part_id)

            if part_info is None:
                raise ValueError(f"Part not found: {part_id}")

            unit_price = part_info["price"]
            base_price = unit_price * quantity

            # Apply parts margin
            margin_amount, final_price = _apply_margin(base_price, self.parts_margin)

            part_items.append(PartLineItem(
                part_id=part_id,
                quantity=quantity,
                unit_price=unit_price,
                margin_amount=margin_amount,
                final_price=final_price
            ))

            subtotal_parts += final_price

        # Calculate totals
        subtotal = subtotal_labor + subtotal_parts
        vat_amount = subtotal * self.vat_rate
        total = subtotal + vat_amount

        estimate = CostEstimate(
            service_items=service_items,
            part_items=part_items,
            subtotal_labor=subtotal_labor,
            subtotal_parts=subtotal_parts,
            subtotal=subtotal,
            vat_amount=vat_amount,
            total=total
        )

        logger.info(
            f"Generated estimate: {len(service_items)} services, "
            f"{len(part_items)} parts, total={total}"
        )

        return estimate
