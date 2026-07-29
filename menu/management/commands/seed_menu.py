from decimal import Decimal
from pathlib import Path

from django.apps import apps
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db import transaction

from menu.models import Category, FoodItem


CATEGORIES = (
    ("Drinks", "drinks"),
    ("Pizza", "pizza"),
    ("Burger", "burger"),
    ("Biryani", "biryani"),
    ("Fried Chicken", "fried-chicken"),
    ("Snacks", "snacks"),
    ("Sandwich", "sandwich"),
    ("Juice", "juice"),
    ("Special Offer", "special-offer"),
)

MENU_ITEMS = (
    {
        "title": "Beef Burger",
        "description": "A juicy beef patty served in a fresh bun.",
        "price": "200.00",
        "image": "beefburger.jpg",
        "categories": ("burger",),
    },
    {
        "title": "Beef Pizza",
        "description": "Pizza topped with seasoned beef and melted cheese.",
        "price": "1000.00",
        "image": "beefpizza.jpg",
        "categories": ("pizza",),
    },
    {
        "title": "Biryani",
        "description": "Aromatic basmati rice layered with tender spiced meat.",
        "price": "500.00",
        "image": "biryani.jpg",
        "categories": ("biryani",),
    },
    {
        "title": "Kacchi",
        "description": "Traditional kacchi biryani slow-cooked with meat and rice.",
        "price": "450.00",
        "image": "biryani2.jpg",
        "categories": ("biryani",),
    },
    {
        "title": "Chicken Pizza",
        "description": "Pizza with seasoned chicken, vegetables, and cheese.",
        "price": "700.00",
        "image": "chickenpizza.jpg",
        "categories": ("pizza",),
    },
    {
        "title": "Chicken Burger",
        "description": "Seasoned chicken served in a bun with fresh toppings.",
        "price": "340.00",
        "image": "cknburger.jpg",
        "categories": ("burger",),
    },
    {
        "title": "Cola",
        "description": "Chilled carbonated cola.",
        "price": "100.00",
        "image": "cola.jpg",
        "categories": ("drinks",),
    },
    {
        "title": "Cold Coffee",
        "description": "Chilled coffee blended for a smooth, refreshing drink.",
        "price": "70.00",
        "image": "coldcoffee.jpg",
        "categories": ("drinks",),
    },
    {
        "title": "Egg Pizza",
        "description": "Fresh pizza topped with egg, vegetables, and cheese.",
        "price": "500.00",
        "image": "eggpizza.jpg",
        "categories": ("pizza",),
    },
    {
        "title": "Fried Rice",
        "description": "Stir-fried rice with egg, vegetables, and seasoning.",
        "price": "300.00",
        "image": "friedrice.jpg",
        "categories": ("biryani",),
    },
    {
        "title": "Fries",
        "description": "Golden, crispy potato fries.",
        "price": "150.00",
        "image": "fries.jpg",
        "categories": ("snacks",),
    },
    {
        "title": "Noodles",
        "description": "Stir-fried noodles with vegetables and savory seasoning.",
        "price": "250.00",
        "image": "noodles.jpg",
        "categories": ("snacks",),
    },
    {
        "title": "Pasta",
        "description": "Tender pasta tossed in a rich savory sauce.",
        "price": "350.00",
        "image": "pasta.jpg",
        "categories": ("snacks",),
    },
    {
        "title": "Slush",
        "description": "An icy flavored drink served chilled.",
        "price": "200.00",
        "image": "slush.jpg",
        "categories": ("drinks",),
    },
    {
        "title": "Chicken Wings",
        "description": "Crispy chicken wings seasoned and cooked until golden.",
        "price": "300.00",
        "discount_price": "250.00",
        "image": "chickenwings.jpg",
        "categories": ("fried-chicken", "special-offer"),
    },
    {
        "title": "Fried Chicken",
        "description": "Juicy chicken in a crisp, seasoned coating.",
        "price": "350.00",
        "image": "friedchicken.jpg",
        "categories": ("fried-chicken",),
    },
    {
        "title": "Sandwich",
        "description": "A fresh sandwich filled with vegetables, cheese, and meat.",
        "price": "250.00",
        "discount_price": "200.00",
        "image": "sandwich.jpg",
        "categories": ("sandwich", "special-offer"),
    },
    {
        "title": "Shawarma",
        "description": "Slow-roasted seasoned meat wrapped with fresh toppings.",
        "price": "250.00",
        "discount_price": "180.00",
        "image": "shawarma.jpg",
        "categories": ("special-offer",),
    },
    {
        "title": "Lemon Mint",
        "description": "Fresh lemon juice blended with cooling mint.",
        "price": "150.00",
        "discount_price": "120.00",
        "image": "lemonmint.jpg",
        "categories": ("juice", "special-offer"),
    },
    {
        "title": "Mango Juice",
        "description": "A refreshing juice made with ripe mango.",
        "price": "180.00",
        "image": "mango.jpg",
        "categories": ("juice",),
    },
)


class Command(BaseCommand):
    help = "Create the non-sensitive starter categories and menu items."

    def add_arguments(self, parser):
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update matching menu items as well as creating missing ones.",
        )
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Do not copy packaged starter images into media storage.",
        )
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Seed only when no menu items exist yet.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["if_empty"] and FoodItem.objects.exists():
            self.stdout.write("Menu seed skipped: menu items already exist.")
            return

        categories = {}
        for name, slug in CATEGORIES:
            category, _ = Category.objects.update_or_create(
                slug=slug,
                defaults={"name": name},
            )
            categories[slug] = category

        created_count = 0
        updated_count = 0
        unchanged_count = 0
        image_source_dir = Path(apps.get_app_config("menu").path) / "images"

        for seed in MENU_ITEMS:
            item = FoodItem.objects.filter(title=seed["title"]).order_by("pk").first()
            created = item is None
            should_update = created or options["update_existing"]
            defaults = {
                "description": seed["description"],
                "price": Decimal(seed["price"]),
                "discount_price": (
                    Decimal(seed["discount_price"])
                    if seed.get("discount_price")
                    else None
                ),
                "active": False,
                "start_date": None,
                "end_date": None,
                "is_available": True,
            }

            if created:
                item = FoodItem.objects.create(title=seed["title"], **defaults)
                created_count += 1
            elif should_update:
                for field, value in defaults.items():
                    setattr(item, field, value)
                item.full_clean(exclude=("image",))
                item.save(update_fields=tuple(defaults))
                updated_count += 1
            else:
                unchanged_count += 1

            if should_update:
                item.category.set(categories[slug] for slug in seed["categories"])

            if not options["skip_images"]:
                self._attach_image(
                    item,
                    image_source_dir / seed["image"],
                    update_reference=should_update or not item.image,
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Menu seed complete: "
                f"{created_count} created, {updated_count} updated, "
                f"{unchanged_count} unchanged."
            )
        )

    def _attach_image(self, item, source_path, update_reference):
        if item.image and not update_reference:
            existing_source = source_path.parent / Path(item.image.name).name
            if existing_source.exists():
                source_path = existing_source

        if not source_path.exists():
            self.stderr.write(self.style.WARNING(f"Missing seed image: {source_path}"))
            return

        destination = (
            f"menu/images/{source_path.name}"
            if update_reference or not item.image
            else item.image.name
        )
        if not default_storage.exists(destination):
            with source_path.open("rb") as image_file:
                default_storage.save(destination, File(image_file))
        if update_reference and item.image.name != destination:
            item.image.name = destination
            item.save(update_fields=("image",))
