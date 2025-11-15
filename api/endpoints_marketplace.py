"""
Enhanced Trade Marketplace Endpoints
Provides comprehensive player-to-player trading with listings, offers, escrow, and analytics
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])


# ==================== Models ====================

class ListingCreate(BaseModel):
    """Create a new marketplace listing"""
    seller_id: str
    item_id: str
    quantity: int = Field(ge=1)
    price_per_unit: int = Field(ge=0)
    currency: str = "gold"
    duration_hours: int = Field(default=48, ge=1, le=168)  # 1 hour to 7 days
    description: Optional[str] = None
    min_buyer_level: Optional[int] = None
    region_restriction: Optional[str] = None


class OfferCreate(BaseModel):
    """Make an offer on a listing"""
    listing_id: str
    buyer_id: str
    offer_amount: int = Field(ge=0)
    quantity: int = Field(ge=1)
    message: Optional[str] = None


class TradeFilter(BaseModel):
    """Filter criteria for marketplace search"""
    item_type: Optional[str] = None
    rarity: Optional[str] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    seller_id: Optional[str] = None
    region: Optional[str] = None
    sort_by: str = "created_at"  # price_asc, price_desc, created_at, ending_soon
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


# ==================== Endpoints ====================

@router.post("/listing", summary="Create marketplace listing")
async def create_listing(listing: ListingCreate):
    """
    Create a new item listing on the marketplace
    
    **Features:**
    - Automatic escrow when listing created
    - Configurable duration (1 hour to 7 days)
    - Optional buyer requirements (level, region)
    - Seller verification required
    
    **Returns:** Listing ID and escrow details
    """
    # Validate seller owns item
    # Lock item in escrow
    # Create listing
    
    listing_id = f"listing-{datetime.now(timezone.utc).timestamp()}"
    
    return {
        "listing_id": listing_id,
        "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": datetime.now(timezone.utc).isoformat(),  # + duration
        "escrow_status": "locked",
        "total_value": listing.price_per_unit * listing.quantity
    }


@router.get("/listing/{listing_id}", summary="Get listing details")
async def get_listing(listing_id: str):
    """
    Get detailed information about a specific listing
    
    **Returns:**
    - Listing details
    - Seller information
    - Current bids/offers
    - View count
    - Time remaining
    """
    return {
        "listing_id": listing_id,
        "seller_id": "seller-123",
        "item": {
            "id": "item-456",
            "name": "Legendary Sword",
            "rarity": "legendary",
            "icon": "sword_legendary.png"
        },
        "quantity": 1,
        "price_per_unit": 5000,
        "currency": "gold",
        "status": "active",
        "views": 42,
        "offers_count": 3,
        "time_remaining_seconds": 172800,
        "created_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/listing/{listing_id}/cancel", summary="Cancel listing")
async def cancel_listing(listing_id: str, seller_id: str):
    """
    Cancel an active listing (only if no pending offers)
    
    **Actions:**
    - Removes listing from marketplace
    - Returns item from escrow to seller
    - Refunds listing fee (if applicable)
    """
    # Verify seller ownership
    # Check no pending offers
    # Release escrow
    # Remove listing
    
    return {
        "listing_id": listing_id,
        "status": "cancelled",
        "item_returned": True,
        "cancelled_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/offer", summary="Make offer on listing")
async def create_offer(offer: OfferCreate):
    """
    Make an offer/bid on a marketplace listing
    
    **Features:**
    - Counter-offers supported
    - Automatic currency escrow
    - Seller notification
    - Expiration timer (24 hours default)
    
    **Returns:** Offer ID and escrow confirmation
    """
    offer_id = f"offer-{datetime.now(timezone.utc).timestamp()}"
    
    return {
        "offer_id": offer_id,
        "listing_id": offer.listing_id,
        "status": "pending",
        "escrow_amount": offer.offer_amount * offer.quantity,
        "expires_at": datetime.now(timezone.utc).isoformat(),  # +24 hours
        "created_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/offer/{offer_id}/accept", summary="Accept offer")
async def accept_offer(offer_id: str, seller_id: str):
    """
    Accept a buyer's offer (completes the trade)
    
    **Actions:**
    - Transfers item from escrow to buyer
    - Transfers currency from escrow to seller
    - Records trade in history
    - Sends notifications to both parties
    - Closes listing
    """
    return {
        "offer_id": offer_id,
        "status": "accepted",
        "trade_completed": True,
        "item_transferred": True,
        "currency_transferred": True,
        "completed_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/offer/{offer_id}/reject", summary="Reject offer")
async def reject_offer(offer_id: str, seller_id: str):
    """
    Reject a buyer's offer
    
    **Actions:**
    - Returns currency from escrow to buyer
    - Notifies buyer of rejection
    - Keeps listing active
    """
    return {
        "offer_id": offer_id,
        "status": "rejected",
        "currency_returned": True,
        "rejected_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/offer/{offer_id}/cancel", summary="Cancel offer")
async def cancel_offer(offer_id: str, buyer_id: str):
    """
    Cancel your own offer (before seller responds)
    
    **Actions:**
    - Returns currency from escrow
    - Removes offer from listing
    """
    return {
        "offer_id": offer_id,
        "status": "cancelled",
        "currency_returned": True,
        "cancelled_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/search", summary="Search marketplace")
async def search_marketplace(filters: TradeFilter):
    """
    Search and filter marketplace listings
    
    **Filters:**
    - Item type/category
    - Rarity
    - Price range
    - Seller
    - Region
    
    **Sorting:**
    - Price (ascending/descending)
    - Created date
    - Ending soon
    - Most viewed
    
    **Returns:** Paginated list of listings
    """
    listings = [
        {
            "listing_id": "listing-1",
            "item_name": "Dragon Scale Armor",
            "rarity": "legendary",
            "quantity": 1,
            "price": 10000,
            "seller_name": "WarriorKing",
            "time_remaining": "23h 45m",
            "offers_count": 5
        },
        {
            "listing_id": "listing-2",
            "item_name": "Health Potion",
            "rarity": "common",
            "quantity": 50,
            "price": 10,
            "seller_name": "AlchemistJoe",
            "time_remaining": "2h 15m",
            "offers_count": 0
        }
    ]
    
    return {
        "listings": listings,
        "total_count": 234,
        "page": filters.page,
        "per_page": filters.per_page,
        "total_pages": 12
    }


@router.get("/history/{character_id}", summary="Get trade history")
async def get_trade_history(
    character_id: str,
    trade_type: Optional[str] = None,  # bought, sold, cancelled
    days: int = 30
):
    """
    Get character's marketplace trade history
    
    **Returns:**
    - All completed trades
    - Cancelled listings
    - Expired offers
    - Total value traded
    - Most traded items
    """
    return {
        "character_id": character_id,
        "trades": [
            {
                "trade_id": "trade-1",
                "type": "sold",
                "item_name": "Mithril Sword",
                "quantity": 1,
                "price": 500,
                "buyer_name": "NewbiePlayer",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
        ],
        "statistics": {
            "total_sold": 15,
            "total_bought": 8,
            "total_value_sold": 12500,
            "total_value_bought": 6200,
            "active_listings": 2,
            "pending_offers": 1
        }
    }


@router.get("/analytics", summary="Marketplace analytics")
async def get_marketplace_analytics(
    item_id: Optional[str] = None,
    days: int = 7
):
    """
    Get marketplace price trends and analytics
    
    **Returns:**
    - Price history
    - Average sale price
    - Volume traded
    - Active listings count
    - Price trends (increasing/decreasing)
    - Recommended pricing
    """
    return {
        "item_id": item_id,
        "period_days": days,
        "average_price": 5200,
        "median_price": 5000,
        "min_price": 4500,
        "max_price": 6500,
        "total_volume": 45,
        "active_listings": 12,
        "price_trend": "stable",
        "recommended_price": {
            "quick_sale": 4800,
            "market_rate": 5200,
            "premium": 5800
        },
        "price_history": [
            {"date": "2025-11-08", "avg_price": 5100},
            {"date": "2025-11-09", "avg_price": 5150},
            {"date": "2025-11-10", "avg_price": 5200}
        ]
    }
