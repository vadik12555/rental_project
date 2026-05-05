from __future__ import annotations

import os
from decimal import Decimal
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from catalog.models import Item


def _seed_items() -> tuple[int, int]:
    """
    Creates a small catalog of tools.

    - Idempotent: does not duplicate existing items (matches by title).
    - Optional images: if `media/seed/<slug>.(jpg|png|webp)` exists, attaches it.
    """

    items = [
        {
            "title": "Молоток",
            "description": "Надёжный стальной молоток для дома и стройки.",
            "price": Decimal("499.00"),
            "stock": 25,
            "image_slug": "molotok",
        },
        {
            "title": "Топор",
            "description": "Удобный топор для хозяйственных работ и походов.",
            "price": Decimal("1290.00"),
            "stock": 15,
            "image_slug": "topor",
        },
        {
            "title": "Шуруповёрт",
            "description": "Аккумуляторный шуруповёрт для сборки мебели и ремонта.",
            "price": Decimal("3490.00"),
            "stock": 12,
            "image_slug": "shurupovert",
        },
        {
            "title": "Пила",
            "description": "Ручная пила по дереву — ровный и быстрый распил.",
            "price": Decimal("890.00"),
            "stock": 20,
            "image_slug": "pila",
        },
        {
            "title": "Линейка",
            "description": "Металлическая линейка 30 см — точные замеры.",
            "price": Decimal("199.00"),
            "stock": 50,
            "image_slug": "lineyka",
        },
        {
            "title": "Рулетка",
            "description": "Рулетка 5 м с фиксатором — для стройки и дома.",
            "price": Decimal("350.00"),
            "stock": 30,
            "image_slug": "ruletka",
        },
        {
            "title": "Плоскогубцы",
            "description": "Плоскогубцы с прорезиненными рукоятками — удобный хват.",
            "price": Decimal("590.00"),
            "stock": 18,
            "image_slug": "ploskogubcy",
        },
        {
            "title": "Отвёртка",
            "description": "Отвёртка крестовая PH2 — базовый инструмент в наборе.",
            "price": Decimal("150.00"),
            "stock": 60,
            "image_slug": "otvertka",
        },
    ]

    base_dir = Path(__file__).resolve().parents[4]  # .../app
    seed_dir = base_dir / "media" / "seed"

    created = 0
    skipped = 0

    for data in items:
        title = data["title"]
        defaults = {
            "description": data["description"],
            "price": data["price"],
            "stock": data["stock"],
        }

        obj, was_created = Item.objects.get_or_create(title=title, defaults=defaults)
        if was_created:
            created += 1
        else:
            skipped += 1

        # Attach an image only when:
        # - we created the item (do not unexpectedly override user data)
        # - and image isn't already set
        if not was_created or obj.image:
            continue

        slug = data.get("image_slug")
        if not slug:
            continue

        for ext in ("jpg", "jpeg", "png", "webp"):
            candidate = seed_dir / f"{slug}.{ext}"
            if candidate.exists():
                with candidate.open("rb") as f:
                    obj.image.save(candidate.name, File(f), save=True)
                break

    return created, skipped


def _ensure_superuser() -> tuple[bool, str]:
    """
    Creates a superuser if it doesn't exist.

    Env vars (optional):
    - DJANGO_SUPERUSER_USERNAME (default: admin)
    - DJANGO_SUPERUSER_EMAIL (default: admin@example.com)
    - DJANGO_SUPERUSER_PASSWORD (default: admin12345)
    """

    User = get_user_model()

    username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin12345")

    user = User.objects.filter(username=username).first()
    if user:
        if not (user.is_staff and user.is_superuser):
            user.is_staff = True
            user.is_superuser = True
            if not user.email:
                user.email = email
            user.save(update_fields=["is_staff", "is_superuser", "email"])
        return False, username

    User.objects.create_superuser(username=username, email=email, password=password)
    return True, username


class Command(BaseCommand):
    help = "Seed initial catalog items and create a superuser (idempotent)."

    def handle(self, *args, **options):
        su_created, su_username = _ensure_superuser()
        items_created, items_skipped = _seed_items()

        self.stdout.write(self.style.SUCCESS("Seed completed."))
        self.stdout.write(
            f"Superuser: {'created' if su_created else 'exists'} (username={su_username})"
        )
        self.stdout.write(
            f"Items: created={items_created}, skipped={items_skipped} (matched by title)"
        )

