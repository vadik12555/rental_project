from .cart import Cart


def cart_count(request):
    """
    Provide cart item count for navbar.
    """
    return {"cart_count": len(Cart(request))}

