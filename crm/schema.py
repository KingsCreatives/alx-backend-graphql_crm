import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .models import Customer, Product, Order

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# =====================================================
PHONE_RE = re.compile(r'^(\+?\d{7,15}|(\d{3}-\d{3}-\d{4}))$')


def validate_phone(phone):
    """Raise ValueError if phone provided and invalid."""
    if phone and not PHONE_RE.match(phone):
        raise ValueError("Invalid phone format. Use +1234567890 or 123-456-7890.")


def to_decimal(value):
    """Safely convert a float/str/int to Decimal or raise ValueError."""
    try:
        # Use str() to avoid float precision issues
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError(f"Invalid decimal value: {value}")


class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class BulkCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=False)


class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)  # client sends float; we'll convert safely
    stock = graphene.Int(required=False, default_value=0)


class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.NonNull(graphene.ID), required=True)
    order_date = graphene.DateTime(required=False)


class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            if Customer.objects.filter(email=input.email).exists():
                return CreateCustomer(customer=None, message="Failed to create customer.",
                                      errors=[f"Email '{input.email}' already exists."])
            validate_phone(input.phone)
            customer = Customer.objects.create(
                name=input.name.strip(),
                email=input.email.strip().lower(),
                phone=(input.phone.strip() if input.phone else None)
            )
            return CreateCustomer(customer=customer, message="Customer created successfully.", errors=[])
        except Exception as exc:
            return CreateCustomer(customer=None, message="Failed to create customer.", errors=[str(exc)])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(graphene.NonNull(BulkCustomerInput), required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        errors = []

        for idx, record in enumerate(input, start=1):
            try:
                name = (record.name or "").strip()
                email = (record.email or "").strip().lower()
                phone = (record.phone or None)
                if Customer.objects.filter(email=email).exists():
                    errors.append(f"Row {idx}: Email '{email}' already exists.")
                    continue
                validate_phone(phone)
                customer = Customer.objects.create(name=name, email=email, phone=phone)
                created_customers.append(customer)
            except Exception as exc:
                errors.append(f"Row {idx}: {str(exc)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            # Convert price to Decimal safely
            price = to_decimal(input.price)
            if price <= Decimal("0"):
                return CreateProduct(product=None, errors=["Price must be a positive number."])
            stock = input.stock if input.stock is not None else 0
            if stock < 0:
                return CreateProduct(product=None, errors=["Stock cannot be negative."])

            product = Product.objects.create(name=input.name.strip(), price=price, stock=stock)
            return CreateProduct(product=product, errors=[])
        except Exception as exc:
            return CreateProduct(product=None, errors=[str(exc)])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        try:
            # Validate customer
            try:
                customer = Customer.objects.get(id=input.customer_id)
            except Customer.DoesNotExist:
                return CreateOrder(order=None, errors=[f"Customer with id '{input.customer_id}' does not exist."])

            # Validate product IDs list
            product_ids = list(input.product_ids) if input.product_ids else []
            if not product_ids:
                return CreateOrder(order=None, errors=["At least one product must be provided."])

            # Fetch products
            products_qs = Product.objects.filter(id__in=product_ids)
            found_ids = {str(p.id) for p in products_qs}
            missing_ids = [pid for pid in product_ids if str(pid) not in found_ids]
            if missing_ids:
                return CreateOrder(order=None, errors=[f"Invalid product IDs: {missing_ids}"])

            # Compute total_amount using Decimal arithmetic
            total_amount = sum((p.price for p in products_qs), Decimal("0.00"))

            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount,
                order_date=input.order_date or timezone.now()
            )
            order.products.set(products_qs)
            order.save()

            return CreateOrder(order=order, errors=[])
        except Exception as exc:
            return CreateOrder(order=None, errors=[str(exc)])

class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(root, info):
        return Customer.objects.all()

    def resolve_all_products(root, info):
        return Product.objects.all()

    def resolve_all_orders(root, info):
        return Order.objects.select_related("customer").prefetch_related("products").all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
